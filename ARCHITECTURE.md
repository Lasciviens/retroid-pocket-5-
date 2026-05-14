# Retroid Pocket 5 — Proje Mimarisi

> **Anlık proje durumu için:** [`CURRENT_STATE.md`](CURRENT_STATE.md)  
> Bu dosya statik mimari referanstır — değişmez gerçekler burada, anlık durum CURRENT_STATE'de.

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

## Database Schema (Current)

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
| `games` | Oyun kaydı + IGDB canonical alanları (igdb_rating, igdb_url, external_id, publisher, storyline) |
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
| `v_games_summary` | Ana kütüphane liste/kart görünümü için hafif özet view |
| `v_games_full` | Tek oyun detay modalı ve ağır metadata fetch için tam view |
| `v_games_cleanup` | Cleanup Workspace için hızlı admin anomaly özeti |
| `v_games_audit` | Audit score + issue_types ile yoğun kalite kontrol view |
| `v_game_platform_audit` | Platform satırı bazında anomaly view |

---

## Dosya Yapısı

```
/
├── index.html                      # Ana hub sayfası
├── Retroid_Library_Dashboard.html  # Ana kütüphane — grid/list/table görünüm
├── Retroid_Cleanup_Workspace.html  # Metadata denetim yüzeyi
├── Retroid_IGDB_Bridge.html        # IGDB eşleştirme ve import
├── Retroid_Series_Roadmap.html     # Seri yol haritası
├── Retroid_Emulator_Matrix.html    # Emülatör rehberi
├── Retroid_Queue.html              # Oyun sırası
├── Retroid_Tierlist.html           # Tier listesi
├── Retroid_Glossary.html           # Teknik terimler
├── Retroid_Tips.html               # İpuçları (notes.category=tip)
├── Retroid_Request_Tracker.html    # İstekler (notes.category=request)
├── rp5_auth.js                     # Supabase Auth helper
├── rp5_igdb.js                     # IGDB Bridge helper
├── scripts/                        # Python araçları
│   ├── igdb_bulk_match.py
│   ├── audit_report.py
│   ├── igdb_repair_missing.py
│   └── igdb_top_import.py
├── migrations/
│   ├── migration_v12.sql
│   ├── migration_v14.sql
│   └── migration_v15.sql
├── docs/
│   └── audit_system.md
├── supabase/functions/igdb-search  # IGDB proxy
├── README.md
├── ARCHITECTURE.md
├── project_todo.md
```

---

## Yeni Emülatör Ekleme

1. Supabase Dashboard'dan `emulators` tablosuna ekle
2. `emulator_systems` tablosuna hangi sistemleri desteklediğini ekle:
   ```sql
   INSERT INTO emulator_systems (emulator_id, system_id)
   SELECT e.id, s.id FROM emulators e, systems s
   WHERE e.name = 'YeniEmülatör' AND s.name IN ('PS3', 'Vita');
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
- Eski migration geçmişi repodan temizlendi; sadece güncel referans migration tutulur.

---

## AI Ajan Koordinasyonu

Okuma sırası: `CURRENT_STATE.md` → `AI_RULES.md` → `project_todo.md` → bu dosya.
