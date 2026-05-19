# Current State — Tek Yetkili Kaynak

> Her session başında ilk okunan dosya bu.
> Son güncelleme: 2026-05-19 · codex

---

## Sahiplik

| Alan | Sahip | Dosyalar |
|------|-------|----------|
| DB · migration · script · data | **Claude** | `migrations/` `scripts/` `docs/` `supabase/` |
| HTML · UX · site davranışı | **Codex** | `*.html` `rp5_*.js` |
| Paylaşımlı | **İkisi** | `CURRENT_STATE.md` `project_todo.md` `AI_RULES.md` |

---

## DB Katmanı — Anlık Durum

| Öğe | Durum |
|-----|-------|
| Aktif şema | migration_v15 (son) |
| Oyun sayısı | 321 |
| Ortalama audit skoru | 95.2 / 100 |
| Primary variant kapsamı | %100 |

### Aktif View'lar
| View | Kullanım |
|------|---------|
| `v_games_summary` | Library grid/list — hafif, hızlı |
| `v_games_full` | Modal detay — tam veri |
| `v_games_cleanup` | Admin anomaly özeti |
| `v_games_audit` | 18 kural, 0-100 audit score |
| `v_game_platform_audit` | Platform bazlı audit |

### Açık DB Sorunlar
| Sorun | Sayı |
|-------|------|
| base64 cover_url | 60 platform satırı — kullanıcı kararı bekliyor |
| no_primary_variant | 14 oyun |
| no_external_id | 5 oyun |
| never_synced | 37 oyun |

---

## Entegrasyon Durumları

| Entegrasyon | Durum | Not |
|-------------|-------|-----|
| ScreenScraper | ✅ Hazır | devid alındı, isim araması test edildi ve çalışıyor |
| RetroAchievements | ✅ Deploy edildi | retroachievements-player function aktif |
| IGDB | ⚠️ Legacy fallback | SS tam çalışınca kademeli kalkacak; şimdilik kırmadan korunacak |
| RAWG | ⏸ Beklemede | rawg-discover var ama deploy edilmedi |
| Linear | ✅ Aktif | Proje yönetim aracı, MCP üzerinden bağlı |

---

## ScreenScraper — Teknik Detaylar

**Yöntem:** isim + SS sistem ID → `jeuRecherche` → ss_id → `jeuInfos` → tam veri

**SS Sistem ID Mapping:**
| DB system_id | Platform | SS system_id |
|---|---|---|
| 1 | PS1 | 57 |
| 2 | PS2 | 58 |
| 3 | PSP | 61 |
| 4 | GBA | 24 |
| 5 | DS | 78 |
| 6 | 3DS | 17 |
| 7 | N64 | 14 |
| 8 | GameCube | 13 |
| 9 | Wii | 16 |
| 10 | SNES | 4 |
| 11 | NES | 3 |
| 12 | Genesis | 1 |
| 13 | Dreamcast | 23 |
| 16 | GBC | 29 |

**Çekilecek medya tipleri:** box-2D (us bölgesi), wheel-hd, ss (screenshot), video-normalized, fanart

**Medya URL güvenlik notu:** SS medya URL'lerinde devpassword görünüyor.
Public view veya HTML'e credential içeren SS URL'i çıkmayacak. Storage'a kopyalanacak: box-2D, wheel-hd. Screenshot/video/fanart için ya Storage kopyası ya da auth/proxy gerekir; public-safe URL yoksa UI placeholder gösterecek.

**Test sonucu:** God of War II (PS2) — exact match, rating 90/100, tüm medya geldi ✅

**Plan dokümanları:**
- `SCREENSCRAPER_MIGRATION_PLAN.md` — SS'e geçiş ve IGDB'den kademeli çıkış planı
- `CLAUDE_SUPABASE_SS_PROMPT.md` — Claude'a verilecek migration/function prompt'u

---

## UI Katmanı — Anlık Durum

| Öğe | Durum |
|-----|-------|
| Library endpoint | `v_games_summary` ✓ |
| Modal endpoint | `v_games_full` ✓ |
| Varsayılan sıralama | IGDB rating ✓ |
| Lightbox / zoom | Cover + screenshot ✓ |
| Video player | Henüz yok — Phase 1 |
| Wheel art desteği | Henüz yok — Phase 1 |
| Duplicate/platform görünüm | Henüz yok — Phase 1 |

---

## Son Session — 2026-05-19 — claude

- ScreenScraper devid alındı, Supabase secret'a eklendi
- SS API test edildi: isim araması çalışıyor (God of War II exact match)
- retroachievements-player Edge Function deploy edildi ve test edildi
- Linear workspace kuruldu: 21 issue, 14 label, 1 proje
- ss-test Edge Function deploy edildi (geçici test aracı)
- Sistem analizi PDF + Excel hazırlandı

---

## Sıradaki Aksiyonlar

| Sahip | Aksiyon | Öncelik |
|-------|---------|---------|
| Claude | migration_v16 yaz ve deploy et | Yüksek |
| Claude | v_games_summary + v_games_full view'larını güncelle | Yüksek |
| Claude | ss-enricher Edge Function yaz | Yüksek |
| Codex | Modal'a video player + wheel art ekle | Orta |
| Codex | Library duplicate/platform görünüm mantığı | Orta |
| Codex | IGDB etiketlerini metadata-provider nötr hale getir | Orta |
| Kullanıcı | base64_cover kararı: temizle mi Storage'a taşı mı | Yüksek |
| Kullanıcı | Linear API key'ini revoke et, yenisini Supabase secret'a ekle | Yüksek |

---

## Bir Daha Analiz Etme — Bunlar Bitti

| Konu | Referans |
|------|----------|
| developer kolonu kaldırma | migration_v12 |
| Library v_games_summary geçişi | commit 84c632b |
| Primary variant kapsamı | migration_v13 |
| Modal lightbox + galeri gezinme | commit 1a0ec5a |
| Koordinasyon OS kurulumu | commit 27a84d1 |
| SS API test + devid | 2026-05-19 |
| RA function deploy | 2026-05-19 |
| SS migration hazırlık planı | `SCREENSCRAPER_MIGRATION_PLAN.md` |
