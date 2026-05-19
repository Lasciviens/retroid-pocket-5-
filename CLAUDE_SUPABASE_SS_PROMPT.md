# Claude Prompt — Supabase ScreenScraper Migration

Copy this whole prompt into Claude when assigning the Supabase/database part.

---

You are working in the GitHub repo `Lasciviens/retroid-pocket-5-`.

Read these files first, in this order:

1. `AI_RULES.md`
2. `CURRENT_STATE.md`
3. `project_todo.md`
4. `ARCHITECTURE.md`
5. `SCREENSCRAPER_MIGRATION_PLAN.md`

Your task is the Supabase/backend part of the ScreenScraper migration. Do not work on frontend HTML except for documentation references.

## Goal

Make ScreenScraper the primary metadata source while keeping IGDB as a temporary fallback. Do not drop IGDB columns yet.

The site currently uses:

- `v_games_summary` for the Library grid/list/table.
- `v_games_full` for modal details.
- IGDB columns on `games` and `game_platforms`.
- `retroachievements-player` Edge Function already deployed.
- temporary `ss-test` Edge Function deployed for earlier testing.

## Critical Security Rule

ScreenScraper media URLs may include developer credentials or secret-bearing query params.

Therefore:

- You may store full raw ScreenScraper response in private JSONB columns.
- You must not expose raw ScreenScraper media URLs in public views.
- Frontend-safe `ss_*_url` columns must contain only Supabase Storage URLs or another public-safe/proxy-safe URL.
- If a media URL is not public-safe yet, leave the public URL column null and store the source only in `ss_media_json` / `ss_raw_json`.

## Work Package 1 — migration_v16

Create a new migration file only:

```txt
migrations/migration_v16.sql
```

Do not edit old migration files.

Add columns with `IF NOT EXISTS`.

### `systems`

Add:

- `ss_system_id integer`
- `ss_name text`

Then seed the known mapping:

```txt
DB system_id -> SS system_id
1 PS1 -> 57
2 PS2 -> 58
3 PSP -> 61
4 GBA -> 24
5 DS -> 78
6 3DS -> 17
7 N64 -> 14
8 GameCube -> 13
9 Wii -> 16
10 SNES -> 4
11 NES -> 3
12 Genesis -> 1
13 Dreamcast -> 23
16 GBC -> 29
```

Use IDs only if they match live DB. Verify before update. If live IDs differ, update by `systems.name`.

### `games`

Add:

- `ss_game_id bigint`
- `ss_title text`
- `ss_description text`
- `ss_rating numeric`
- `ss_players text`
- `ss_box_url text`
- `ss_wheel_url text`
- `ss_video_url text`
- `ss_screenshot_url text`
- `ss_fanart_url text`
- `ss_raw_json jsonb`
- `ss_media_json jsonb`
- `ss_match_method text`
- `ss_match_confidence integer`
- `ss_needs_review boolean default false`
- `ss_synced_at timestamptz`

Add reasonable checks:

- `ss_rating` between 0 and 100 if not null.
- `ss_match_confidence` between 0 and 100 if not null.

Do not change `games.rating`.

### `game_platforms`

Add:

- `developer text`
- `ss_rom_id bigint`
- `ss_release_date date`
- `ss_rom_regions text[] default '{}'::text[]`
- `ss_rom_languages text[] default '{}'::text[]`
- `ss_variant_flags jsonb`
- `ss_rom_json jsonb`
- `ra_supported boolean default false`
- `ra_last_checked_at timestamptz`

### Indexes

Add indexes where useful:

- `games(ss_game_id)`
- `games(ss_synced_at)`
- `games(ss_needs_review)`
- `game_platforms(ss_rom_id)`
- `game_platforms(ra_supported)`
- `systems(ss_system_id)`

## Work Package 2 — Update Views

Update `v_games_summary` and `v_games_full`.

Requirements:

- Keep backward compatibility with existing frontend fields.
- Add provider-neutral fields:
  - `metadata_provider`
  - `metadata_rating`
  - `metadata_synced_at`
  - `metadata_match_confidence`
  - `display_cover_url`
- `metadata_provider` should be:
  - `screenscraper` if `ss_game_id is not null`
  - `igdb` if no SS match but `external_id is not null`
  - `manual` otherwise
- `metadata_rating` should prefer `ss_rating`, then `igdb_rating`, then null.
- `display_cover_url` should prefer safe `ss_box_url`, then `primary_cover_url`, then existing platform cover.
- Include `ss_wheel_url`, `ss_video_url`, `ss_screenshot_url`, `ss_fanart_url` if they are public-safe columns.
- Include `platforms[].developer`, `platforms[].ra_supported`, `platforms[].ss_release_date`.
- Do not expose raw JSON fields in public views.

Update audit views:

- Do not mark a game as missing metadata if it has `ss_game_id`.
- Prefer provider-neutral issue names where possible.
- Keep old IGDB labels if needed for compatibility, but add SS-aware alternatives.

## Work Package 3 — Storage and Function Plan

Prepare `supabase/functions/ss-enricher/index.ts`.

Function modes:

- `dry_run`
- `single`
- `batch`
- `refresh_media`

Secrets expected:

- `SS_DEVID`
- `SS_DEVPASSWORD`
- `SS_DEBUGPASSWORD` if needed by the account setup
- ScreenScraper username/password secret names already in Supabase
- `SUPABASE_URL`
- service role key if needed for DB/storage writes

Do not hardcode secrets.

Function behavior:

1. Resolve platform via `systems.ss_system_id`.
2. If ROM hash/size exists, use hash-first `jeuInfos`.
3. Otherwise use `jeuRecherche` with title and system ID.
4. Score candidates.
5. Fetch full `jeuInfos` by `gameid`.
6. Parse into DB payload.
7. Copy `box-2D` and `wheel-hd` to Supabase Storage.
8. Save only public-safe Storage URLs into `games.ss_box_url` and `games.ss_wheel_url`.
9. Store raw response in `ss_raw_json`.
10. Store selected/private media source data in `ss_media_json`.
11. Set `ss_needs_review` for low confidence.

Recommended confidence:

- 100 hash match
- 90 exact title + platform + year
- 80 exact title + platform
- 65 fuzzy title + platform
- 50 ambiguous candidates
- 40 notgame/hack/clone

## Work Package 4 — Verification

Run or prepare tests for:

- God of War II / PS2
- Mario Kart: Double Dash!! / GameCube
- Sonic the Hedgehog 2 / Genesis
- Chrono Trigger / SNES
- one multi-platform duplicate candidate
- one obscure/missing media case

Verify:

- `v_games_summary` still loads old rows.
- SS fields appear when populated.
- IGDB fields remain as fallback.
- Raw SS JSON is not exposed in public views.
- No credential-bearing ScreenScraper URL appears in `v_games_summary` or `v_games_full`.
- `ra_supported` can be read per platform.

## Deliverables

Commit with prefix:

```txt
ajan: claude — feat: add screenscraper supabase foundation
```

Update:

- `CURRENT_STATE.md`
- `project_todo.md`
- `supabase/functions/README.md`
- `ARCHITECTURE.md` if schema text changes

Do not change:

- `Retroid_Library_Dashboard.html`
- `rp5_igdb.js`
- existing migration files

## Final Message Expected

Report:

- migration file created
- views updated
- Edge Function status
- tests run
- any manual decisions needed
- whether Codex can start the web/UI phase
