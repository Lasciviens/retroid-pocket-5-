# 🎮 Retroid Pocket 5 — Elite Gaming Library

> A personal retro gaming library tracker built for the Retroid Pocket 5 handheld.  
> Live at **[lasciviens.github.io/retroid-pocket-5-](https://lasciviens.github.io/retroid-pocket-5-/)**

---

## What is this?

A fully dynamic web app to manage, track, and explore a curated retro game collection — synced across all devices via Supabase.

**Built with:** Vanilla HTML/CSS/JS + Supabase (PostgreSQL) + GitHub Pages

No frameworks. No build step. Every page talks directly to the Supabase REST API.

---

## Features

| Page | Description |
|------|-------------|
| 📚 **Library** | 100+ games with cover art, filters (system, genre, series), sorting by year/rating, play status |
| 👫 **Co-op Hub** | Filtered view of 2-player games with random suggestion engine |
| 🗺️ **Series Roadmap** | Chronological game list per series — where to start each franchise |
| 🎮 **Play Queue** | Drag-and-drop play order, synced across devices |
| ♡ **Wishlist** | Track games to add, emulator requests, features — with priority levels |
| 🛰️ **IGDB Bridge** | IGDB arama, link import, aday ekleme, ve mevcut oyun eslestirme yuzeyi |
| ⚙️ **Emulator Matrix** | Which emulator for which system, pulled from DB |
| 📖 **Glossary** | Technical terms (ROM, BIOS, JIT...) explained for developers |
| ➕ **Admin Panel** | Add/edit/delete games with full form UI |

## Access Model

- Public visitors can browse the site without logging in.
- Write actions and admin pages use a remembered Supabase Auth session.
- The browser keeps your admin session so you are not asked on every visit.
- Server-side RLS hardening is prepared in `supabase_rls_hardening.sql` and should be applied in Supabase next.
- Legacy migration/import tools are archived and no longer part of the live product surface.
- The main Library modal includes live IGDB summary and bridge controls, but sorting uses DB-stored values rather than live IGDB fetches.
- `Retroid_IGDB_Bridge.html` now supports IGDB page link import, admin-side candidate creation, and matching existing local games.

---

## Architecture

```
Frontend (Static HTML) ──► Supabase REST API ──► PostgreSQL
        │
        └── GitHub Pages (published from gh-pages branch)
```

### Database Schema

```
systems          → PS1, PS2, PSP, GBA, DS, GameCube, Wii...
genres           → Action, RPG, Platformer...
series           → God of War, Zelda, Pokemon...
emulators        → AetherSX2, PPSSPP, Dolphin, mGBA...
games            → title, release_year, is_coop, play_status, rating...
game_platforms   → game ↔ system ↔ emulator (cover_url, performance)
game_genres      → game ↔ genre (many-to-many)
roms             → ROM file tracking per platform
glossary         → Technical terms
notes            → Wishlist / free notes
```

All play status updates sync in real-time across devices — phone, tablet, PC, all see the same state.

---

## Deployment

GitHub Pages is published from the `gh-pages` branch.

```bash
git add .
git commit -m "your change"
git push
```

To publish the current static site to GitHub Pages:

```bash
git push origin main:gh-pages
```

Migration notes: `GITHUB_PAGES_MIGRATION.md`
Security follow-up: `SECURITY_NEXT_STEPS.md`
RLS apply checklist: `SUPABASE_RLS_APPLY.md`
IGDB bridge notes: `IGDB_INTEGRATION.md`
IGDB data plan: `IGDB_DATA_PLAN.md`
Supabase proxy scaffold: `supabase/functions/igdb-search/index.ts`

---

## Systems Supported

PS1 · PS2 · PSP · GBA · DS · 3DS · N64 · GameCube · Wii · SNES · NES · Genesis · Dreamcast

---

## Notes

- Cover art sourced from [libretro-thumbnails](https://github.com/libretro-thumbnails)
- ROM files are **not** included or linked
- Personal project — not affiliated with Retroid or Anbernic
