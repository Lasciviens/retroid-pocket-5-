# IGDB Integration Notes

Bu repo icin IGDB entegrasyonu iki parcaya ayrildi:

1. **Canli bridge katmani**
2. **Daha sonra DB sync akisi**

## Neden bridge gerekiyor?

IGDB'nin resmi dokumanina gore API erisimi Twitch Developer uzerinden `client_credentials` token ile yapiliyor. Ayni dokuman, tarayicidan IGDB API'ye dogrudan istek atildiginda CORS hatasi alinacagini da acikca soyluyor.

Resmi kaynaklar:

- https://api-docs.igdb.com/
- https://dev.twitch.tv/docs/authentication/getting-tokens-oauth/#client-credentials-grant-flow

Bu yuzden GitHub Pages uzerindeki bu statik site, secret'i frontend'e koymadan calismali. Secilen yapi bu:

- frontend: `Retroid_IGDB_Bridge.html`
- helper: `rp5_igdb.js`
- secret tasiyan katman: ileride eklenecek bir proxy endpoint

## Su an ne hazir?

- `Retroid_IGDB_Bridge.html`
  - oyun adi ile arama
  - proxy varsa canli sonuc gosterme
  - proxy yoksa IGDB web aramasina kopru
  - kutuphaneden query string ile acilabilme: `?title=Chrono%20Trigger`
- `rp5_igdb.js`
  - proxy URL'yi tarayici localStorage'da saklar
  - farkli proxy response formatlarini normalize eder
  - IGDB sayfasina ve fallback web aramasina link uretir

## Beklenen proxy sekli

Bridge su formatta bir endpoint bekler:

`GET /igdb-search?title=Chrono%20Trigger`

Yanit olarak su sekillerden biri kabul edilir:

### Secenek A

```json
[
  {
    "id": 123,
    "name": "Chrono Trigger",
    "slug": "chrono-trigger",
    "summary": "Classic RPG...",
    "total_rating": 96.2,
    "first_release_date": 536457600,
    "cover": { "url": "//images.igdb.com/igdb/image/upload/t_thumb/abc.jpg" },
    "genres": [{ "name": "Role-playing (RPG)" }],
    "platforms": [{ "abbreviation": "SNES" }]
  }
]
```

### Secenek B

```json
{
  "results": [ ... ]
}
```

## Sonraki adim: proxy

Gereken gizli bilgiler:

- Twitch / IGDB Client ID
- Twitch / IGDB Client Secret

Bunlar frontend'e gomulmemeli.

En pratik sonraki deployment secenekleri:

1. Supabase Edge Function
2. Cloudflare Worker
3. Kucuk bir Node endpoint

## Sonraki adim: DB sync

DB senkronu bu turda bilerek yapilmadi.

Daha sonra Claude veya baska bir agent su akisi ekleyebilir:

1. Kutuphanedeki oyunu IGDB ile eslestir
2. Aday sonucu goster
3. Onaylanan alanlari yaz:
   - `games.external_id`
   - `games.description`
   - `games.rating`
   - gerekirse `games.primary_cover_url`
4. Otomatik overwrite yerine alan bazli onay kullan

## Not

Bu dosya mimari karar notudur. Su anki canli site DB'ye yazmadan, sadece bridge ve kaynak baglantisi tarafini hazir tutar.
