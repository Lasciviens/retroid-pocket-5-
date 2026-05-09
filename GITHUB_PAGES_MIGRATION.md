# GitHub Pages Migration Log

Date: 2026-05-09

## Goal

Move the static Retroid Pocket 5 dashboard away from Netlify usage limits and publish it with GitHub Pages.

Target GitHub Pages URL:

```text
https://lasciviens.github.io/retroid-pocket-5-/
```

## Data Safety Rules

- Do not modify Supabase data during hosting migration.
- Do not run `INSERT`, `UPDATE`, `PATCH`, or `DELETE` against Supabase as part of this migration.
- Keep existing game, system, emulator, genre, series, note, and glossary data intact.
- Hosting migration only changes where static HTML files are served from.

## Supabase Snapshot Before Migration

Snapshot source: `~/retroid-project/data.json`, refreshed from Supabase on 2026-05-09.

| Table/data group | Count |
|---|---:|
| games | 202 |
| systems | 15 |
| genres | 17 |
| series | 39 |
| emulators | 14 |
| notes | 6 |
| glossary | 12 |

ROM status totals from `game_platforms`:

| rom_status | Count |
|---|---:|
| sd_card | 79 |
| found | 4 |
| missing | 109 |
| installed | 0 |

Previously added recommendation games confirmed present:

| Game | System | Emulator | Rating | Tier |
|---|---|---|---:|---|
| Burnout 3: Takedown | PS2 | AetherSX2 | 10 | S |
| Gran Turismo 4 | PS2 | AetherSX2 | 10 | S |
| Dragon Quest VIII | PS2 | AetherSX2 | 10 | S |
| F-Zero GX | GameCube | Dolphin | 10 | S |
| Skies of Arcadia Legends | GameCube | Dolphin | 10 | S |
| Jet Set Radio | Dreamcast | Flycast | 9 | A |
| Vagrant Story | PS1 | DuckStation | 10 | S |
| Chrono Trigger | SNES | Snes9x | 10 | S |

## Repository Changes

Added:

- `.github/workflows/pages.yml` - GitHub Actions workflow for GitHub Pages deployment.
- `.nojekyll` - disables Jekyll processing so static files are served as-is.
- `GITHUB_PAGES_MIGRATION.md` - this migration log for future AI/human maintainers.

Updated:

- `README.md` - deployment target now documents GitHub Pages instead of Netlify.
- `ARCHITECTURE.md` - hosting architecture now documents GitHub Pages.

## Current Architecture

```text
GitHub repository
  -> GitHub Pages static hosting
  -> browser loads HTML/CSS/JS
  -> Supabase REST API
  -> PostgreSQL data
```

There is no frontend build step. The root `index.html` is the app entry point.

## Important Follow-up

This migration does not clean public admin/migration pages yet. That is intentional because the request was to preserve all current behavior first.

Security cleanup should happen next:

- Review public write access in Supabase RLS (Row Level Security -- row-based access control).
- Move or remove one-time migration HTML pages from public navigation/deployment.
- Protect admin/write pages with Supabase Auth (authentication -- login/user identity).
- Re-check CORS (Cross-Origin Resource Sharing -- browser rule for calls between different domains) if GitHub Pages cannot call Supabase.

