# TEAM HANDOFF — Retroid RP5

> **Bu dosya tüm AI ajanlar için tek ortak çalışma günlüğüdür.**
> Claude · Codex App · Codex Web — hepsi buraya yazar, buradan okur.
> Bir göreve başlamadan önce bu dosyayı, AI_RULES.md ve ARCHITECTURE.md'yi oku.

---

## Proje Kimliği

| | |
|---|---|
| **Site** | https://lasciviens.github.io/retroid-pocket-5-/ |
| **Repo** | https://github.com/Lasciviens/retroid-pocket-5- |
| **Supabase** | https://bniqmxbtvgwkaoswugds.supabase.co |
| **Deploy** | GitHub Actions → GitHub Pages (her push'ta otomatik) |
| **GitHub PAT** | memory'de kayıtlı (claude session memory) |
| **Supabase Service Key** | memory'de kayıtlı |

---

## Genel Proje Tanımı

Furkan'ın Retroid Pocket 5 el konsolu için kişisel retro oyun kütüphanesi.
Supabase (PostgreSQL) + statik HTML + GitHub Pages. Framework yok, sunucu yok.
323 oyun kayıtlı. Oyunların ~319'unda IGDB eşleşmesi var.

---

## Mevcut DB Schema (v10 — Mayıs 2026)

### games tablosu — önemli kolonlar
- `id`, `title`, `release_year`, `developer`, `publisher`
- `description`, `storyline` — açıklamalar
- `keywords TEXT[]`, `screenshots TEXT[]` — IGDB'den
- `themes TEXT[]` — YENİ (migration_v9, henüz boş)
- `age_rating TEXT` — YENİ (migration_v9, henüz boş)
- `rating_count INTEGER` — YENİ (migration_v9, henüz boş)
- `multiplayer_info TEXT[]` — YENİ (migration_v9, henüz boş)
- `is_coop`, `coop_notes` — co-op bilgisi
- `play_status`, `play_notes`, `game_log`, `play_order`, `tier`
- `primary_cover_url` — ana kapak görseli
- `series_id FK`, `external_id` — IGDB canonical ID
- `igdb_rating`, `igdb_url`, `igdb_synced_at`

### game_platforms tablosu — önemli kolonlar
- `system_id`, `emulator_id`, `performance`, `cover_url`
- `rom_status`, `rom_url`, `region`, `folder_path`
- `is_primary_variant` — hangi platform ana gösterimde kullanılır
- `igdb_game_id`, `igdb_slug`, `igdb_rating`, `igdb_url`
- `igdb_release_year`, `version_title`

### Views
- `v_games_full` — tüm JOIN'ları içerir, tüm sayfalar bunu kullanır

---

## AŞAMA 3 — SİRADAKİ GÖREV (ŞU AN BURADA)

### ⚡ Şu an çalışıyor: IGDB Full Sync (GitHub Actions)
Actions → IGDB Full Sync workflow çalışıyor/çalıştırılacak.
Sync edilen alanlar: screenshots, keywords, genres, storyline, developer, publisher,
multiplayer, franchises, themes, age_rating, rating_count

**Workflow çalıştıktan sonra yapılacaklar:**

### 1. Sonuçları kontrol et
```
SELECT title, themes, age_rating, rating_count, multiplayer_info,
       array_length(screenshots,1) ss, array_length(keywords,1) kw
FROM v_games_full 
WHERE themes != '{}' OR age_rating IS NOT NULL
LIMIT 10;
```

### 2. Library Dashboard modalına yeni alanları ekle
Şu an modal'da gösterilmeyen ama DB'de olan alanlar:
- `themes` → "Temalar: Open World, Sci-fi" gibi
- `age_rating` → "PEGI 18" gibi badge
- `rating_count` → "47.8k değerlendirme" gibi
- `multiplayer_info` → "Offline co-op (2)" gibi
- `screenshots` → oyun görselleri galerisi

Dosya: `Retroid_Library_Dashboard.html`

### 3. Co-op Dashboard'ı geliştir
`multiplayer_info` array'i artık dolacak. Co-op filtresi daha akıllı hale gelebilir.
Dosya: `Retroid_Coop_Dashboard.html`

---

## TAMAMLANAN BÜYÜK İŞLER (Bu session)

- [x] DB mimarisi temizlendi: emulator_systems junction, roms DROP, notes FK
- [x] `primary_cover_url` games tablosuna eklendi, tüm cover'lar düzeltildi
- [x] `v_games_full` view oluşturuldu ve tüm sayfalar buna geçirildi
- [x] migration_v8: keywords, screenshots kolonları
- [x] migration_v9: themes, age_rating, rating_count, multiplayer_info kolonları
- [x] migration_v10: v_games_full yeni kolonlarla güncellendi
- [x] Repo organizasyonu: migrations/, docs/ klasörleri
- [x] IGDB Full Sync GitHub Action workflow oluşturuldu
- [x] AI_RULES.md, TEAM_HANDOFF.md protokolü kuruldu
- [x] GitHub PAT, Supabase keys memory'e kaydedildi
- [x] Emülatör bağlantıları tamamlandı (157 NULL → dolduruldu)
- [x] is_primary_variant game_platforms'a eklendi

---

## AÇIK KALAN GÖREVLER (project_todo.md'den)

### Yüksek Öncelik
- [ ] IGDB Full Sync sonuçlarını doğrula
- [ ] Library Dashboard modal'ına yeni alanları göster
- [ ] Co-op Dashboard'u multiplayer_info ile güşlendir
- [ ] Genres eksikliği — sync sonrası kontrol et, hâlâ boşsa manuel ekle

### Orta Öncelik
- [ ] Session Log — oyun başına ne zaman oynadım tablosu
- [ ] Artwork Manager — cover seçimi arayüzü
- [ ] Admin panele emülatör ekleme formu

### Teknik Borç
- [ ] emulators.supported_systems kolonu DROP et (emulator_systems junction doldu)
- [ ] games_full eski view'ini DROP et (v_games_full var)

---

## ÖNEMLİ KURALLAR (AI_RULES.md özeti)

1. `game_log` alanını kullanıcı onayı olmadan TEMİZLEME
2. Mevcut oyunu DELETE yapmadan önce kullanıcıya sor
3. `migrations/` klasörüne dokunma — sadece yeni SQL ekle
4. IGDB en güvenilir data kaynağı — oyuna ait saf veri (genre, theme vb.) için IGDB kullan
5. Commit mesajı: `ajan: claude — feat: açıklama`
6. DB'ye yazarken duplicate kontrolü yap

---

## IGDB SYNC WORKFLOW KULLANIMI

Actions → IGDB Full Sync → Run workflow

**Parametreler:**
- `fields`: hangi alanları sync edeceğin (varsayılan: hepsi)
- `game_ids`: spesifik UUID'ler (boşsa tümü)
- `limit`: max oyun sayısı

**Örnek — sadece 5 oyun test:**
- fields: `genres,themes`
- game_ids: `uuid1,uuid2,uuid3,uuid4,uuid5`

---

## GITHUB & DEPLOYMENT

```bash
# Sandbox'tan push (Claude için):
# GitHub API kullanılıyor — git push sandbox'tan çalışmıyor

# Sen push yapacaksan:
cd "C:\Users\fuha00\CP - Retroid"
git pull origin main   # önce çek
git add .
git commit -m "açıklama"
git push
```

Site: https://lasciviens.github.io/retroid-pocket-5-/

---

## AJAN DURUMU

### In Progress
- [ ] IGDB Full Sync çalışıyor/çalıştırılacak — ajan: furkan

### Done (Bu Session)
- [x] DB schema v9-v10 tamamlandı — ajan: claude — 2026-05-11
- [x] igdb_full_sync workflow hazırlandı — ajan: claude — 2026-05-11
- [x] AI koordinasyon sistemi kuruldu — ajan: claude — 2026-05-11
- [x] Tüm sayfalar v_games_full'a geçirildi — ajan: claude — 2026-05-11
- [x] 157 emülatör NULL bağlantısı dolduruldu — ajan: claude — 2026-05-11
