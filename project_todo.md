# 🗺️ Retroid Pocket 5 — Proje To-Do Listesi

Her session başında bu dosyayı okuyorum. Yeni görev eklemek için buraya yaz.

---

## 🔴 Öncelikli (High Priority)

- [ ] **IGDB data-first akisi** — Canli sort yerine DB'ye kaydedilmis IGDB metadata kullan. Karar kaydi: `IGDB_DATA_PLAN.md`
- [ ] **Bridge uzerinden kontrollu eslestirme turu** — mevcut DB oyunlarini tek tek veya kucuk partilerle eslestir
- [x] **migration_v6.sql uygulandi** — storyline, publisher, igdb_url, igdb_rating, igdb_synced_at canli DB'de mevcut
- [ ] **Toplu IGDB audit araci** — eslesmeyen / dusuk skorlu / eksik metadata kayitlarini listele
- [ ] **IGDB enrich pass** — `scripts/igdb_enrich_missing.py` ile dry-run -> hedefli apply -> tam apply akisini tamamla
- [ ] **Schema degerlendirmesi** — screenshots, videos, websites, publisher gibi alanlar icin yeni kolon veya iliski gerekirse planla
- [x] **IGDB varyant modeli** — ayni isim/farkli platform oyunlari icin `migration_v7.sql` mantigina gecis
- [x] **IGDB normalize write flow** — import oncesi `canonical_game + platform_variants` formatina oturt
- [ ] **RetroAchievements entegrasyonu** — user progress / completion / game progress proxy + modal enrichment
- [ ] **SteamGridDB entegrasyonu** — alternatif kapak / hero / logo onerileri
- [ ] **RAWG discovery entegrasyonu** — benzer oyunlar / dis linkler / discovery katmani
- [ ] **Cleanup Workspace** — admin icin yogun metadata denetim gorunumu (ilk ekran tamam, sonraki adim inline hizli aksiyonlar)
- [ ] **Artwork Manager** — IGDB / libretro / SteamGridDB kaynaklari arasinda kapak secimi
- [ ] **Discovery Shelf** — kutuphaneden secilmis akilli oneriler



- [ ] **Library bulk cleanup görünümü** — özellikle eşleşmemiş / metadata eksiği olan oyunlar için daha yoğun admin görünümü (ilk faz: grid/list/table + gap filtreleri tamam)
- [ ] **ROM klasör yapısını hazırla** — `ROM_Folder_Guide.md` dosyası oluşturuldu (bkz. aşağı). Dashboard'da her oyunun hangi klasöre gideceği görünmeli.

---

## 🟡 Orta Öncelik

- [ ] **Session Log** — Oyun başına "ne zaman oynadım, kaç saat" günlüğü. Yeni tablo: `session_logs(game_id, date, duration_minutes, note)`.


- [ ] **Dashboard'a "ROM Durumu" kolonu ekle** — Her oyun için: `[ ] Bulunamadı`, `[~] Aranıyor`, `[✓] Hazır` gibi bir status.
- [ ] **Quick Start Guide** — RP5 geldiğinde eşiyle ilk akşam 3 saatlik oyun planı.
- [ ] **Achievement / Missable Tips** — Her oyun için "şunu kaçırma" notu. Zelda, Pokemon, RPG'ler için kritik.

---

## 🟢 İleride / Nice to Have

- [ ] **Top 10 "ölmeden önce oyna" listesi** — Furkan'ın kütüphanesinden seçilmiş elit 10.
- [ ] **Donanım kıyaslama tablosu** — RP5 vs Switch vs Steam Deck vs Odin 2.
- [ ] **Shader / CRT filter rehberi** — Glossary'e eklenecek terimler: Shader, CRT, Scanline.
- [ ] **Glossary genişletme** — Sıradaki terimler: PGXP, HLE/LLE, Frame Pacing, Vsync, Texture Pack, Netplay, Vulkan, Adreno GPU, Snapdragon 865.
- [ ] **Series Roadmap'e "oynadım" takibi ekle** — Şu an sadece liste, interaktif olmayabilir.

---


## 🤝 Multi-Agent Calisma Kurali (Claude + Codex App + Codex Web)

- [x] Ortak handoff dosyasi: `TEAM_HANDOFF.md`
- [ ] Sprint 1: `v_games_full` gecis planini cikart
- [ ] Sprint 1: IGDB data-first kapanis kontrol listesini tamamla
- [ ] Sprint 1: Cleanup Workspace inline hizli aksiyonlarini tanimla
- [ ] Sprint 2: Co-op akisini ana Dashboard filtresinde birlestir
- [ ] Sprint 3: Artwork Manager ve Session Log kapsam taslagi

---

## ✅ Tamamlananlar

- [x] Ana kütüphane Dashboard'u (95+ oyun, boxart, filtre, arama)
- [x] Dashboard'a release year eklendi
- [x] Dashboard'a sorting eklendi (A-Z, yıl, rating, IGDB rating)
- [x] Kütüphane için grid / liste / tablo görünümü eklendi
- [x] Kütüphaneye metadata gap filtreleri eklendi (IGDB / kapak / ozet / yil eksik)
- [x] Cleanup Workspace sayfasi eklendi
- [x] Co-op Dashboard (19 oyun, rastgele öneri)
- [x] Series Roadmap (10 seri, timeline)
- [x] Emülatör Matrix (17 sistem, deep-dive notlar)
- [x] Glossary (12 terim, yazılımcı mantığıyla)
- [x] game_wishlist.md sistemi kuruldu
- [x] ROM klasör yapısı rehberi oluşturuldu
- [x] IGDB Bridge iskeleti kuruldu (proxy-ready arama yüzeyi + kutuphaneden kopru)
- [x] Supabase Edge Function IGDB proxy scaffold eklendi
- [x] IGDB link import + aday ekleme + mevcut oyun eslestirme akisi kuruldu
- [x] `migration_v7.sql` canli schema ile uzlastirildi ve uygulandi
- [x] Bridge ve bulk import canonical + platform_variants modeline gecirildi
- [x] Yeni entegrasyonlar icin roadmap ve function scaffold'lari eklendi
- [x] Dis referanslardan urun fikirleri derlendi (`PRODUCT_IDEAS_FROM_REFERENCES.md`)
- [x] IGDB import playbook ve field map hazirlandi

---

## 📝 Notlar

- Dashboard'a her yeni özellik eklenirken tüm dosyalar çapraz-link kontrolü yapılmalı.
- `game_wishlist.md` = yeni oyun eklemek için. Bu dosya = geliştirme fikirleri için.
