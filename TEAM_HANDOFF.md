# TEAM HANDOFF — Retroid RP5

> **Bu dosya tüm AI ajanlar için tek ortak çalışma günlüğüdür.**
> Claude · Codex App · Codex Web — hepsi buraya yazar, buradan okur.
> Bir göreve başlamadan önce bu dosyayı oku. Bitirince güncelle.

---

## Proje Kimliği

| | |
|---|---|
| **Site** | https://lasciviens.github.io/retroid-pocket-5-/ |
| **Repo** | https://github.com/Lasciviens/retroid-pocket-5- |
| **Supabase** | https://bniqmxbtvgwkaoswugds.supabase.co |
| **Deploy** | GitHub Actions → GitHub Pages (her push'ta otomatik) |

---

## Repo Yapısı (Güncel)

```
/
├── *.html              # Canlı sayfalar (Library, Database, IGDB Bridge vs.)
├── index.html          # Ana hub
├── admin.html          # Oyun ekle/düzenle/sil
├── rp5_auth.js         # Supabase Auth helper
├── rp5_igdb.js         # IGDB Bridge helper
├── migrations/         # Tüm SQL migration dosyaları (v3→v7)
├── scripts/            # Python araçları (igdb_bulk_match.py vs.)
├── legacy_tools/       # Eski migration HTML'leri (.txt olarak arşivlendi)
├── supabase/functions/ # Edge function scaffold'ları
├── docs/               # Tüm MD dokümantasyon (IGDB, RLS, Roadmap vs.)
├── ARCHITECTURE.md     # Teknik mimari (OKUMAK ZORUNLU)
├── TEAM_HANDOFF.md     # Bu dosya — ortak çalışma günlüğü
├── DOCS_INDEX.md       # Dokümanlara hızlı index
└── project_todo.md     # Görev backlog'u (TEK kaynak)
```

---

## Ajan Çalışma Protokolü

### Başlamadan önce:
1. Bu dosyayı oku (son "In Progress" ve "Done" bölümleri)
2. `project_todo.md`'yi oku (aktif backlog)
3. `ARCHITECTURE.md`'yi oku (schema, mimari prensipleri)

### Çalışırken:
4. Üstlendiğin görevi aşağıda **In Progress** olarak işaretle
5. Başkasının "In Progress" olarak işaretlediği göreve dokunma

### Bitirince:
6. Görevi **Done** bölümüne taşı, ne yaptığını 1 satırda yaz
7. `project_todo.md`'yi güncelle
8. İlgili MD dokümanı güncelle (varsa)
9. Commit mesajında "ajan: claude|codex-app|codex-web" yaz

---

## Kritik Kurallar

- `game_platforms` yazarken: **canonical_game + platform_variants** modelini koru
- `primary_cover_url` → games tablosunda, platform cover'ı → game_platforms.cover_url
- `game_log` → kullanıcı işaretleme alanı, AI otomatik temizlemez (kullanıcı onayı şart)
- `migrations/` altındaki SQL'leri değiştirme — sadece yeni dosya ekle
- `legacy_tools/` dosyalarına dokunma

---

## DB Schema Özeti

| Tablo | Ne için |
|-------|---------|
| `games` | Ana oyun kaydı + IGDB canonical alanları |
| `game_platforms` | Platform varyantları (sistem, emülatör, cover, IGDB variant) |
| `game_genres` | Many-to-many oyun↔tür |
| `emulator_systems` | Many-to-many emülatör↔sistem |
| `systems` | PS2, GBA, GBC, N64... |
| `emulators` | AetherSX2, Dolphin, PPSSPP... |
| `genres` | Action, RPG, Platformer... |
| `series` | God of War, Zelda, Pokemon... |
| `notes` | Tips ve Request Tracker için |

**Yeni kolonlar (migration_v7):** `game_platforms.igdb_game_id`, `igdb_slug`, `igdb_url`, `igdb_rating`, `igdb_release_year`, `is_primary_variant`, `version_title`

---

## Aktif Sprint Hedefleri

1. `v_games_full` view standardizasyonu → tüm sayfalar bunu kullansın
2. IGDB data-first kapanış (eksik eşleşmeler)
3. Cleanup Workspace inline hızlı aksiyonlar
4. Co-op akışını ana Dashboard filtresinde birleştir
5. Artwork Manager
6. Session Log / Progress layer

---

## In Progress

> Buraya aktif görevleri yaz. Format: `- [ ] GÖREV — ajan: X — başlangıç: YYYY-MM-DD`

- [ ] Repo organizasyonu (migrations/, docs/ taşıma) — ajan: claude — 2026-05-11

---

## Done

> Format: `- [x] GÖREV — ajan: X — tarih: YYYY-MM-DD — not: kısa açıklama`

- [x] IGDB entegrasyonu (bulk match, 228 oyun) — ajan: codex — 2026-05-10
- [x] Library Dashboard yenileme (grid/list/table, filtreler, modal nav) — ajan: codex — 2026-05-10
- [x] GitHub Pages geçişi (Netlify kaldırıldı) — ajan: codex — 2026-05-10
- [x] migration_v7 (platform variant model) — ajan: codex — 2026-05-11
- [x] PR #3 merge (TEAM_HANDOFF ortak yapıya geçiş) — ajan: furkan — 2026-05-11
- [x] migrations/ klasörü, migrate_ HTML temizliği — ajan: claude — 2026-05-11
- [x] TEAM_HANDOFF protokol güçlendirmesi — ajan: claude — 2026-05-11

---

## Geçmiş Oturumlar

Detaylı handoff geçmişi için: `docs/TEAM_HANDOFF_ARCHIVE_2026-05-09.md`
