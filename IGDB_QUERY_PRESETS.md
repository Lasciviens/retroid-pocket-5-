# IGDB Query Presets

Bu dosya, tekrar kullanacagimiz IGDB query kaliplarini toplar.

Amaç:

- ayni field setlerini tekrar tekrar yazmamak
- hangi veri ne icin cekiliyor net olsun
- import ve enrich akislari daha hizli olsun

## 1. Minimal Search

Baslik ararken hizli sonuc:

```txt
search "{TITLE}";
fields name,slug,total_rating,first_release_date,platforms.name,cover.url,url;
limit 20;
```

Kullanim:

- manuel arama
- bridge aday listesi
- hizli karsilastirma

## 2. Full Game Fetch

Bir eslesme secildikten sonra olabildigince zengin veri:

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
where id = {IGDB_ID};
limit 1;
```

Kullanim:

- DB enrich
- yeni oyun ekleme
- canonical + variant normalize etme

## 3. Platform Top List

Platform bazli aday kesfi:

```txt
fields name,slug,total_rating,total_rating_count,first_release_date,platforms.name,cover.url,url;
where platforms = ({PLATFORM_ID});
sort total_rating desc;
limit 100;
```

Kullanim:

- top oyunlardan DB gap analizi
- wishlist / discovery adaylari

## 4. Name + Platform Safer Match

Baslik ayni ama platform kritikse:

```txt
search "{TITLE}";
fields name,slug,total_rating,first_release_date,platforms.name,platforms.abbreviation,cover.url,url;
limit 50;
```

Sonra local taraf:

- ad yakinligi
- platform overlap
- yil sinyali
- seri / publisher

ile skorlanir.

## 5. Normalize Payload

IGDB cevabi once buna cevrilir:

```json
{
  "canonical_game": {
    "title": "",
    "summary": "",
    "storyline": "",
    "developer": "",
    "publisher": "",
    "franchise": "",
    "collection": "",
    "genres": [],
    "themes": [],
    "keywords": [],
    "websites": [],
    "screenshots": [],
    "videos": []
  },
  "platform_variants": [
    {
      "platform": "",
      "igdb_game_id": 0,
      "igdb_slug": "",
      "igdb_url": "",
      "release_year": null,
      "first_release_date": null,
      "rating": null,
      "cover_url": "",
      "version_title": "",
      "multiplayer_signals": [],
      "is_primary_variant": false
    }
  ]
}
```

## 6. Yazma Sirasi

Standart sira:

1. query calistir
2. ham cevabi al
3. normalize et
4. canonical / variant kararini ver
5. sonra DB write yap

Direkt ham IGDB response'u DB'ye yama olarak gecme.
