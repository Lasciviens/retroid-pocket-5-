# Retroid Pocket 5 — Proje Mimarisi

## Genel Yapı

Static HTML siteleri + Supabase (PostgreSQL) backend. Sunucu yok, framework yok. Her HTML dosyası doğrudan Supabase REST API'sine bağlanır.

**Canlı Site:** https://lasciviens.github.io/retroid-pocket-5-/
**GitHub:** https://github.com/Lasciviens/retroid-pocket-5-
**Supabase:** https://bniqmxbtvgwkaoswugds.supabase.co

## Erişim Modeli

- Site login olmadan okunabilir.
- Yazma yapan butonlar ve yönetim sayfaları Supabase Auth oturumu ister.
- Oturum tarayıcıda saklanır; her ziyarette yeniden giriş gerekmez.

---

## Database Schema (v7 — Mayıs 2026)

### Lookup Tabloları
| Tablo | Açıklama |
|-------|----------|
| `systems` | PS2, GBA, DS... (manufacturer, generation, release_year) |
| `genres` | Action, RPG, Platformer... (id, name, description) |
| `series` | God of War, Zelda, Pokemon... |
| `emulators` | AetherSX2, PPSSPP, mGBA... (type: standalone/retroarch_core) |

### Junction Tabloları
| Tablo | Açıklama |
|-------|----------|
| `emulator_systems` | Emülatör ↔ Sistem (many-to-many) |
| `game_genres` | Oyun ↔ Tür (many-to-many) |

### Ana Tablolar
| Tablo | Açıklama |
|-------|----------|
| `games` | Oyun kaydı + IGDB canonical alanları (igdb_rating, igdb_url, external_id) |
| `game_platforms` | Oyun ↔ Sistem ↔ Emülatör + IGDB platform variant alanları |
| `notes` | Tips / Request Tracker. category: tip/request/done. Opsiyonel game_id FK |
| `glossary` | Teknik terimler sözlüğü |

### game_platforms — Önemli Kolonlar
| Kolon | Açıklama |
|-------|----------|
| `system_id` | FK → systems |
| `emulator_id` | FK → emulators |
| `performance` | good / warn / bad |
| `cover_url` | Platform bazlı kapak (libretro/IGDB CDN) |
| `rom_status` | missing / found / verified / installed / sd_card |
| `rom_url` | ROM dosyasının yerel yolu veya URL'si |
| `igdb_game_id` | IGDB platform variant ID |
| `igdb_rating` | IGDB ham puan (0-100) |
| `igdb_url` | IGDB oyun sayfası |
| `is_primary_variant` | Hangi platform kaydı ana gösterimde kullanılacak |

### Views
| View | Açıklama |
|------|----------|
| `games_full` | Eski view — geriye dönük uyumluluk |
| `v_games_full` | Yeni tam JOIN view — tüm sayfalar bunu kullanmaya geçecek |

---

## Dosya Yapısı

```
/
├── index.html                       # Ana hub sayfası
├── Retroid_Library_Dashboard.html   # Ana kütüphane — grid/list/table görünüm
├── Retroid_Database.html            # Tam DB UI — filtrele, düzenle, ROM URL ekle
├── Retroid_IGDB_Bridge.html         # IGDB eşleştirme ve import
├── Retroid_Cleanup_Workspace.html   # Metadata denetim yüzeyi
├── Retroid_Coop_Dashboard.html      # Co-op oyun seçici
├── Retroid_Series_Roadmap.html      # Seri yol haritası
├── Retroid_Emulator_Matrix.html     # Emülatör rehberi
├── Retroid_Cover_Test.html          # Cover URL test ve güncelleme
├── Retroid_Queue.html               # Oyun sırası
├── Retroid_Tierlist.html            # Tier listesi
├── Retroid_Glossary.html            # Teknik terimler
├── Retroid_Tips.html                # İpuçları (notes.category=tip)
├── Retroid_Request_Tracker.html     # İstekler (notes.category=request)
├── Retroid_Legacy_Tools.html        # Eski araçlara erişim sayfası
├── admin.html                       # Oyun ekle/düzenle/sil
├── rp5_auth.js                      # Supabase Auth helper
├── rp5_igdb.js                      # IGDB Bridge helper
│
├── migrations/                      # Tüm SQL migration geçmişi
│   ├── migration_v3.sql             # emulator_systems, roms DROP, v_games_full
│   ├── migration_v4.sql             # primary_cover_url kolonu
│   ├── migration_v5.sql             # rom_url kolonu
│   ├── migration_v6.sql             # IGDB metadata alanları
│   ├── migration_v7.sql             # Platform variant model
│   └── cover_url_update.sql         # Cover URL güncelleme şablonu
│
├── scripts/                         # Python araçları
│   ├── igdb_bulk_match.py           # Toplu IGDB eşleştirme
│   ├── igdb_repair_missing.py       # Eksik IGDB data onarımı
│   └── igdb_top_import.py           # Top oyun import
│
├── docs/                            # Tüm MD dokümantasyon
│   ├── IGDB_INTEGRATION.md
│   ├── IGDB_DATA_PLAN.md
│   ├── IGDB_IMPORT_PLAYBOOK.md
│   ├── IGDB_FIELD_MAP.md
│   ├── IGDB_QUERY_PRESETS.md
│   ├── INTEGRATIONS_ROADMAP.md
│   ├── PRODUCT_IDEAS_FROM_REFERENCES.md
│   ├── SECURITY_NEXT_STEPS.md
│   ├── SUPABASE_RLS_APPLY.md
│   ├── GITHUB_PAGES_MIGRATION.md
│   ├── ROM_Folder_Guide.md
│   └── TEAM_HANDOFF_ARCHIVE_2026-05-09.md
│
├── legacy_tools/                    # Arşiv (.txt olarak, çalıştırılmaz)
├── supabase/functions/              # Edge function scaffold'ları
├── .github/workflows/               # GitHub Actions (Pages deploy)
│
├── ARCHITECTURE.md                  # Bu dosya
├── TEAM_HANDOFF.md                  # AI ajan koordinasyon protokolü ← OKUMAK ZORUNLU
├── DOCS_INDEX.md                    # Dokümanlara hızlı index
├── README.md                        # Proje tanıtımı
├── project_todo.md                  # Görev backlog'u (tek kaynak)
└── game_wishlist.md                 # Eklenecek oyun kuyruğu
```

---

## Deployment

GitHub Actions → GitHub Pages. Her push'ta otomatik deploy.

```bash
git add .
git commit -m "ajan: claude — açıklama"
git push origin main
```

---

## API Yapısı

```js
const SB_URL = 'https://bniqmxbtvgwkaoswugds.supabase.co';
const SB_KEY = 'eyJ...'; // anon public key

// Okuma
fetch(`${SB_URL}/rest/v1/games?select=*`, {
  headers: { apikey: SB_KEY, Authorization: `Bearer ${SB_KEY}` }
});

// Güncelleme
fetch(`${SB_URL}/rest/v1/games?id=eq.${id}`, {
  method: 'PATCH',
  headers: { apikey: SB_KEY, 'Content-Type': 'application/json' },
  body: JSON.stringify({ play_status: 'playing' })
});
```

---

## Mimari Prensipleri

- **Lookup tabloları** sadece isim/metadata tutar.
- **Junction tabloları** many-to-many ilişkileri temsil eder.
- **Ana tablolar** uygulama datasını tutar.
- **Views** JOIN'li okumayı kolaylaştırır, data tutmaz.
- **primary_cover_url** games tablosunda — tüm sayfalarda bu kullanılır.
- **is_primary_variant** game_platforms'da — hangi platform ana gösterimde çıkar.
- **migrations/** klasörü dokunulmazdır — sadece yeni dosya eklenir.

---

## AI Ajan Koordinasyonu

Ortak çalışma protokolü için: **TEAM_HANDOFF.md** ← her oturumda önce bunu oku.
