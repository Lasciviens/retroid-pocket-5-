# 🎮 Retroid Pocket 5 — Elite Gaming Library

> A personal retro gaming library tracker built for the Retroid Pocket 5 handheld.  
> Live at **[lasciviens.netlify.app](https://lasciviens.netlify.app)**

---

## What is this?

A fully dynamic web app to manage, track, and explore a curated retro game collection — synced across all devices via Supabase.

**Built with:** Vanilla HTML/CSS/JS + Supabase (PostgreSQL) + Netlify

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
| ⚙️ **Emulator Matrix** | Which emulator for which system, pulled from DB |
| 📖 **Glossary** | Technical terms (ROM, BIOS, JIT...) explained for developers |
| ➕ **Admin Panel** | Add/edit/delete games with full form UI |

---

## Architecture

```
Frontend (Static HTML) ──► Supabase REST API ──► PostgreSQL
        │
        └── Netlify (auto-deploy from GitHub)
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

Push to `main` → Netlify auto-deploys in ~30 seconds.

```bash
git add .
git commit -m "your change"
git push
```

---

## Systems Supported

PS1 · PS2 · PSP · GBA · DS · 3DS · N64 · GameCube · Wii · SNES · NES · Genesis · Dreamcast

---

## Notes

- Cover art sourced from [libretro-thumbnails](https://github.com/libretro-thumbnails)
- ROM files are **not** included or linked
- Personal project — not affiliated with Retroid or Anbernic
