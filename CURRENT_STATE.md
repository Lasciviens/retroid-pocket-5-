# Current State — Tek Yetkili Kaynak

> **Her session başında ilk okunan dosya bu.**
> Bir şey yapmadan önce burayı oku. Bir şey yaptıktan sonra burayı güncelle.
>
> Son güncelleme: 2026-05-14 · claude

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
| Varsayılan sıralama | IGDB rating — açık görev |
| Lightbox / zoom | Eklendi — commit 061b6c8 |

### UI Açık Sorunlar

- Default sort = IGDB rating (Library açılışında) — project_todo'da var
- Modal screenshot zoom + kapak zoom
- Cleanup Workspace inline quick aksiyonlar

---

## Son Session

**2026-05-14 — claude:**
- migration_v14: `v_games_summary` (payload −51%, 3.8× hızlı) + `v_games_cleanup`
- migration_v15: `v_games_audit` (18 kural, audit_score) + `v_game_platform_audit`
- `scripts/audit_report.py` + `scripts/audit_autofix.py` + `docs/audit_system.md`
- Repo koordinasyon sistemi: `CURRENT_STATE.md` + `AI_RULES.md` güncelleme + `project_todo.md` sadeleştirme

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

---

## Sıradaki Aksiyonlar

| Sahip | Aksiyon | Öncelik |
|-------|---------|---------|
| Kullanıcı | base64_cover kararı: temizle mi Storage'a taşı mı | Yüksek |
| Kullanıcı | `audit_autofix.py` için service-key sağla | Orta |
| Codex | Varsayılan sıralama = IGDB rating (Library açılışı) | Yüksek |
| Codex | Modal screenshot + kapak zoom | Orta |
| Claude | `audit_autofix.py --apply` (service-key gelince) | Orta |
| Claude | IGDB enrich — `never_synced` 37 oyun için stamp | Düşük |
