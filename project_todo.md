# Retroid — Aktif Backlog

> Tamamlananlar bu dosyada tutulmaz — git log'da.
> Session başında: önce CURRENT_STATE.md, sonra burası.

---

## Phase 1 — Zemin (Şimdi)

- [ ] **Secret rotasyonu** — İfşa olmuş GitHub/Linear/API key'leri revoke et; yeni key'leri sadece Supabase secret olarak tut (Kullanıcı)
- [ ] **migration_v16** — SS + RA kolonlarını ekle (Claude)
- [ ] **View güncelleme** — v_games_summary + v_games_full yeni kolonları expose etsin (Claude)
- [ ] **Audit güncelleme** — IGDB eksik flag'leri SS varlığını metadata match kabul etsin (Claude)
- [ ] **Video player placeholder** — Modal'a public-safe `ss_video_url` için player ekle; URL yoksa screenshot/box fallback göster (Codex)
- [ ] **Wheel art desteği** — Grid kartında logo overlay (Codex)
- [ ] **Duplicate/platform görünüm** — Show All modu + game_id+platform_id modal kimliği (Codex)
- [ ] **Metadata provider UI** — IGDB etiketlerini SS/IGDB/manual provider mantığına çevir (Codex)
- [ ] **Web UI uygulama planı** — `SCREENSCRAPER_WEB_UI_PLAN.md` sırasıyla Library/Cleanup/secondary pages hazırlığı (Codex)
- [ ] **base64 cover kararı** — Temizle mi Storage'a taşı mı? (Kullanıcı kararı)

## Phase 2 — SS Entegrasyonu

- [ ] **ss-enricher Edge Function** — isim araması → ss_id → tam veri → DB yaz (Claude)
- [ ] **SS media security** — credential içeren SS source URL'leri public view'a çıkarma; public URL sadece Storage/proxy olsun (Claude)
- [ ] **321 oyun batch enrich** — SS'den tüm metadata + medya (Claude)
- [ ] **Storage kopyalama** — box-2D + wheel-hd → Supabase Storage (Claude)
- [ ] **Series eşleştirme** — SS familles → series tablosu (Claude)

## Phase 3 — RA Entegrasyonu

- [ ] **RA game ID eşleştirme** — completion API + SS ra_supported flag (Claude)
- [ ] **ra-sync Edge Function** — haftalık progress sync (Claude)
- [ ] **Achievement paneli** — Modal'a RA progress bar (Codex)

## Phase 4 — IGDB Kaldırma

- [ ] **Verify** — Tüm oyunlarda SS verisi tam mı? (Claude)
- [ ] **IGDB freeze** — Yeni IGDB enrich/import workflow'larını durdur; sadece fallback olarak kalsın (Claude)
- [ ] **IGDB UI legacy** — IGDB Bridge linkini legacy olarak işaretle veya ana nav'dan indir (Codex)
- [ ] **migration_v17+** — SS coverage doğrulandıktan sonra IGDB kolonlarını drop/archive et (Claude)
- [ ] **igdb-search decommission** — Function + secrets kaldır (Claude)

## Phase 5 — Polish

- [ ] **Achievement Tracker sayfası** — Retroid_Achievements.html (Codex)
- [ ] **RAWG discovery** — rawg-discover deploy/test (opsiyonel)

## Kararlar Bekliyor

- [ ] **base64 cover** — 60 platform satırı — temizle / Storage / bırak
- [ ] **Linear API key** — Revoke et, yenisini Supabase secret'a ekle (LINEAR_API_KEY)
- [ ] **Video/screenshot/fanart policy** — Storage'a mı kopyalanacak, yoksa auth/proxy ile mi sunulacak?

## Plan Referansları

- `SCREENSCRAPER_MIGRATION_PLAN.md` — ana geçiş planı
- `CLAUDE_SUPABASE_SS_PROMPT.md` — Claude'a verilecek Supabase prompt'u
- `SCREENSCRAPER_WEB_UI_PLAN.md` — Codex web/UI uygulama planı
