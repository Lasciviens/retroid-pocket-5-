# IGDB Import Playbook

Bu dosya, bu repo icin **IGDB'den veri cekme standardi**dir.

Amaç:

- her seferinde ayni kararları yeniden vermemek
- IGDB import / enrich / compare akislarini tek formatta toplamak
- ayni isimli ama farkli platformdaki oyunlari duplicate etmeden yonetmek

## Kisa Karar

Bu projede **kutuphanede tek oyun gorunur**, platform farklari ise o oyunun altindaki `game_platforms` satirlarinda tutulur.

Yani:

- `games.title` = kanonik / kutuphane adi
- `game_platforms` = platform bazli varyantlar
- IGDB verisi iki katmanda dusunulur:
  1. **canonical game metadata**
  2. **platform variant metadata**

## En Verimli Veri Formati

IGDB'den veri alirken nihai hedef formatimiz su olacak:

```json
{
  "canonical_game": {
    "title": "XXX",
    "normalized_title": "xxx",
    "summary": "...",
    "storyline": "...",
    "developer": "Studio",
    "publisher": "Publisher",
    "franchise": "Series",
    "collection": "Collection",
    "genres": ["Action", "RPG"],
    "themes": [],
    "keywords": [],
    "websites": [],
    "screenshots": [],
    "videos": []
  },
  "platform_variants": [
    {
      "platform": "PlayStation 2",
      "igdb_game_id": 12345,
      "igdb_slug": "xxx",
      "igdb_url": "https://www.igdb.com/games/xxx",
      "release_year": 2004,
      "first_release_date": 1096588800,
      "rating": 88.4,
      "cover_url": "https://...",
      "multiplayer_signals": ["offline co-op", "2 players"],
      "version_title": "XXX",
      "is_primary_variant": true
    }
  ]
}
```

Bu format bizim icin iki seyi ayni anda cozer:

- tek kutuphane oyunu gorunumu
- platform bazli IGDB varyantlarini kaybetmeme

## Standart IGDB Query Seti

Asagidaki alan seti, bu repo icin varsayilan IGDB query alan setidir.

```txt
fields
  name,
  slug,
  summary,
  storyline,
  total_rating,
  total_rating_count,
  first_release_date,
  cover.url,
  genres.name,
  themes.name,
  keywords.name,
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
  url;
```

Bu liste disina cikmak serbest, ama varsayilan enrich / import / compare akislarinda once bu set kullanilmali.

## Standart Query Tarifleri

### 1. Baslik + platform adayi arama

```txt
search "Chrono Trigger";
fields name,slug,summary,total_rating,first_release_date,platforms.name,cover.url,url;
limit 20;
```

### 2. Dogrudan id ile tam veri cekme

```txt
fields
  name,slug,summary,storyline,total_rating,total_rating_count,first_release_date,
  cover.url,genres.name,themes.name,keywords.name,platforms.name,platforms.abbreviation,
  involved_companies.developer,involved_companies.publisher,involved_companies.company.name,
  franchises.name,collections.name,multiplayer_modes.offlinecoop,multiplayer_modes.offlinecoopmax,
  multiplayer_modes.onlinecoop,multiplayer_modes.onlinecoopmax,multiplayer_modes.offlinemax,
  multiplayer_modes.onlinemax,screenshots.url,videos.video_id,websites.url,url;
where id = 12345;
limit 1;
```

### 3. Toplu aday tarama

```txt
fields name,slug,total_rating,first_release_date,platforms.name,cover.url,url;
where platforms = (48, 167, 9, 38);
sort total_rating desc;
limit 50;
```

## Normalize Etme Kurali

IGDB ham cevabi once su formatta normalize edilir:

```json
{
  "canonical_game": {},
  "platform_variants": [],
  "raw_igdb": {
    "id": 12345,
    "slug": "chrono-trigger",
    "url": "https://www.igdb.com/games/chrono-trigger"
  }
}
```

Sonra write karari verilir.

Kural:

1. once normalize et
2. sonra canonical mi variant mi karar ver
3. en son DB'ye yaz

Ham IGDB cevabindan dogrudan DB'ye patch atma.

## Neden Bu Format?

Cunku IGDB'de ayni adli oyunlar:

- farkli platformlarda farkli `id` ile gelebilir
- ayni oyunun PSP / PS1 / PS2 / GC versiyonlari ayri kayit olabilir
- bazen ayni isim ama gercekte farkli port/remaster/re-release olabilir

Eger tek `games.external_id` mantiginda kalirsak:

- sadece bir IGDB kaydini tutabiliriz
- diger platform varyantlarinin IGDB iliskisi kaybolur

Bu yuzden:

- `games` tablosu = kutuphane nesnesi
- `game_platforms` tablosu = platform varyanti

## Hangi IGDB Verilerini Alacagiz?

### Canonical Game seviyesinde

Bunlari oyunun ana kartinda saklamak mantikli:

- `title`
- `summary`
- `storyline`
- `developer`
- `publisher`
- `franchise / collection`
- `genres`
- `themes`
- `keywords`
- `screenshots`
- `videos`
- `websites / store links`

### Platform Variant seviyesinde

Bunlari platform satirinda saklamak mantikli:

- `igdb_game_id`
- `igdb_slug`
- `igdb_url`
- `release_year`
- `first_release_date`
- `rating`
- `cover_url`
- `platform-specific multiplayer signals`
- `version_title`

## Duplicate Olmadan Ayni Isimli Oyunlar

Kural:

### A. Ayni kutuphane oyunu

Su durumda **tek `games` kaydi** kullan:

- oyun ayni eser
- sadece platformu farkli
- kullanici kutuphanede tek baslik gormek istiyor

Ornek:

- `Resident Evil 2` (N64)
- `Resident Evil 2` (GameCube)
- `Resident Evil 2` (PSP listelerinde gelebilen PS1/PSN versiyon)

Kutuphane gorunumu:

- tek oyun: `Resident Evil 2`
- altinda platform varyantlari

### B. Ayri kutuphane oyunu

Su durumda ayri `games` kaydi ac:

- remake / remaster / sequel / expansion ise
- ayni ad olsa bile gercekte farkli eser ise
- kullanicinin kutuphanede ayri takip etmek isteyecegi kadar farkli ise

Ornek karar gerektirir:

- `Persona 3`
- `Persona 3 FES`

Bu tip durumlarda canonical birlestirme **manuel onayli** olmali.

## Platform Varyant Mantigi

Kutuphanede tek baslik gorunmesi icin hedef model:

- `games` = tek satir, tek kutuphane karti
- `game_platforms` = her sistem icin satir
- gelecekte `game_platforms.igdb_game_id` = her sistemin kendi IGDB eslesmesi

Boylece:

- `Silent Hill 2` kutuphanede tek kart olarak gorunebilir
- ama altinda `PS2`, `PSP`, `HD Collection` gibi varyantlar ayri izlenebilir

Bu karar tekrar tekrar tartisilmasin diye varsayilan modelimiz budur.

## Import Karar Agaci

1. IGDB sonucu bulundu
2. Ad benzerligi kontrol et
3. Platform overlap kontrol et
4. Seri / gelistirici / yil sinyali kontrol et
5. Eslesme tipi sec:
   - `existing canonical game + new platform variant`
   - `existing canonical game + enrich metadata`
   - `new canonical game`
   - `manual review`

## Onerilen Eslesme Kurallari

### Otomatik guvenli

- ad cok yakin
- platform uyusuyor
- yil farki makul
- farkli eser olduguna dair isaret yok

### Manuel inceleme

- ayni ad ama farkli yil / farkli platform kuskulu
- remaster / director's cut / FES / HD / definitive benzeri ekler var
- seri bilgisi uyusmuyor

## Bu Repoda Neyi Degistirmeliyiz?

Su an:

- `games.external_id`
- `games.igdb_url`
- `games.igdb_rating`

oyun seviyesinde tutuluyor.

Bu, tek varyant icin yeterli ama coklu varyant icin dar.

Oneri:

- `games` seviyesindeki alanlari **canonical / default** olarak koru
- platform bazli IGDB kimligini `game_platforms` seviyesine indir

## Onerilen Migration v7

Bu dosya ile birlikte canonical + platform_variants standardi kullanilir.

Temel fikir:

- `game_platforms.igdb_game_id`
- `game_platforms.igdb_slug`
- `game_platforms.igdb_url`
- `game_platforms.igdb_rating`
- `game_platforms.igdb_release_year`
- `game_platforms.igdb_first_release_date`
- `game_platforms.version_title`
- `game_platforms.is_primary_variant`

## Calisma Rutini

Bundam sonra IGDB ile calisirken sira su olmali:

1. `IGDB_IMPORT_PLAYBOOK.md` oku
2. `IGDB_DATA_PLAN.md` oku
3. canonical + platform_variants mantigina gore dusun
4. once canonical game mi platform variant mi karar ver
5. sonra write yap

## Kaynaklar

- https://api-docs.igdb.com/
- https://api-docs.igdb.com/#games
- https://api-docs.igdb.com/#release-date
- https://api-docs.igdb.com/#platform
- https://api-docs.igdb.com/#multiplayer-mode
- https://dev.twitch.tv/docs/authentication/getting-tokens-oauth/#client-credentials-grant-flow
