# Product Ideas From References

Bu dosya, dis referanslardan alinip Retroid Pocket 5 projesine uyarlanabilecek urun fikirlerini toplar.

Ana referanslar:

- `Tonkatsu Box`
- `RomM`
- `Gaseous`
- `Provenance`

## 1. Cleanup Workspace

Kaynak ilham:

- Tonkatsu Box'in grid/list/table coklu tarama akisi
- RomM'in zengin metadata cleanup / enrich mantigi

Bizde ne olabilir:

- kutuphane icinde "Cleanup Mode"
- sadece admin icin gorunen yogun tablo
- kolonlar:
  - IGDB eslesme
  - kapak eksigi
  - ozet eksigi
  - yil eksigi
  - ROM durumu
  - preferred platform
- satir uzerinden hizli aksiyon:
  - `IGDB Bridge`
  - `Kapak Test`
  - `Database`

Neden degerli:

- metadata tamamlama ve denetim cok hizlanir

## 2. Discovery Shelf

Kaynak ilham:

- Tonkatsu Box search/discovery
- RAWG benzer oyun akislari

Bizde ne olabilir:

- ana hub veya library ustunde minik "Bugun bakilacaklar"
- kategoriler:
  - `IGDB rating yuksek ama eslesmemis`
  - `Co-op icin iyi aday`
  - `Ayni seriden eksik oyun`
  - `Wishlist'ten eklemeye deger`

Neden degerli:

- kutuphane sadece veri saklama yeri degil, karar destek araci olur

## 3. Artwork Manager

Kaynak ilham:

- SteamGridDB artwork yapisi
- Provenance'in "museum-quality library" vurgusu

Bizde ne olabilir:

- oyun modalinda `Kapak Degistir`
- olasi kaynaklar:
  - IGDB
  - libretro thumbnail
  - SteamGridDB
- preferred cover secimi
- kapak eksik oyunlar icin toplu artwork turu

Neden degerli:

- sitenin gorsel kalitesi ciddi artar
- eksik/uyumsuz kapaklar daha az can sıkar

## 4. Progress Layer

Kaynak ilham:

- Tonkatsu Box progress tracking
- RetroAchievements import/progress

Bizde ne olabilir:

- library modalinda:
  - RetroAchievements progress
  - tamamlanan achievement sayisi
  - hardcore durum rozeti
- ileride:
  - oynama oturumu logu
  - son oynanma tarihi

Neden degerli:

- `playing/completed` statulerine daha anlamli bir ikinci katman gelir

## 5. Smart ROM Operations

Kaynak ilham:

- RomM ve igir'in ROM management yaklasimi

Bizde ne olabilir:

- `ROM cleanup mode`
- filtreler:
  - `rom_url eksik`
  - `rom_status found ama yol yok`
  - `preferred platform var ama ROM yok`
- ileride:
  - path normalizer
  - file audit helper

Neden degerli:

- RP5'e gercek dosya hazirlama isiyle mevcut DB arasindaki kopru guclenir

## 6. Collection Boards

Kaynak ilham:

- Tonkatsu Box visual boards

Bizde ne olabilir:

- tam serbest canvas degil
- ama hafif "curated shelf" mantigi:
  - `Esimle Oynanacaklar`
  - `RP5 gelince ilk kurulum`
  - `PS2 showcase`
  - `RPG kis listesi`

Neden degerli:

- mevcut queue ve tierlist arasina daha editoryal bir alan ekler

## 7. Better Series Completion

Kaynak ilham:

- koleksiyon yonetim araclarinda eksik parca gorme hissi

Bizde ne olabilir:

- Series Roadmap icinde:
  - bizde olanlar
  - eksik olanlar
  - IGDB uzerinden bulunabilecek devam oyunlari

Neden degerli:

- seri bazli kararlar cok daha net olur

## Onerilen Oncelik

1. Cleanup Workspace
2. Artwork Manager
3. Progress Layer
4. Discovery Shelf
5. Smart ROM Operations
6. Better Series Completion
7. Collection Boards
