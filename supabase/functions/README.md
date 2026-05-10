# Supabase Functions

Bu klasor browser'a secret koymadan dis servislerle konusmak icin server-side proxy katmani olarak kullanilir.

## Hazir Function'lar

- `igdb-search/`
- `retroachievements-player/`
- `steamgriddb-art/`
- `rawg-discover/`

## Secret Listesi

Ornek secret dosyasi:

- `.env.example`

Muhtemel secret'lar:

- `TWITCH_CLIENT_ID`
- `TWITCH_CLIENT_SECRET`
- `RETROACHIEVEMENTS_USERNAME`
- `RETROACHIEVEMENTS_WEB_API_KEY`
- `STEAMGRIDDB_API_KEY`
- `RAWG_API_KEY`
- `MOBYGAMES_API_KEY`
- `SCREENSCRAPER_USER`
- `SCREENSCRAPER_PASSWORD`

## Hedef

- browser sadece bu function'lari cagirir
- ucuncu taraf anahtarlar frontend'e gomulmez
- her entegrasyon kademeli olarak acilir

## Oncelik Sirasi

1. IGDB
2. RetroAchievements
3. SteamGridDB
4. RAWG

Bkz:

- `IGDB_INTEGRATION.md`
- `INTEGRATIONS_ROADMAP.md`
