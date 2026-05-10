# Integration Roadmap

Bu dosya, Retroid Pocket 5 projesi icin sonraki entegrasyon kararlarini toplar.

## Secilen Adaylar

### 1. RetroAchievements

Neden guclu:

- resmi API var
- kullaniciya ozel ilerleme cekilebiliyor
- oyun bazli achievement ve completion metadata veriyor
- RP5 ve retro odagi ile dogrudan uyumlu

Bu projede kullanabilecegimiz seyler:

- oyun modalinda achievement ilerlemesi
- kullanicinin son oynadigi retro oyunlar
- "tamamlandi / hardcore tamamlandi" rozeti
- ileride wishlist ve queue icin achievement motivasyon sinyali

Gerekenler:

- `RETROACHIEVEMENTS_USERNAME`
- `RETROACHIEVEMENTS_WEB_API_KEY`

Karar:

- **uygulanacak**
- ilk faz sadece read-only proxy + library modal enrichment

Resmi kaynaklar:

- https://api-docs.retroachievements.org/
- https://api-docs.retroachievements.org/getting-started.html

### 2. SteamGridDB

Neden guclu:

- kutuphane kartlari ve modal icin daha iyi alternatif artwork verebilir
- grid / hero / logo / icon ayrimi var
- RP5 projesinin gorsel kalitesini hizli arttirir

Bu projede kullanabilecegimiz seyler:

- kapak eksik oyunlar icin alternatif kapak onerileri
- kutuphane modalinda "alternatif artwork" secici
- ileride preferred cover secme akisi

Gerekenler:

- `STEAMGRIDDB_API_KEY`

Karar:

- **uygulanacak**
- ilk faz arama + artwork onerisi
- write tarafi manuel onayla ilerlemeli

Kaynaklar:

- https://www.steamgriddb.com/api/v1
- https://github.com/steamgriddb/node-steamgriddb

Not:

- resmi sayfadaki gorunur dokuman v1 olarak listeleniyor; wrapper ve topluluk referanslari v2 tabanli kullanim gosteriyor. Uygulama sirasinda endpoint versiyonu canli anahtarla dogrulanmali.

### 3. RAWG

Neden guclu:

- discovery / recommendation tarafi icin zengin
- benzer oyunlar, store linkleri, ek video/screenshot alanlari sunuyor
- IGDB'nin yanina "kesif" katmani olarak iyi oturur

Bu projede kullanabilecegimiz seyler:

- "bunu sevdiysen sunlari da sev" onerileri
- store / official site linkleri
- extra screenshot / trailer fallback

Gerekenler:

- `RAWG_API_KEY`

Karar:

- **uygulanabilir**
- ama IGDB ve RetroAchievements'tan sonra
- backlink / kullanim kosullari kontrol edilmeli

Kaynak:

- https://rawg.io/apidocs

## Ikinci Grup Adaylar

### MobyGames

Artisi:

- cok zengin metadata
- cover, screenshot, publisher, release bilgisi iyi

Eksisi:

- ucretli
- kisitli rate limit

Karar:

- **opsiyonel**
- sadece daha sonra metadata kalitesini bir ust seviyeye tasimak istersek

Kaynak:

- https://www.mobygames.com/info/api/
- https://www.mobygames.com/api/subscribe/

### ScreenScraper

Artisi:

- retro odakli medya ve scraper ekosistemi

Eksisi:

- entegrasyon ergonomisi daha daginik
- veri yapisi ve rate/credential modeli daha dikkatli ele alinmali

Karar:

- **arastirma adayi**
- ilk uc entegrasyondan sonra tekrar degerlendir

Kaynak:

- https://www.screenscraper.fr/

## Simdilik Beklemeye Alinanlar

### HowLongToBeat

Karar:

- **bekle**

Sebep:

- resmi / acik public API zemini bu tur icin yeterince net degil
- resmi olmayan scrapers veya kirilgan entegrasyonlar istemiyoruz

## Onerilen Sira

1. RetroAchievements proxy
2. SteamGridDB artwork proxy
3. Library / modal tarafinda bu iki entegrasyonun okunmasi
4. RAWG discovery proxy
5. Sonra gerekirse MobyGames veya ScreenScraper

## Repo Durumu

Bu roadmap ile birlikte repo icinde su zemin hazirlandi:

- `supabase/functions/.env.example`
- `supabase/functions/retroachievements-player/`
- `supabase/functions/steamgriddb-art/`
- `supabase/functions/rawg-discover/`

Bu iskeletler secret ve proxy akisini standartlastirmak icin var. Henuz canli secret baglanmadi.
