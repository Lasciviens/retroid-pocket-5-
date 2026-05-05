# Retroid Pocket 5 — Proje Mimarisi

## Genel Yapı

Static HTML siteleri + Supabase (PostgreSQL) backend. Sunucu yok, framework yok. Her HTML dosyası doğrudan Supabase REST API'sine bağlanır.

**Canlı Site:** https://illustrious-liger-fbd40d.netlify.app  
**GitHub:** https://github.com/Lasciviens/retroid-pocket-5-  
**Supabase:** https://bniqmxbtvgwkaoswugds.supabase.co

---

## Database Schema

### Lookup Tabloları
| Tablo | Açıklama |
|-------|----------|
| `systems` | PS2, GBA, DS... (manufacturer, generation, release_year) |
| `genres` | Action, RPG, Platformer... |
| `series` | God of War, Zelda, Pokemon... |
| `emulators` | AetherSX2, PPSSPP, mGBA... (type: standalone/retroarch_core) |

### Ana Tablolar
| Tablo | Açıklama |
|-------|----------|
| `games` | Oyun kaydı. series_id FK, play_status, rating, is_coop, is_iconic |
| `game_platforms` | Oyun ↔ Sistem ↔ Emülatör bağlantısı. cover_url, performance, folder_path burada |
| `game_genres` | Oyun ↔ Tür (many-to-many) |
| `roms` | Platform başına ROM dosyası. status: missing/searching/found/verified |
| `glossary` | Teknik terimler sözlüğü |
| `notes` | Serbest notlar |

### Kullanışlı View
`games_full` — JOIN'lı tam oyun verisi. Dashboard bu view'i kullanır.

---

## Dosya Yapısı

```
/
├── index.html                  # Ana hub sayfası
├── Retroid_Library_Dashboard.html  # Ana kütüphane — Supabase'den okur
├── Retroid_Coop_Dashboard.html     # Co-op oyun seçici
├── Retroid_Series_Roadmap.html     # 10 serinin yol haritası
├── Retroid_Emulator_Matrix.html    # Emülatör rehberi
├── Retroid_Glossary.html           # Teknik terimler
├── admin.html                  # Oyun ekle/düzenle/sil
├── migrate_v2.html             # İlk data yüklemesi (bir kez çalıştırıldı)
├── ROM_Folder_Guide.md         # ROM klasör yapısı rehberi
├── game_wishlist.md            # Eklenecek oyunlar listesi
├── project_todo.md             # Geliştirme to-do listesi
└── ARCHITECTURE.md             # Bu dosya
```

---

## Yeni Oyun Ekleme

### Yol 1 — Admin Panel (Önerilen)
`/admin.html` → "Yeni Oyun Ekle" sekmesi → Form doldur → Kaydet

### Yol 2 — game_wishlist.md
Dosyaya `- Oyun Adı | Sistem | Not` formatında yaz. Sonraki session'da Claude ekler.

---

## Deployment

GitHub → Netlify otomatik deploy. Push yaptıktan sonra ~30 saniye içinde canlıya geçer.

```bash
git add .
git commit -m "değişiklik açıklaması"
git push
```

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

// Güncelleme
fetch(`${SB_URL}/rest/v1/games?id=eq.${id}`, {
  method: 'PATCH',
  headers: { apikey: SB_KEY, ..., 'Content-Type': 'application/json' },
  body: JSON.stringify({ play_status: 'playing' })
});
```

---

## İleride Yapılacaklar

- [ ] Sorting (release_year var, UI bağlanacak) ✅ release_year eklendi
- [ ] ROM durumu takibi (roms tablosu hazır)
- [ ] Dashboard'dan ROM status güncelleme
- [ ] Harici API entegrasyonu (RAWG/IGDB — external_id kolonu hazır)
- [ ] Co-op Dashboard'u Supabase'e bağla
- [ ] Glossary'yi Supabase'e taşı
