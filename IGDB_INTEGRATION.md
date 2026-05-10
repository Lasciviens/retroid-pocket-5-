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
  - `external_id` bos olan kutuphane oyunlarini one cikarir
  - aday sonuclarda basit eslesme skoru gosterir
  - sonuc kartindan mapping JSON kopyalayabilir
- `rp5_igdb.js`
  - proxy URL'yi tarayici localStorage'da saklar
  - farkli proxy response formatlarini normalize eder
  - IGDB sayfasina ve fallback web aramasina link uretir
  - basit title/year eslesme skoru hesaplar
- `supabase/functions/igdb-search/index.ts`
  - Supabase Edge Function icin deploy edilebilir proxy iskeleti
  - Twitch token alip IGDB `games` endpoint'ine server-side istek atar
  - browser'dan cagri icin CORS header'larini doner

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

Bu repo su an Supabase Edge Function odakli bir scaffold da iceriyor:

- `supabase/functions/igdb-search/index.ts`
- `supabase/functions/README.md`

Bu proxy artik deploy edildi:

- `https://bniqmxbtvgwkaoswugds.supabase.co/functions/v1/igdb-search`

Ornek deploy akisi, Supabase'in resmi docs akisi ile uyumludur:

1. `supabase login`
2. `supabase link --project-ref <project-ref>`
3. `supabase secrets set TWITCH_CLIENT_ID=... TWITCH_CLIENT_SECRET=...`
4. `supabase functions deploy igdb-search`
5. frontend'de proxy URL olarak su adresi kullan:
   `https://<project-ref>.supabase.co/functions/v1/igdb-search`

Bu projede frontend varsayilan olarak su endpoint'e baglidir:

`https://bniqmxbtvgwkaoswugds.supabase.co/functions/v1/igdb-search`

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
