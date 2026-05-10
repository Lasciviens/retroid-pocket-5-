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
- Gerçek server-side koruma için `supabase_rls_hardening.sql` dosyasındaki RLS adımları sıradaki güvenlik işidir.

---

## Database Schema (v3 — Mayıs 2026)

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
| `emulator_systems` | Emülatör ↔ Sistem (many-to-many). PK: (emulator_id, system_id) |
| `game_genres` | Oyun ↔ Tür (many-to-many). PK: (game_id, genre_id) |

> **Not:** `emulators.supported_systems` (text[]) kolonu geriye dönük uyumluluk için tutuldu. Yeni sorgular `emulator_systems` junction tablosunu kullanır. İleride kaldırılabilir.

### Ana Tablolar
| Tablo | Açıklama |
|-------|----------|
| `games` | Oyun kaydı. series_id FK, play_status, rating, is_coop, is_iconic, tier, play_order |
| `game_platforms` | Oyun ↔ Sistem ↔ Emülatör. cover_url, performance, rom_status, region, folder_path |
| `notes` | Serbest notlar. category: 'tip' / 'request' / 'done'. Opsiyonel game_id FK |
| `glossary` | Teknik terimler sözlüğü |

### Views
| View | Açıklama |
|------|----------|
| `games_full` | Eski view — geriye dönük uyumluluk için korundu |
| `v_games_full` | Yeni tam JOIN view. games + series + genres + platforms (system/emulator) |

### Kaldırılan Tablolar (v3)
| Tablo | Sebep |
|-------|-------|
| `roms` | Boştu, `game_platforms.rom_status` aynı işi yapıyor |

---

## Dosya Yapısı

```
/
├── index.html                      # Ana hub sayfası
├── Retroid_Library_Dashboard.html  # Ana kütüphane — Supabase'den okur
├── Retroid_Coop_Dashboard.html     # Co-op oyun seçici
├── Retroid_Series_Roadmap.html     # 10 serinin yol haritası
├── Retroid_Emulator_Matrix.html    # Emülatör rehberi (emulator_systems kullanır)
├── Retroid_Glossary.html           # Teknik terimler
├── Retroid_Queue.html              # Oyun sırası
├── Retroid_Tierlist.html           # Tier listesi
├── Retroid_Tips.html               # İpuçları (notes tablosu, category=tip)
├── Retroid_Request_Tracker.html    # İstekler (notes tablosu, category=request/done)
├── Retroid_IGDB_Bridge.html        # IGDB arama, link import, aday ekleme ve eslestirme
├── admin.html                      # Oyun ekle/düzenle/sil
├── migration_v3.sql                # DB migration (Supabase SQL Editor'de çalıştırıldı)
├── Retroid_Legacy_Tools.html       # Legacy araçlar için güvenli indeks sayfası
├── legacy_tools/*.html.txt         # Çalıştırılmayan arsiv snapshot'ları
├── Retroid_Cover_Test.html         # Yönetici aracı
├── rp5_igdb.js                     # IGDB bridge helper
├── IGDB_INTEGRATION.md             # IGDB proxy ve sync mimarisi
├── IGDB_DATA_PLAN.md               # IGDB veri kapsami ve sonraki urun yolu
├── supabase/functions/igdb-search  # IGDB proxy scaffold
├── ROM_Folder_Guide.md             # ROM klasör yapısı rehberi
├── game_wishlist.md                # Eklenecek oyunlar listesi
├── project_todo.md                 # Geliştirme to-do listesi
└── ARCHITECTURE.md                 # Bu dosya
```

---

## Yeni Oyun Ekleme

### Yol 1 — Admin Panel (Önerilen)
`/admin.html` → "Yeni Oyun Ekle" sekmesi → Form doldur → Kaydet

### Yol 2 — game_wishlist.md
Dosyaya `- Oyun Adı | Sistem | Not` formatında yaz. Sonraki session'da Claude ekler.

---

## Yeni Emülatör Ekleme

1. `admin.html` veya Supabase Dashboard'dan `emulators` tablosuna ekle
2. `emulator_systems` tablosuna hangi sistemleri desteklediğini ekle:
   ```sql
   INSERT INTO emulator_systems (emulator_id, system_id)
   SELECT e.id, s.id FROM emulators e, systems s
   WHERE e.name = 'YeniEmülatör' AND s.name IN ('PS3', 'Vita');
   ```

---

## Deployment

GitHub Pages yayını `gh-pages` branch üzerinden çalışır.

```bash
git add .
git commit -m "değişiklik açıklaması"
git push
```

Canlıya yayınlamak için:

```bash
git push origin main:gh-pages
```

Migration log: `GITHUB_PAGES_MIGRATION.md`

---

## API Yapısı

Supabase REST API kullanılır. Her sayfa doğrudan fetch() ile bağlanır.

```js
const SB_URL = 'https://bniqmxbtvgwkaoswugds.supabase.co';
const SB_KEY = 'eyJ...'; // anon public key

// Okuma
fetch(`${SB_URL}/rest/v1/games?select=*`, {
  headers: { apikey: SB_KEY, Authorization: `Bearer ${SB_KEY}` }
});

// v_games_full view (tam data, tek sorgu)
fetch(`${SB_URL}/rest/v1/v_games_full?select=*`, {
  headers: { apikey: SB_KEY, Authorization: `Bearer ${SB_KEY}` }
});

// Güncelleme
fetch(`${SB_URL}/rest/v1/games?id=eq.${id}`, {
  method: 'PATCH',
  headers: { apikey: SB_KEY, ..., 'Content-Type': 'application/json' },
  body: JSON.stringify({ play_status: 'playing' })
});
```

---

## Mimari Prensipleri

- **Lookup tabloları** sadece isim/metadata tutar. Hiçbir zaman başka tablonun datasını kopyalamaz.
- **Junction tabloları** (emulator_systems, game_genres) many-to-many ilişkileri temsil eder.
- **Ana tablolar** (games, game_platforms) uygulama datasını tutar.
- **Views** (v_games_full) JOIN'li okumayı kolaylaştırır, data tutmaz.
- **notes tablosu** category kolonu ile farklı amaçlar için kullanılır (tip, request, done). game_id FK opsiyoneldir.
- **Yeni bir sistem veya emülatör eklemek** sadece lookup ve junction tablolarına kayıt eklemek anlamına gelir — hiçbir kod değişmez.

---

## İleride Yapılacaklar

- [ ] emulators.supported_systems kolonunu DROP et (junction tablosu dolduktan sonra)
- [ ] Dashboard'a v_games_full geçişi (şu an nested select ile çalışıyor, her ikisi de doğru)
- [ ] ROM durumu takibi UI (game_platforms.rom_status kolonu hazır)
- [ ] toplu IGDB <-> DB denetim / bulk esleme araci
- [ ] Admin'e emülatör ekleme formu

## Operasyon Notu

- Normal kullanıcı akışı `index.html` üzerinden başlar.
- Legacy migration araçları `legacy_tools/` altında düz metin olarak tutulur.
- `Retroid_IGDB_Bridge.html` artik admin oturumu ile aday ekleme ve mevcut oyunu eslestirme akislarini da tasir.
- `supabase/functions/igdb-search/index.ts` canlı proxy için hazır iskelet sağlar.
- `Retroid_Library_Dashboard.html` modal icinde canli IGDB sonuclarini gosterir; liste/siralama ise DB'ye kaydedilen degerleri kullanir.
- IGDB kapsam kararlari `IGDB_DATA_PLAN.md` icinde tutulur.
- RLS uygulama adımı için `SUPABASE_RLS_APPLY.md` dosyasını kullan.
