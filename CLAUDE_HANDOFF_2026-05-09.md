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

### Protected Pages

These pages are now gated for admin/write use:

- `admin.html`
- `Retroid_Database.html`
- `Retroid_Cover_Test.html`

These pages remain readable publicly, but write actions require login:

- `Retroid_Library_Dashboard.html`
- `Retroid_Request_Tracker.html`
- `Retroid_Queue.html`
- `Retroid_Tierlist.html`
- `Retroid_Coop_Dashboard.html`
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
- Admin page navigation was cleaned up
- Database page got a clearer management note
- Old Netlify links were replaced with GitHub Pages links
- Docs were updated to distinguish active product pages vs legacy migration tools
- Legacy migration/import pages were archived into `legacy_tools/*.html.txt`
- `Retroid_Legacy_Tools.html` now points to archived tool snapshots safely
- `Retroid_IGDB_Bridge.html` and `rp5_igdb.js` were added as the non-DB IGDB integration layer
- Bridge now reads library candidates, prioritizes titles without `external_id`, and shows simple match scores
- `supabase/functions/igdb-search/index.ts` was added as a ready proxy scaffold for later secret-backed deployment

## Important Constraints

- Do not assume service-role or raw DB credentials are available in repo
- Do not expose secret keys in frontend
- Supabase data is considered sensitive; avoid casual write testing
- Do not do DB-level IGDB sync until credentials and matching rules are explicitly agreed

## Files Worth Reading First

1. `README.md`
2. `ARCHITECTURE.md`
3. `rp5_auth.js`
4. `rp5_igdb.js`
5. `IGDB_INTEGRATION.md`
6. `supabase/functions/igdb-search/index.ts`
7. `supabase_rls_hardening.sql`
8. `SECURITY_NEXT_STEPS.md`
9. `SUPABASE_RLS_APPLY.md`

## Suggested Next Steps

Small, safe next moves:

1. UX polish for `Retroid_Queue.html` and `Retroid_Tierlist.html`
2. Deploy the Supabase Edge Function proxy using Twitch / IGDB credentials
3. Add approved field-level IGDB -> DB sync after proxy is live
4. Optional stronger admin-role model later
