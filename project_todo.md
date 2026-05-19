# Retroid — Aktif Backlog

> Tamamlananlar bu dosyada tutulmaz — git log'da.
> Session başında: önce CURRENT_STATE.md, sonra burası.

---

## Phase 1 — Zemin (Şimdi)

- [ ] **migration_v16** — SS + RA kolonlarını ekle (Claude)
- [ ] **View güncelleme** — v_games_summary + v_games_full yeni kolonları expose etsin (Claude)
- [ ] **Video player placeholder** — Modal'a ss_video_norm_url için player ekle (Codex)
- [ ] **Wheel art desteği** — Grid kartında logo overlay (Codex)
- [ ] **Duplicate/platform görünüm** — Show All modu + game_id+platform_id modal kimliği (Codex)
- [ ] **base64 cover kararı** — Temizle mi Storage'a taşı mı? (Kullanıcı kararı)

## Phase 2 — SS Entegrasyonu

- [ ] **ss-enricher Edge Function** — isim araması → ss_id → tam veri → DB yaz (Claude)
- [ ] **321 oyun batch enrich** — SS'den tüm metadata + medya (Claude)
- [ ] **Storage kopyalama** — box-2D + wheel-hd → Supabase Storage (Claude)
- [ ] **Series eşleştirme** — SS familles → series tablosu (Claude)

## Phase 3 — RA Entegrasyonu

- [ ] **RA game ID eşleştirme** — completion API + SS ra_supported flag (Claude)
- [ ] **ra-sync Edge Function** — haftalık progress sync (Claude)
- [ ] **Achievement paneli** — Modal'a RA progress bar (Codex)

## Phase 4 — IGDB Kaldırma

- [ ] **Verify** — Tüm oyunlarda SS verisi tam mı? (Claude)
- [ ] **migration_v17** — IGDB kolonlarını drop et (Claude)
- [ ] **igdb-search decommission** — Function + secrets kaldır (Claude)

## Phase 5 — Polish

- [ ] **Achievement Tracker sayfası** — Retroid_Achievements.html (Codex)
- [ ] **RAWG discovery** — rawg-discover deploy/test (opsiyonel)

## Kararlar Bekliyor

- [ ] **base64 cover** — 60 platform satırı — temizle / Storage / bırak
- [ ] **Linear API key** — Revoke et, yenisini Supabase secret'a ekle (LINEAR_API_KEY)
