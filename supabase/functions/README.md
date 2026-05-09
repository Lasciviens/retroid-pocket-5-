# Supabase Functions

Bu klasor IGDB proxy gibi server-side kopecikler icin hazirlandi.

Su an ekli iskelet:

- `igdb-search/`

Bu function:

- tarayicidan gelen `title` query'sini alir
- Twitch `client_credentials` ile access token alir
- IGDB `games` endpoint'ine server-side sorgu atar
- sonucu browser'a CORS ile geri doner

Gerekli secret'lar:

- `TWITCH_CLIENT_ID`
- `TWITCH_CLIENT_SECRET`

Bkz: `IGDB_INTEGRATION.md`
