# Claude Handoff — 2026-05-09

## Current State

- GitHub Pages is the active host.
- Live site: `https://lasciviens.github.io/retroid-pocket-5-/`
- Repo: `Lasciviens/retroid-pocket-5-`
- Publishing flow: push `main`, then publish to `gh-pages`

## What Was Completed

### Hosting / Deploy

- GitHub Pages migration completed.
- `gh-pages` is the live publishing branch.
- `.nojekyll` exists.

### Auth / Access Model

- Public site is guest-first.
- Visitors can browse without login.
- Auth UI is injected by `rp5_auth.js`.
- Top-right auth control uses:
  - `Log in`
  - `Log out`
- Admin/write actions require Supabase Auth session.
- Session is persisted in browser.

### Protected Actions

Public browse remains open, but write actions require login:

- `Retroid_Library_Dashboard.html`
- `Retroid_Request_Tracker.html`
- `Retroid_Queue.html`
- `Retroid_Tierlist.html`
- `Retroid_Tips.html`

### RLS

- Minimal RLS hardening SQL was prepared in `supabase_rls_hardening.sql`
- User confirmed it was run in Supabase SQL Editor
- Target model:
  - anonymous users can read
  - authenticated users can write

Related docs:

- `SECURITY_NEXT_STEPS.md`
- `SUPABASE_RLS_APPLY.md`

### UX / Cleanup

- Hub now explains guest mode briefly
- Old Netlify links were replaced with GitHub Pages links
- `Retroid_IGDB_Bridge.html` and `rp5_igdb.js` were added as the non-DB IGDB integration layer
- Bridge now reads library candidates, prioritizes titles without `external_id`, and shows simple match scores
- `supabase/functions/igdb-search/index.ts` was added as a ready proxy scaffold for later secret-backed deployment
- The IGDB proxy is now actually deployed at `https://bniqmxbtvgwkaoswugds.supabase.co/functions/v1/igdb-search`
- The bridge page now points to that deployed proxy by default using the public anon headers
- The main Library modal now loads live IGDB summary/rating/link data and shows admin match buttons
- Library sorting uses DB-backed values rather than live IGDB hydration
- `Retroid_IGDB_Bridge.html` now supports:
  - search by title
  - import by IGDB page link / slug
  - `Ana DB'ye Aday Olarak Ekle`
  - `Var Olan Oyunla Eslestir`
  - local genre / series / platform merge against the current schema
  - highlights incoming alternative platforms relative to the selected local game

## Important Constraints

- Do not assume service-role or raw DB credentials are available in repo
- Do not expose secret keys in frontend
- Supabase data is considered sensitive; avoid casual write testing
- Do not reintroduce live IGDB list hydration for sorting/cards; the product direction is DB-first persistence
- Follow `IGDB_DATA_PLAN.md` before expanding schema or bulk sync behavior

## Files Worth Reading First

1. `README.md`
2. `ARCHITECTURE.md`
3. `rp5_auth.js`
4. `rp5_igdb.js`
5. `IGDB_DATA_PLAN.md`
6. `IGDB_INTEGRATION.md`
7. `supabase/functions/igdb-search/index.ts`
8. `supabase_rls_hardening.sql`
9. `SECURITY_NEXT_STEPS.md`
10. `SUPABASE_RLS_APPLY.md`

## Suggested Next Steps

Next-product moves:

1. Use the live bridge add/match flow on more games
2. Use the current live schema and `migration_v7.sql` as the platform-variant baseline
3. Build a bulk `DB <-> IGDB` audit tool
4. Expand schema for screenshots / videos / websites if desired
5. Optional stronger admin-role model later
