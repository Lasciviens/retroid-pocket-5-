# Current State — Tek Yetkili Kaynak

> **Her session başında ilk okunan dosya bu.**
> Bir şey yapmadan önce burayı oku. Bir şey yaptıktan sonra burayı güncelle.
>
> Son güncelleme: 2026-05-15 · chatgpt (Pages redeploy tetiklendi)

---

## Sahiplik

| Alan | Sahip | Dosyalar |
|------|-------|----------|
| DB · migration · script · data audit | **Claude** | `migrations/` `scripts/` `docs/` `supabase/` |
| HTML · UX · site davranışı · canlı doğrulama | **Codex** | `*.html` `rp5_*.js` |
| Paylaşımlı | **İkisi** | `CURRENT_STATE.md` `project_todo.md` `AI_RULES.md` |

**Çakışma riski:** `rp5_igdb.js`, `ARCHITECTURE.md` — dokunmadan önce koordine et.

---

## DB Katmanı — Anlık Durum

| Öğe | Durum |
|-----|-------|
| Aktif şema | migration_v15 (son) |
| Canlı view'lar | `v_games_summary` · `v_games_full` · `v_games_cleanup` · `v_games_audit` · `v_game_platform_audit` |
| Oyun sayısı | 321 |
| Ortalama audit skoru | 95.2 / 100 |
| `developer` kolonu | KALDIRILDI (migration_v12) — geri getirme |
| Primary variant kapsamı | %100 (platform kaydı olan oyunlarda) |
| Auto-fix pipeline | `scripts/audit_autofix.py` hazır — apply için service-key gerekli |

### DB Açık Sorunlar

| Sorun | Sayı | Durum |
|-------|------|-------|
| base64 cover_url (platform satırı) | 60 | Kullanıcı kararı bekliyor: temizle vs Storage'a taşı |
| `no_primary_variant` (platformsuz oyun) | 14 | Manuel — önce game_platforms ekle |
| `no_external_id` (IGDB eşleşmesi yok) | 5 | `igdb_bulk_match.py` ile bulunabilir |
| `no_storyline` | 159 | IGDB'de gerçekten yok — otomatik çözülmez |
| `never_synced` | 37 | `audit_autofix.py --apply` ile stamp basılabilir |

---

## UI Katmanı — Anlık Durum

| Öğe | Durum |
|-----|-------|
| Library liste endpoint | `v_games_summary` ✓ — commit 84c632b |
| Modal detay endpoint | `v_games_full?id=eq.{id}` ✓ |
| Cleanup Workspace | `v_games_audit` ✓ — rp5_igdb.js:209-210 |
| IGDB Bridge | `v_games_summary` + `v_games_audit` ✓ |
| Varsayılan sıralama | IGDB rating ✓ — commit 061b6c8 |
| Lightbox / zoom | Cover + screenshot zoom ✓ — commit d19509d |
| Lightbox galeri gezinmesi | Sağ/sol buton + klavye ✓ — commit 1a0ec5a |
| GitHub Pages | Repo public'e döndü; redeploy commit'i tetiklendi |

### UI Açık Sorunlar

- Library araması hâlâ DB-backed değil; hardcoded alias geri alındı, doğru çözüm Claude tarafında search/view stratejisi
- Cleanup Workspace inline quick aksiyonlar
- RAWG Faz 1: secret set + function deploy/test + Library modal canlı discovery paneli

---

## Son Session

**2026-05-15 — chatgpt:**
- RAWG API key alındı; key repo dosyalarına yazılmadı, secret olarak set edilmesi gerekiyor
- `project_todo.md`: RAWG Faz 1 yüksek önceliğe alındı
- Repo private/public geçişinden sonra GitHub Pages redeploy tetiklemek için bu commit atıldı

**2026-05-14 — claude:**
- migration_v14: `v_games_summary` (payload −51%, 3.8× hızlı) + `v_games_cleanup`
- migration_v15: `v_games_audit` (18 kural, audit_score) + `v_game_platform_audit`
- `scripts/audit_report.py` + `scripts/audit_autofix.py` + `docs/audit_system.md`
- Repo koordinasyon sistemi: `CURRENT_STATE.md` + `AI_RULES.md` güncelleme + `project_todo.md` sadeleştirme
- commit `27a84d1`: koordinasyon OS + `audit_autofix.py` GitHub'a alındı

**2026-05-14 — codex:**
- commit `061b6c8`: default sort = IGDB rating + modal lightbox ilk sürüm
- commit `d19509d`: modal cover/screenshot zoom güvenilir hale getirildi
- commit `1a0ec5a`: lightbox galeri büyütüldü, sağ/sol gezinme eklendi, mobil/desktop davranışı iyileştirildi
- Library search için yanlış hardcoded alias geçici çözümü geri alındı; arama artık yine yalnız mevcut DB summary alanlarına dayanıyor

---

## Bir Daha Analiz Etme — Bunlar Bitti

| Konu | Durum | Referans |
|------|-------|----------|
| `developer` kolonu kaldırma | ✅ BITTI | migration_v12 + tüm scriptler |
| Library `v_games_summary` geçişi | ✅ BITTI | Codex — commit 84c632b |
| `v_games_audit` Cleanup'a entegrasyon | ✅ BITTI | Codex — rp5_igdb.js:209 |
| Primary variant kapsamı | ✅ BITTI | migration_v13 |
| FIFA 07 + PES 2013 duplicate merge | ✅ BITTI | migration_v13 |
| Metal Gear Solid GBC yanlış external_id | ✅ BITTI | migration_v13 |
| Modal lazy-load (DB-first, live IGDB ikincil) | ✅ BITTI | Codex — commit 16e134e |
| Varsayılan sıralama = IGDB rating | ✅ BITTI | Codex — commit 061b6c8 |
| Modal cover + screenshot zoom | ✅ BITTI | Codex — commit d19509d |
| Modal galeri sağ/sol gezinme | ✅ BITTI | Codex — commit 1a0ec5a |
| Koordinasyon OS (CURRENT_STATE + AI_RULES protokolü) | ✅ BITTI | Claude — commit 27a84d1 |

---

## Sıradaki Aksiyonlar

| Sahip | Aksiyon | Öncelik |
|-------|---------|---------|
| Kullanıcı | RAWG key'i Supabase secret olarak set et: `RAWG_API_KEY` | Yüksek |
| Claude/Codex | `rawg-discover` deploy/test + Library modal RAWG Discovery paneli | Yüksek |
| Kullanıcı | base64_cover kararı: temizle mi Storage'a taşı mı | Yüksek |
| Kullanıcı | `audit_autofix.py` için service-key sağla | Orta |
| Claude | Library aramasını DB-backed hale getir: `v_games_summary` için search_text / acronym / alias stratejisi, hardcode yok | Yüksek |
| Codex | Cleanup Workspace inline quick aksiyonlarını tasarla/uygula | Orta |
| Claude | `audit_autofix.py --apply` (service-key gelince) | Orta |
| Claude | IGDB enrich — `never_synced` 37 oyun için stamp | Düşük |
