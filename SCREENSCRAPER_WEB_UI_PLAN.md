# ScreenScraper Web UI Plan

> Owner: Codex.
> Created: 2026-05-19.
> Status: ready to execute after Claude lands `migration_v16` + updated views.

## Goal

Move the website from IGDB-specific UI to provider-neutral metadata UI, then let ScreenScraper become the primary provider without breaking the current Library.

The frontend must not call ScreenScraper directly. It reads only:

- Supabase REST views
- Supabase Storage public URLs
- future auth/proxy-safe URLs

Raw ScreenScraper source URLs must never appear in HTML or browser JS.

## Current UI Surface

Primary file:

- `Retroid_Library_Dashboard.html`

Secondary files:

- `Retroid_Cleanup_Workspace.html`
- `index.html`
- `Retroid_Queue.html`
- `Retroid_Tierlist.html`
- `Retroid_Series_Roadmap.html`

Legacy/fallback files:

- `Retroid_IGDB_Bridge.html`
- `rp5_igdb.js`

## DB/View Contract Needed First

Codex should wait for Claude to expose these fields before coding the real UI switch:

### `v_games_summary`

```txt
id
title
release_year
publisher
play_status
tier
rating
metadata_provider
metadata_rating
metadata_synced_at
metadata_match_confidence
display_cover_url
primary_ss_game_id
ss_box_url
ss_wheel_url
ss_video_url
ss_screenshot_url
ss_fanart_url
ss_needs_review
ra_supported
series_id
series_name
genres
platforms
```

### `v_games_full`

Everything above plus:

```txt
ss_title
ss_players
storyline or existing description fallback
screenshots / safe media arrays
platforms[].ss_game_id
platforms[].ss_rating
platforms[].ss_box_url
platforms[].ss_wheel_url
platforms[].developer
platforms[].ra_supported
platforms[].ss_release_date
platforms[].ss_rom_regions
platforms[].ss_rom_languages
```

### Compatibility Rule

Every frontend helper must tolerate missing SS fields. The current site must still work against `migration_v15`.

## Implementation Order

### Step 1: Data Normalization Helpers

File: `Retroid_Library_Dashboard.html`

Add provider-neutral helpers before rendering:

- `getMetadataProvider(game)`
- `getMetadataRating(game)`
- `getMetadataLabel(game)`
- `getMetadataBadgeClass(game)`
- `getDisplayCover(game)`
- `getWheelArt(game)`
- `getSafeVideoUrl(game)`
- `getSafeScreenshotUrl(game)`
- `hasMetadataMatch(game)`

Fallback logic:

```txt
provider = metadata_provider || (primarySsGameId ? 'screenscraper' : externalId ? 'igdb' : 'manual')
rating = metadata_rating || primary platform ssRating || igdbRating || null
cover = display_cover_url || primary platform ssBoxUrl || primary_cover_url || primary platform cover || null
wheel = ss_wheel_url || primary platform ssWheelUrl || null
video = ss_video_url only if public-safe
screenshot = ss_screenshot_url only if public-safe
```

Do not use raw SS JSON or private media source URLs.

### Step 2: Library Query Expansion

File: `Retroid_Library_Dashboard.html`

Update summary query from IGDB-specific fields to provider-neutral fields.

Current query contains:

```txt
igdb_rating_canonical
external_id
primary_cover_url
```

New query should include both old and new fields:

```txt
metadata_provider
metadata_rating
metadata_match_confidence
display_cover_url
primary_ss_game_id
ss_rating
ss_box_url
ss_wheel_url
ss_video_url
ss_screenshot_url
ss_fanart_url
ss_needs_review
igdb_rating_canonical
external_id
primary_cover_url
```

The mapper should set both legacy and new properties:

```txt
game.metadataProvider
game.metadataRating
game.metadataConfidence
game.primarySsGameId
game.ssRating
game.ssBoxUrl
game.ssWheelUrl
game.ssVideoUrl
game.ssScreenshotUrl
game.ssFanartUrl
game.needsMetadataReview
```

### Step 3: Rename Filters and Stats

File: `Retroid_Library_Dashboard.html`

Change visible labels:

- `IGDB Eksik` -> `Metadata Eksik`
- `IGDB Rating` -> `Metadata Rating`
- `IGDB Eksik` filter state -> `metadataMissing`
- `s-unmatched` meaning -> no metadata provider match

Keep internal legacy values only where backward compatibility is easier.

Default sort:

- Before: `igdb-rating`
- After: `metadata-rating`
- Fallback: if no metadata rating, sort score is 0.

### Step 4: Provider Badges

File: `Retroid_Library_Dashboard.html`

Replace hard-coded IGDB badges with provider-aware badges:

- `SS` when `metadata_provider = screenscraper`
- `IGDB` when `metadata_provider = igdb`
- `Manual` when no external provider
- `Review` badge when `ss_needs_review = true` or confidence is low

Recommended colors:

- ScreenScraper: cyan/teal
- IGDB legacy: purple
- Manual: muted gray
- Review: amber

### Step 5: Cover + Wheel Art

File: `Retroid_Library_Dashboard.html`

Grid card:

- Use `getDisplayCover(g)` for box art.
- If `ss_wheel_url` exists, show wheel/logo overlay near lower left or lower center.
- Keep title text visible even when wheel exists.
- On missing wheel, no layout shift.

List/table:

- Use `display_cover_url`.
- Do not show wheel in dense table unless it remains compact.

Modal:

- Hero uses `display_cover_url`.
- If wheel exists, render it above or near the title as an image with fixed max width.
- Lightbox includes cover and safe screenshots.

### Step 6: Video Placeholder / Player

File: `Retroid_Library_Dashboard.html`

Modal media section:

- If `ss_video_url` exists and is public-safe, render a `<video controls preload="metadata">`.
- If no video but screenshot/fanart exists, show media preview.
- If neither exists, keep current clean empty state.

Rules:

- Never autoplay.
- Never render an SS URL if it includes secret-looking query params.
- Video block should not resize the modal awkwardly.

### Step 7: Duplicate / Platform View

File: `Retroid_Library_Dashboard.html`

Add a fourth view or toggle:

- Current: `Grid`, `Liste`, `Tablo`
- New: `Platformlar` or `Tüm Varyantlar`

Default remains one card per `games.id`.

Show-all mode:

- Flatten `ALL` into virtual card rows:
  - `gameId`
  - `platformId`
  - `title`
  - `platform`
  - `emulator`
  - `romStatus`
  - platform-specific metadata
- Card click calls `openModal(gameId, platformId)`.
- Modal highlights the selected platform row.
- Modal navigation should walk through the current rendered list, not just `games.id`.

Do not create duplicate `games` rows.

### Step 8: RA UI

File: `Retroid_Library_Dashboard.html`

After Claude exposes top-level `ra_supported` and `platforms[].ra_supported`:

- Add `RA supported` filter to Library using top-level `ra_supported`.
- Add small `RA` badge on platform rows when supported.
- In modal platform list, show `RA supported` beside ROM status.
- Full achievement progress panel waits for `ra-sync` / RA game ID mapping.

### Step 9: Cleanup Workspace

File: `Retroid_Cleanup_Workspace.html`

Make cleanup provider-neutral:

- Top note: `Metadata, kapak, özet...`
- `IGDB Eksik` -> `Metadata Eksik`
- `no_external_id` and `no_igdb_rating` labels become provider-neutral when new audit fields exist.
- Keep old labels as fallback if migration_v16 audit fields are not present.

This page should be the review queue for:

- low `ss_match_confidence`
- `ss_needs_review`
- missing safe media
- base64 cover decisions

### Step 10: Secondary Pages

Files:

- `Retroid_Queue.html`
- `Retroid_Tierlist.html`
- `Retroid_Series_Roadmap.html`

Change cover source to prefer `display_cover_url` once views expose it.

Fallback:

```txt
display_cover_url || primary_cover_url
```

No wheel/video needed here.

### Step 11: Navigation

File: `index.html`

Change labels:

- Cleanup card description should say metadata provider, not IGDB-only.
- IGDB Bridge card should be marked legacy after SS UI exists.
- Add or rename a card later:
  - `Metadata Bridge`
  - `ScreenScraper Review`

Do not remove IGDB Bridge until SS coverage is verified.

## Suggested Helper Shape

If `Retroid_Library_Dashboard.html` becomes too dense, create:

```txt
rp5_metadata.js
```

Possible exports on `window.rp5Metadata`:

- `normalizeGame(row)`
- `getProvider(game)`
- `getRating(game)`
- `getCover(game)`
- `getMedia(game)`
- `isSafePublicMediaUrl(url)`

This should be small and dependency-free.

## UI Copy

Preferred labels:

- `Metadata`
- `Metadata Rating`
- `Metadata Eksik`
- `SS`
- `IGDB Legacy`
- `Review`
- `RA`

Avoid:

- claiming SS data exists before enrichment
- calling IGDB "removed" while Bridge/function still exist
- exposing raw provider names everywhere when a provider-neutral label is clearer

## Visual Rules

- Wheel art must not cover title/status controls.
- Video player appears only in modal, not cards.
- Platform view must remain dense and scannable.
- Missing SS media must look intentional, not broken.
- Buttons/status labels should keep stable dimensions across mobile and desktop.

## Verification Checklist

Use Browser after implementation.

Desktop:

- Library loads.
- Grid/list/table render.
- New provider labels render with old `migration_v15` fields.
- Modal opens.
- Lightbox still works.
- Status and ROM buttons still require auth.
- IGDB Bridge link still works.

Mobile:

- Cards do not overflow.
- Modal media does not push content off-screen.
- Platform view remains tappable.

Data scenarios:

- Game with SS fields.
- Game with only IGDB fields.
- Game with no provider match.
- Multi-platform game.
- Game with no cover.
- Game with `ra_supported`.

## Blocked Until Claude

Actual SS-first UI implementation is blocked until:

- `migration_v16` exists.
- `v_games_summary` and `v_games_full` expose provider-neutral fields.
- At least one test game has safe Storage media URLs.

Codex can still do a defensive preparatory refactor before Claude lands the DB work, but the highest-signal implementation should wait for the view contract.

## First Codex Implementation Batch

Once Claude is done:

1. Update Library query and mapper.
2. Add provider-neutral helpers.
3. Replace visible IGDB labels in Library.
4. Add display cover + wheel support.
5. Add modal video/media placeholder.
6. Add platform/show-all view.
7. Verify in Browser.

## Second Codex Implementation Batch

After pilot enrichment:

1. Update Cleanup Workspace as SS review queue.
2. Update Queue/Tier/Series cover fallback.
3. Mark IGDB Bridge legacy in navigation.
4. Add RA badges in modal/platform rows.
5. Verify desktop/mobile.
