# 🗺️ Retroid Pocket 5 — Proje To-Do Listesi

Her session başında bu dosyayı okuyorum. Yeni görev eklemek için buraya yaz.

---

## 🔴 Öncelikli (High Priority)

- [ ] **IGDB proxy + DB sync** — Bridge ve Supabase function scaffold hazir. Sonraki adim Twitch/IGDB Client ID + Secret ile proxy deployment, sonra alan bazli DB esleme.



- [ ] **Dashboard'a release year ekle** — Her oyuna `releaseYear` variable'ı eklenmeli. Sorting için gerekli. (Furkan isteği: 2026-05-01)
- [ ] **Dashboard'a sorting ekle** — Release year, alfabetik, sistem, rating bazlı sıralama. releaseYear variable olmadan yapılamaz, önce o.
- [ ] **ROM klasör yapısını hazırla** — `ROM_Folder_Guide.md` dosyası oluşturuldu (bkz. aşağı). Dashboard'da her oyunun hangi klasöre gideceği görünmeli.

---

## 🟡 Orta Öncelik

- [ ] **Session Log** — Oyun başına "ne zaman oynadım, kaç saat" günlüğü. Yeni tablo: `session_logs(game_id, date, duration_minutes, note)`.


- [ ] **Dashboard'a "ROM Durumu" kolonu ekle** — Her oyun için: `[ ] Bulunamadı`, `[~] Aranıyor`, `[✓] Hazır` gibi bir status.
- [ ] **Co-op Dashboard'u co-op filter olarak ana Dashboard'a entegre et** — Şu an ayrı dosya, birleştirilebilir.
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

## ✅ Tamamlananlar

- [x] Ana kütüphane Dashboard'u (95+ oyun, boxart, filtre, arama)
- [x] Co-op Dashboard (19 oyun, rastgele öneri)
- [x] Series Roadmap (10 seri, timeline)
- [x] Emülatör Matrix (17 sistem, deep-dive notlar)
- [x] Glossary (12 terim, yazılımcı mantığıyla)
- [x] game_wishlist.md sistemi kuruldu
- [x] ROM klasör yapısı rehberi oluşturuldu
- [x] IGDB Bridge iskeleti kuruldu (proxy-ready arama yüzeyi + kutuphaneden kopru)
- [x] Supabase Edge Function IGDB proxy scaffold eklendi

---

## 📝 Notlar

- Dashboard'a her yeni özellik eklenirken tüm dosyalar çapraz-link kontrolü yapılmalı.
- `game_wishlist.md` = yeni oyun eklemek için. Bu dosya = geliştirme fikirleri için.
