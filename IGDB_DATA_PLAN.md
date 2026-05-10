# IGDB Data Plan

Bu dosya, IGDB yonu icin net karar kaydidir.

## Ana Urun Karari

- IGDB rating siralamasi ve kartlardaki IGDB vurgusu canli fetch degil, **DB'ye kaydedilmis alanlar** uzerinden calisir.
- Canli IGDB sorgusu sadece su yuzeylerde kullanilir:
  - `Retroid_IGDB_Bridge.html`
  - kutuphane modalindaki IGDB paneli
  - admin eslestirme / aday ekleme akislarinda
- Hedef: veri once DB'ye girsin, sonra site onu kullansin.

## Canliya Alinan IGDB Akisi

1. Oyun adiyla IGDB arama
2. IGDB sayfasi linkinden ice alma
3. Kendi siteden IGDB sonuc tarama
4. Admin olarak:
   - `Ana DB'ye Aday Olarak Ekle`
   - `Var Olan Oyunla Eslestir`
5. Eslesme ekraninda yerel platformlar / IGDB platformlari / yeni alternatif platformlar karsilastirmasi

## IGDB'den Cekilecek Cekirdek Alanlar

- `title`
- `summary`
- `storyline`
- `release date / year`
- `cover`
- `genres`
- `platforms`
- `rating`
- `developer / publisher`
- `franchise / collection`
- `multiplayer / co-op` sinyalleri
- `screenshots / videos / websites / store links`

## IGDB'den Gelmeyecek Lokal Alanlar

- `emulator`
- `performance`
- `ROM status`
- `folder path`
- `ROM URL`
- `personal notes`
- `play status`
- `queue`
- `tier`
- `wishlist state`
- `curated iconic flags`

## Yerel Kurallar

- `performance`
  - PS2 icin genel varsayim: cihazda cogunlukla oynanir, oyun bazli tweak gerekebilir
  - bridge tarafinda yeni PS2 platform satirlari acilinca varsayilan `warn`
- diger eslesen platformlar icin varsayilan `good`
- IGDB'den gelen ve local DB'de olmayan platformlar `game_platforms` icine alternatif platform satiri olarak acilabilir
- `emulator` ve ROM alanlari manuel/editorial katmanda kalir

## Bu Turda Kasten Yapilmayanlar

- toplu otomatik tum DB matchleme
- mevcut local rating'leri zorla IGDB rating ile overwrite etme
- screenshots / videos / websites icin yeni schema acma

## Sonraki Mantikli Isler

1. `migration_v6.sql` ile `storyline`, `publisher`, `igdb_url`, `igdb_rating`, `igdb_synced_at` alanlarini acmak
2. toplu `DB <-> IGDB` denetim araci
3. mevcut DB oyunlari icin kontrollu eslestirme turu
4. `game_media_assets` uzerinden screenshots / videos / external links saklamak
