# IGDB Field Map

Bu dosya, IGDB alanlarinin bu projedeki hedef alanlara nasil map edilecegini listeler.

## Games Endpoint'ten Cekilecek Ana Alanlar

IGDB query icinde hedef alanlar:

```txt
name,
slug,
summary,
storyline,
total_rating,
first_release_date,
cover.url,
genres.name,
platforms.name,
platforms.abbreviation,
involved_companies.developer,
involved_companies.publisher,
involved_companies.company.name,
franchises.name,
collections.name,
multiplayer_modes.offlinecoop,
multiplayer_modes.offlinecoopmax,
multiplayer_modes.onlinecoop,
multiplayer_modes.onlinecoopmax,
multiplayer_modes.offlinemax,
multiplayer_modes.onlinemax,
screenshots.url,
videos.video_id,
websites.url,
url
```

## Mapping

| IGDB field | Hedef alan | Seviye | Not |
|---|---|---|---|
| `name` | `games.title` veya `game_platforms.version_title` | canonical / variant | canonical kararina gore |
| `slug` | `game_platforms.igdb_slug` | variant | tek varyant kimligi |
| `summary` | `games.description` | canonical | bossa yaz |
| `storyline` | `games.storyline` | canonical | migration gerekir |
| `total_rating` | `games.igdb_rating` veya `game_platforms.igdb_rating` | canonical / variant | uzun vadede variant daha dogru |
| `first_release_date` | `games.release_year` veya `game_platforms.igdb_first_release_date` | canonical / variant | unix time |
| `cover.url` | `games.primary_cover_url` veya `game_platforms.cover_url` | canonical / variant | platform cover daha guclu |
| `genres.name` | `game_genres` | canonical | lookup merge |
| `platforms.name` | `game_platforms.system_id` | variant | systems map gerekir |
| `involved_companies.company.name` | `games.developer` / `games.publisher` | canonical | developer/publisher flag'ine gore |
| `franchises.name` | `series` / `series_id` | canonical | manuel merge gerekebilir |
| `collections.name` | `series` / `series_id` | canonical | fallback |
| `multiplayer_modes.*` | `games.is_coop`, `games.coop_notes` | canonical / variant | metin normalize edilir |
| `screenshots.url` | `game_media_assets` | canonical | migration gerekir |
| `videos.video_id` | `game_media_assets` | canonical | YouTube linkine cevrilebilir |
| `websites.url` | `game_media_assets` | canonical | store/official ayrimi sonraki adim |
| `url` | `games.igdb_url` veya `game_platforms.igdb_url` | canonical / variant | uzun vadede variant |

## Import Modlari

### 1. Enrich only

- mevcut oyuna sadece eksik alanlar yaz

### 2. Match existing canonical

- `games` kaydi sabit
- `game_platforms` altina yeni varyant ac

### 3. New canonical game

- yeni `games`
- gerekli `game_platforms`
- gerekli `game_genres`

## Not

Bu dosya tekrar tekrar ayni mapping kararlarini vermemek icin var.
