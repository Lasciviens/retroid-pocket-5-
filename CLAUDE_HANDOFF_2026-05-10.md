# Claude Handoff — 2026-05-10

## Proje Özeti

Retroid Pocket 5 oyun kütüphanesi. Supabase DB + GitHub Pages statik site.

- **GitHub Pages:** `https://lasciviens.github.io/retroid-pocket-5-/`
- **Repo:** `https://github.com/Lasciviens/retroid-pocket-5-`
- **Supabase URL:** `https://bniqmxbtvgwkaoswugds.supabase.co`
- **Supabase Service Role Key:** `~/retroid-project/igdb_fill_rating.py` dosyasında mevcut (KEY değişkeni)
- **Supabase Anon Key:** `~/retroid-project/igdb_bulk_match.py` dosyasında mevcut (ANON_KEY değişkeni)
- **Supabase PAT:** Kullanıcıdan al (Supabase dashboard → Account → Access Tokens)

---

## Bu Oturumda Yapılanlar

### 0. Sonraki Codex Turu — UI ve Cleanup
Bu handoff sonrasinda kütüphane yüzeyi üzerinde güvenli UX iyilestirmeleri yapildi:
- `Retroid_Library_Dashboard.html`
  - `grid / list / table` gorunum modlari eklendi
  - `IGDB Eksik` filtresi eklendi
  - `Kapak Eksik / Ozet Eksik / Yil Eksik` filtreleri eklendi
  - sonuc ozeti / aktif filtre ozeti eklendi
- `Retroid_Cleanup_Workspace.html`
  - yeni yogun metadata denetim yuzeyi eklendi
  - gap skoru ile cleanup adaylarini one cikarir
  - kutuphane / IGDB / database / kapak araci gecislerini tek satirda toplar
- `Retroid_IGDB_Bridge.html`
  - eslestirme sonuc kartlarinda yerel platformlar, IGDB platformlari ve yeni alternatif platformlar daha net gosteriliyor
- `README.md`, `ARCHITECTURE.md`, `project_todo.md`
  - GitHub Actions deploy modeli ve yeni kutuphane davranislariyla guncellendi
- `DOCS_INDEX.md`
  - markdown notlari icin hizli index eklendi
- Yeni entegrasyon zemini:
  - `INTEGRATIONS_ROADMAP.md`
  - `PRODUCT_IDEAS_FROM_REFERENCES.md`
  - `IGDB_IMPORT_PLAYBOOK.md`
  - `IGDB_FIELD_MAP.md`
  - `IGDB_QUERY_PRESETS.md`
  - `migration_v7.sql`
  - `scripts/igdb_bulk_match.py`
  - `supabase/functions/.env.example`
  - `supabase/functions/retroachievements-player/`
  - `supabase/functions/steamgriddb-art/`
  - `supabase/functions/rawg-discover/`

Not:
- `migration_v6.sql` hala repo'da duruyor ama `igdb_url` ve `igdb_rating` alanlari artik canli DB'de mevcut. Bu migration uygulanmadan once mevcut schema ile tekrar reconcile edilmeli.

### 0b. Sonraki Codex Turu — IGDB Variant Model
Bu handoff sonrasinda `migration_v7.sql` canli schema ile uzlastirildi ve uygulandi:
- `games`
  - `storyline`
  - `publisher`
  - `igdb_synced_at`
- `game_platforms`
  - `igdb_game_id`
  - `igdb_slug`
  - `igdb_url`
  - `igdb_rating`
  - `igdb_release_year`
  - `igdb_first_release_date`
  - `version_title`
  - `is_primary_variant`

Ayrica:
- `Retroid_IGDB_Bridge.html`
  - canonical game + platform_variants mantigina gecti
  - canonical fallback olarak `games.external_id / igdb_rating / igdb_url` koruyor
  - platform varyanti verisini `game_platforms` seviyesinde yazar
- `Retroid_Library_Dashboard.html`
  - manuel `saveIgdbMatch` akisi artik platform varyant alanlarini da gunceller
- `scripts/igdb_bulk_match.py`
  - repo icine alindi
  - bulk match artik canonical patch + variant patch mantigiyla calisiyor
- `~/retroid-project/igdb_bulk_match.py`
  - repo ile senkron yeni surumle guncellendi

Canli backfill kontrolden gecti:
- `game_platforms.igdb_game_id` dolu satir: `228`

### 1. GitHub Pages Deploy Sorunu Çözüldü
Commit `abeb714`'ten sonra GitHub Pages otomatik deploy durmuştu (4 commit birikti, hiç deploy edilmedi). `.github/workflows/pages.yml` custom workflow oluşturuldu. GitHub repo Settings → Pages → Source **"GitHub Actions"** olarak değiştirildi (kullanıcı yaptı). Artık her push'ta otomatik deploy çalışıyor.

### 2. IGDB Puanı Yuvarlama Düzeltildi
`igdbToLocalRating(value)` fonksiyonu `Math.round(value)/10` yerine `parseFloat((value/10).toFixed(1))` kullanacak şekilde güncellendi. `Math.round` 77.7'yi 78'e yuvarlayıp 7.8 yapıyordu; şimdi 7.7 doğru geliyor.

### 3. Kişisel Puan (rating kolonu) Temizlendi
`games.rating` kolonundaki tüm değerler NULL yapıldı (149 oyun). Bu değerler geçmiş scriptlerden geliyordu, kullanıcı girmemişti. Kolon yerinde duruyor — ileride kendi puanlama sistemi için kullanılabilir. Kod da bu kolonu artık hiçbir yerde göstermiyor.

### 4. igdb_url Dolduruldu
228 eşleşmiş oyuna `igdb_url` yazıldı (0 hata). Oyun modalında **"🎮 IGDB Sayfası"** butonu eklendi.

### 5. saveIgdbMatch Köklü Düzeltme
Manuel eşleştirme yapılınca (`saveIgdbMatch`) artık şunlar da yazılıyor:
- `igdb_rating` (ham 0-100 IGDB değeri)
- `igdb_url`
- `title` — bizdeki isim IGDB'den farklıysa IGDB ismiyle güncelleniyor

Eski hatalı `payload.rating = igdbToDbRating(item.rating)` yazımı kaldırıldı.

### 6. 13 Eksik Oyun Dolduruldu
`external_id` olan ama `igdb_rating`/`igdb_url` eksik 13 oyun tespit edildi ve dolduruldu. Bunlar önceki fill scriptleri çalıştıktan sonra manuel eşleştirilen oyunlardı.

Bu arada title sync de yapıldı:
- `"Crash Bandicoot 3: Warped"` → `"Crash Bandicoot: Warped"` (IGDB'de "3" yok)
- `"Lara Croft Tomb Raider: Legend"` → `"Tomb Raider: Legend"`
- `"Harry Potter and the Chamber of Secrets"` → `"Harry Potter and The Chamber of Secrets"`
- `"The Powerpuff Girls: Relish Rampage"` → `"The PowerPuff Girls: Relish Rampage"`

### 7. No-Cache Meta Tag Eklendi
Tarayıcı eski JS'i cache'lemesini önlemek için HTML'e `Cache-Control: no-cache` meta tag'leri eklendi.

---

## DB Şeması (Güncel)

### `games` tablosu — önemli kolonlar
| Kolon | Tip | Açıklama |
|-------|-----|---------|
| `id` | UUID | PK |
| `title` | TEXT | Oyun adı (IGDB ile senkronize ediliyor) |
| `external_id` | TEXT | IGDB game ID |
| `igdb_rating` | NUMERIC(5,2) | IGDB total_rating, **0-100 skalası** (UI'da /10 gösterilir) |
| `igdb_url` | TEXT | `https://www.igdb.com/games/...` |
| `rating` | INTEGER | Kişisel puan 1-10 — **şu an boş**, ileride kullanılacak |
| `primary_cover_url` | TEXT | IGDB cover veya libretro thumbnail |
| `description` | TEXT | IGDB summary |
| `developer` | TEXT | Geliştirici |
| `release_year` | INTEGER | |
| `play_status` | TEXT | backlog/playing/completed/dropped/wishlist |

### `game_platforms` tablosu — önemli kolonlar
| Kolon | Tip | Açıklama |
|-------|-----|---------|
| `id` | UUID | PK |
| `game_id` | UUID | FK → games |
| `system_id` | UUID | FK → systems |
| `rom_status` | TEXT | installed/sd_card/found/missing |
| `rom_url` | TEXT | Cihazdaki dosya yolu |
| `is_preferred` | BOOLEAN | Tercih edilen platform |
| `performance` | TEXT | good/warn/bad |
| `cover_url` | TEXT | Platform-specific kapak |
| `region` | TEXT | |

---

## Mevcut Script Dosyaları (`~/retroid-project/`)

| Dosya | Açıklama |
|-------|---------|
| `igdb_bulk_match.py` | Toplu IGDB eşleştirme (dry-run + --apply) |
| `igdb_fill_rating.py` | external_id'li ama igdb_rating eksik oyunlara puan çeker |
| `igdb_fill_url.py` | external_id'li ama igdb_url eksik oyunlara URL çeker |
| `generate_sql.py` | igdb_dry_run_full.json'dan SQL üretir |
| `sync.py` | Supabase → data.json export |

**DİKKAT:** `igdb_bulk_match.py` dosyasında hâlâ `payload['rating'] = round(best['rating'])` satırı var (yorum satırına alınmamış). Bu satır `rating` kolonuna IGDB'nin 0-100 değerini yazar ve check constraint'i ihlal eder. Çalıştırılmadan önce bu satır kaldırılmalı.

---

## Eşleşmeyen 47 Oyun

İlk bulk match'te 47 oyun eşleşmedi (skor < 90 veya platform overlap yok). Bunlar `external_id = null` durumunda. Kullanıcı isterse Retroid_IGDB_Bridge.html üzerinden manuel eşleştirebilir.

---

## GitHub Pages Workflow

`.github/workflows/pages.yml` — her `main` push'unda otomatik çalışır. GitHub repo Settings → Pages → Source: **"GitHub Actions"** seçili olmalı (değiştirildi, dokunma).

---

## Sıradaki Adım (Kullanıcının Niyeti)

Kullanıcı ISO dosyalarını bulmayı planlıyordu ama bu oturumda yapılmadı. Muhtemelen:
- Mac veya external disk'teki PS2/Wii/diğer ISO dosyalarını tarayıp
- Eşleşen oyunların `game_platforms.rom_status`'unu `found` veya `sd_card` yapmak istiyor
- `rom_url` de doldurulacak

`~/retroid-project/sync.py` çalıştırılarak güncel `data.json` alınabilir.
