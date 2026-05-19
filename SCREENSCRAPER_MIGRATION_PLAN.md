# ScreenScraper Migration Plan

> Goal: make ScreenScraper the primary metadata source, retire IGDB gradually, and keep the live Library stable while the database and UI change underneath.
> Created: 2026-05-19 by Codex.

## Short Decision

ScreenScraper should become the canonical metadata provider for this project.

Reasoning:

- This is a retro handheld library, not a general modern games catalog.
- ScreenScraper knows ROM/platform context, regional titles, box art, wheel art, screenshots, videos, fanart, manuals, and ROM-level flags.
- IGDB is already wired deeply into the app, so the safe path is not removal first. The safe path is compatibility first, SS-first reads second, IGDB decommission last.

## Current Starting Point

Known state from `CURRENT_STATE.md` and live Supabase inspection:

- Current DB baseline is `migration_v15`.
- Library grid reads `v_games_summary`.
- Detail modal reads `v_games_full`.
- IGDB fields exist at both `games` and `game_platforms` levels.
- `retroachievements-player` Edge Function is active.
- `ss-test` Edge Function exists as a temporary test tool.
- ScreenScraper test succeeded for God of War II on PS2 with exact match and media.
- Linear project exists, but GitHub remains the source of durable engineering context.

## Core Model

Keep the existing canonical-game plus platform-variant model:

- `games` = one visible library item.
- `game_platforms` = system/platform variant rows.
- ScreenScraper game metadata can live mostly on `games`.
- ScreenScraper ROM/platform metadata should live on `game_platforms`.

This preserves the current duplicate/platform strategy and avoids creating duplicate game cards during enrichment.

## Self-Review Questions

### Should IGDB be dropped now?

No. IGDB is currently used by views, sort options, badges, bridge UI, audit views, and scripts. Dropping columns before SS data is populated would break the site and remove fallback data.

Decision: freeze IGDB as legacy/fallback, add SS in parallel, switch display logic, then remove IGDB later.

### Should ScreenScraper media URLs be stored directly?

Not in public views. ScreenScraper returned media URLs may contain developer credentials or session-bearing query params. The database may keep the raw response in private JSONB for audit/debug, but frontend-facing columns must be sanitized.

Decision:

- Store raw/source URL only in `ss_raw_json` / `ss_media_json`, not exposed through public views.
- Copy box/wheel to Supabase Storage before exposing them.
- For video/screenshot/fanart, either copy to Storage or serve via an authenticated/proxy Edge Function. Until that exists, UI should show a placeholder/fallback.

### Where should SS rating live?

Authoritative `ss_rating` should live on `game_platforms`, because ScreenScraper matches are platform/system specific. `v_games_summary.metadata_rating` should derive from the selected primary/preferred platform's `ss_rating`, then fall back to `games.igdb_rating`. Do not overwrite `games.rating`, because that is the user's personal/library rating.

### What should the UI read first?

The UI should prefer SS fields when present:

1. `display_cover_url`, derived from the selected platform's safe `ss_box_url`, over `primary_cover_url`.
2. `ss_wheel_url`, derived from the selected platform's safe wheel asset, for card/detail logo art.
3. `metadata_rating`, derived from the selected platform's `ss_rating` then IGDB fallback, for external/community rating display.
4. Existing `description` remains the display text. SS synopsis may fill it only when empty; otherwise the raw synopsis stays in `ss_raw_json`.
5. IGDB stays visible only as legacy/fallback during the transition.

### What can go wrong?

- Wrong regional match from name-only search.
- Credential-bearing media URLs leaking through public views.
- Existing IGDB audit flags continuing to mark SS-enriched games as incomplete.
- Duplicate/platform UI opening the wrong platform variant.
- Storage copying becoming expensive or slow if video is copied too early.
- Batch work exceeding ScreenScraper daily request/download limits if quota telemetry is ignored.

## Phase 0: Freeze and Safety

Owner: user + Claude.

Tasks:

- Revoke exposed GitHub/Linear tokens and rotate any leaked keys.
- Ensure ScreenScraper secrets are only in Supabase secrets.
- Decide whether `ss-test` should be removed or locked behind JWT/auth after `ss-enricher` exists.
- Do not deploy new IGDB enrichment workflows except bug fixes.
- Keep IGDB columns intact.

Acceptance:

- No secret values are present in repo files.
- `ss-test` is either documented as temporary or removed.
- `CURRENT_STATE.md` says IGDB is legacy/fallback, not the target provider.

## Phase 1: Supabase Compatibility Layer

Owner: Claude.

Create `migrations/migration_v16.sql`.

Minimum DB additions:

### `systems`

- `ss_system_id integer`
- `ss_name text`

### `games`

- `ss_title text`
- `ss_players text`
- `ss_video_url text`
- `ss_screenshot_url text`
- `ss_fanart_url text`
- `ss_raw_json jsonb`
- `ss_media_json jsonb`
- `ss_synced_at timestamptz`

Important: `games.ss_video_url`, `games.ss_screenshot_url`, and `games.ss_fanart_url` must be public-safe URLs only. If the only URL available contains ScreenScraper credentials, keep it in private JSON and leave the public URL null.

### `game_platforms`

- `ss_game_id bigint`
- `ss_title text`
- `ss_rating numeric`
- `developer text`
- `ss_rom_id bigint`
- `ss_box_url text`
- `ss_wheel_url text`
- `ss_release_date date`
- `ss_rom_regions text[]`
- `ss_rom_languages text[]`
- `ss_variant_flags jsonb`
- `ss_rom_json jsonb`
- `ss_match_method text`
- `ss_match_confidence integer`
- `ss_needs_review boolean default false`
- `ra_supported boolean default false`
- `ra_last_checked_at timestamptz`

Important: `game_platforms.ss_box_url` and `game_platforms.ss_wheel_url` must contain only Supabase Storage or proxy-safe public URLs. Raw ScreenScraper URLs stay in JSONB only.

### Views

Update `v_games_summary`:

- Include SS-safe display fields derived from the selected primary/preferred platform:
  - `primary_ss_game_id`
  - `ss_rating`
  - `ss_box_url`
  - `ss_wheel_url`
  - `ss_video_url`
  - `ss_screenshot_url`
  - `ss_fanart_url`
  - `metadata_provider`
  - `metadata_rating`
  - `metadata_match_confidence`
  - `ra_supported`
- Keep existing IGDB aliases during transition.
- Platform JSON should include `ss_game_id`, `ss_rating`, `ss_box_url`, `ss_wheel_url`, `developer`, `ra_supported`, and other public-safe SS fields only.
- `ra_supported` should be a top-level aggregate on `v_games_summary`, preferably `BOOL_OR(game_platforms.ra_supported)`.
- A physical `games.ra_supported` column is not required for the first migration unless indexing becomes necessary; the frontend can filter the top-level view aggregate.

Update `v_games_full`:

- Include all detail-safe SS fields.
- Do not expose `ss_raw_json`, `ss_media_json`, `ss_rom_json`, raw hashes, or credential-bearing URLs to public clients.

Update audit views:

- A game with any platform-level `ss_game_id` should not be flagged as `no_external_id` just because IGDB is missing.
- Replace IGDB-specific labels with provider-neutral labels where practical:
  - `no_external_id` -> `no_metadata_match`
  - `no_igdb_rating` -> `no_external_rating`
  - `never_synced` -> `metadata_never_synced`

Acceptance:

- Existing Library still loads before any SS enrichment.
- Existing IGDB data still displays.
- Views can support SS-first UI without another migration.
- Raw SS JSON is not exposed through public views.

## Phase 2: `ss-enricher` Edge Function

Owner: Claude, reviewed by Codex for UI contract.

Create `supabase/functions/ss-enricher/index.ts`.

Modes:

- `dry_run`: fetch and parse, write nothing.
- `single`: enrich one game/platform.
- `batch`: enrich N records with rate limiting.
- `refresh_media`: reselect/copy media without changing metadata.

Inputs:

- `game_id`
- `game_platform_id`
- `limit`
- `rom_status`
- `dry_run`
- optional `force`

Match order:

1. If ROM hashes/size exist, call `jeuInfos.php` hash-first.
2. Else call `jeuRecherche.php` with title + `systemeid`.
3. Score candidates.
4. Fetch full data with `jeuInfos.php?gameid=...`.
5. If score is below threshold or candidates are ambiguous, set `ss_needs_review = true`.

Recommended confidence:

- 100: hash match.
- 90: exact title + exact platform + matching year.
- 80: exact title + platform, year absent.
- 65: fuzzy title + platform.
- 50: multiple close candidates.
- 40: notgame/hack/clone signals.

Media policy:

- Copy box-2D and wheel-hd to Storage immediately.
- Do not expose raw SS media URLs in views.
- Storage paths should include both game and platform IDs, for example `games/{game_id}/platforms/{platform_id}/ss/box-2d.png`.
- Screenshot/fanart/video can be phase 2.5:
  - either copy to Storage,
  - or implement an auth/proxy endpoint,
  - or leave null so UI shows placeholder.

Acceptance:

- `dry_run` returns parsed payload and candidate reasoning.
- `single` can enrich God of War II and Mario Kart: Double Dash!! without breaking existing rows.
- Batch mode can run with `limit=10` and produce a summary.
- No secret-bearing URL appears in `v_games_summary` or `v_games_full`.

## Phase 3: Codex Web Work

Owner: Codex.

The web changes are sequenced after Claude lands `migration_v16` and the updated views. Codex can prepare defensive helpers earlier, but wheel/video/provider UI should wait for the view contract.

Tasks:

- Rename IGDB-facing labels in the Library to provider-neutral language:
  - `IGDB Eksik` -> `Metadata Eksik`
  - `IGDB Rating` -> `Metadata Rating`
  - `IGDB` badges -> `SS` when `metadata_provider = 'screenscraper'`, otherwise `IGDB`.
- Change default sort from IGDB rating to provider-neutral metadata rating.
- Add wheel art support:
  - card overlay when `ss_wheel_url` exists,
  - fallback to text title when missing.
- Add video placeholder/player:
  - render only if `ss_video_url` is public-safe,
  - otherwise show screenshot/fanart/box fallback.
- Add duplicate/platform view mode:
  - default = one card per `games.id`,
  - show-all = one card per platform variant,
  - modal identity must carry both `game_id` and optional `platform_id`.
- Add RA support badge from `platforms[].ra_supported`.
- Keep IGDB Bridge page reachable during transition, but mark it legacy once SS enricher is live.

Acceptance:

- Library loads with old views and new views.
- No UI calls ScreenScraper directly.
- Modal works for a multi-platform game and opens the intended platform.
- Missing SS media degrades gracefully.

## Phase 4: Pilot Enrichment

Owner: Claude + user review.

Pilot set:

- God of War II / PS2
- Mario Kart: Double Dash!! / GameCube
- Sonic the Hedgehog 2 / Genesis
- Chrono Trigger / SNES
- Resident Evil 2 multi-platform candidate
- A known missing/obscure game

Acceptance:

- At least 90% correct automatic matches in pilot.
- All low-confidence rows are marked review-required.
- Storage assets display in Library.
- Audit score does not regress.

## Phase 5: Batch Rollout

Owner: Claude.

Order:

1. `installed`
2. `sd_card`
3. `found`
4. `missing`
5. wishlist/backlog-only entries

Batch rules:

- Run small batches first: 10, 25, 50.
- Read `ssuser.requeststoday`, `ssuser.maxrequestsperday`, download counters, and server load fields from every response.
- Stop before quota exhaustion; default safety margin should be at least 10% of the daily request limit.
- Store batch summary with calls attempted, calls succeeded, media copied, review-required count, and next resume cursor.
- Stop on quota/rate errors.
- Store summary logs.
- Do not overwrite curated user fields unless empty.

Acceptance:

- 321 games processed or explicitly skipped.
- Review queue is manageable.
- UI shows SS metadata for most games.

## Phase 6: IGDB Retirement

Owner: Claude + Codex.

Only start after SS coverage is high and UI is SS-first.

Steps:

1. Stop IGDB scheduled workflows.
2. Hide IGDB Bridge from main navigation or mark legacy.
3. Confirm views no longer require IGDB fields.
4. Archive IGDB scripts/functions.
5. Create a later migration to drop IGDB columns only after a backup/export.

Do not drop IGDB columns in `migration_v16`.

## Web Contract for Codex

Codex should expect these provider-neutral fields from `v_games_summary`:

```txt
metadata_provider
metadata_rating
metadata_match_confidence
metadata_synced_at
display_cover_url
primary_ss_game_id
ss_box_url
ss_wheel_url
ss_video_url
ss_screenshot_url
ss_fanart_url
ra_supported
platforms[].ra_supported
platforms[].developer
```

`display_cover_url` should be computed by DB/view as:

1. safe selected-platform `ss_box_url`
2. existing `primary_cover_url`
3. primary platform `cover_url`
4. null

## Files to Update

Claude:

- `migrations/migration_v16.sql`
- `supabase/functions/ss-enricher/index.ts`
- `supabase/functions/README.md`
- `CURRENT_STATE.md`
- `project_todo.md`

Codex:

- `Retroid_Library_Dashboard.html`
- possible `rp5_ss.js` helper
- `index.html` navigation labels
- `CURRENT_STATE.md`
- `project_todo.md`

Shared:

- `ARCHITECTURE.md`
- `AI_RULES.md`

## Do Not Do

- Do not expose ScreenScraper credentials in HTML, JS, public view columns, or GitHub files.
- Do not drop IGDB columns in the same migration that adds SS columns.
- Do not overwrite `games.rating`.
- Do not overwrite curated descriptions/logs unless fields are empty or user approved.
- Do not make the frontend call ScreenScraper directly.
- Do not store credential-bearing media URLs in public-facing columns.

## References

- ScreenScraper API v2: https://www.screenscraper.fr/webapi2.php
- Current state: `CURRENT_STATE.md`
- Backlog: `project_todo.md`
- Detailed Claude prompt: `CLAUDE_SUPABASE_SS_PROMPT.md`
