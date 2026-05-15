# Retroid — Aktif Backlog

> Tamamlananlar bu dosyada tutulmaz — git log'da.
> Session başında: önce `CURRENT_STATE.md`, sonra burası.

---

## Yüksek Öncelik

- [ ] **RAWG entegrasyonu — Faz 1** — RAWG API key alındı; key GitHub'a yazılmayacak. `RAWG_API_KEY` Supabase secret olarak set edilecek, `rawg-discover` deploy/test edilecek, Library modalına canlı RAWG Discovery paneli eklenecek.
- [ ] **DB-backed Library search** — `v_games_summary` için search_text / acronym / alias stratejisi. Hardcode yok, UI hack yok.
- [ ] **base64_cover kararı** — 60 platform satırında base64 JPEG var; temizle mi Storage'a taşı mı? (kullanıcı kararı)
- [ ] **audit_autofix apply** — service-key gelince `scripts/audit_autofix.py --apply` çalıştır (37 never_synced stamp)
- [ ] **Platformsuz 14 oyun** — game_platforms kaydı eklenmeli (Sonic Riders, Fable Anniversary vb.)

---

## Orta Öncelik

- [ ] **Cleanup Workspace inline aksiyonlar** — hızlı edit / enrich butonu (faz 2)
- [ ] **Bridge üzerinden kontrollü eşleştirme** — mevcut oyunları IGDB ile küçük partiler halinde eşleştir
- [ ] **IGDB enrich extended pass** — keywords / screenshots / themes / age_rating / rating_count / multiplayer_info
- [ ] **Session Log** — `session_logs(game_id, date, duration_minutes, note)` yeni tablo
- [ ] **RetroAchievements entegrasyonu** — user progress proxy + modal enrichment
- [ ] **SteamGridDB entegrasyonu** — alternatif kapak önerileri
- [ ] **Artwork Manager** — IGDB / libretro / SteamGridDB arasında kapak seçimi

---

## Düşük Öncelik / İleride

- [ ] **Discovery Shelf** — akıllı oyun önerileri (RAWG Faz 1 sonrası genişletilecek)
- [ ] **Quick Start Guide** — RP5 gelince ilk akşam 3 saatlik plan
- [ ] **Achievement / Missable Tips** — "şunu kaçırma" notları
- [ ] **Donanım kıyaslama** — RP5 vs Switch vs Steam Deck
- [ ] **Glossary genişletme** — PGXP, HLE/LLE, Frame Pacing, Vulkan, Netplay

---

## Sprint Aktif

- [ ] RAWG Faz 1: secret set → function deploy/test → Library modal canlı discovery paneli
- [ ] IGDB data-first kapanış kontrol listesini tamamla
- [ ] Cleanup Workspace inline quick aksiyon kapsamını tanımla
