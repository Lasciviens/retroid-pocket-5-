# AI Ajan Çalışma Kuralları

> Bu dosya okunmadan hiçbir yazma işlemi yapılmaz.
> Claude · Codex App · Codex Web için bağlayıcı kurallar.

---

## 1. Başlamadan Önce Oku

Her oturumda bu sırayla oku:
1. `project_todo.md` — aktif backlog
2. `ARCHITECTURE.md` — schema ve dosya yapısı
3. `README.md` — canlı ürün ve giriş noktaları

---

## 2. DB Yazma Kuralları (EN KRİTİK)

### YAPMA:
- `game_log` alanını kullanıcı onayı olmadan temizleme
- `rating` kolonunu yazma (kullanıcı kendi puanı için ayrılmış, şu an NULL)
- Mevcut oyunu DELETE yapma — önce kullanıcıya sor
- `migrations/` klasöründeki SQL'leri değiştirme

### YAP:
- Yeni oyun eklerken `game_log = 'PNG eklenecek'` yaz (kapak yoksa)
- `primary_cover_url` → games tablosuna yaz
- `cover_url` → game_platforms tablosuna yaz (platform bazlı)
- `is_primary_variant = true` → önerilen platformu işaretle

### Duplicate önleme:
Oyun eklemeden önce kontrol et:
```python
# Supabase REST
GET /rest/v1/games?title=ilike.*OYUN_ADI*&select=id,title
```
Benzer isim varsa kullanıcıya sor, otomatik ekleme.

---

## 3. Commit Mesajı Formatı

```
ajan: claude — feat: kısa açıklama
ajan: codex-app — fix: kısa açıklama
ajan: codex-web — docs: kısa açıklama
```

Görev durumu `project_todo.md` içinde takip edilir.

---

## 4. Dosya Dokunulmazlık Kuralları

| Klasör/Dosya | Kural |
|---|---|
| `migrations/` | SADECE yeni dosya ekle, mevcut SQL'e dokunma |
| `project_todo.md` | Tamamladığın görevi done'a taşı |
| `rp5_auth.js` | Değiştirmeden önce kullanıcıya sor |
| `rp5_igdb.js` | Değiştirmeden önce kullanıcıya sor |

---

## 5. IGDB Yazma Kontratı

`game_platforms` tablosuna IGDB verisi yazarken canonical model:
- `igdb_game_id` → IGDB platform release ID
- `igdb_rating` → ham 0-100 değer (bölme/yuvarlama yapma, olduğu gibi yaz)
- `igdb_url` → tam IGDB URL
- `is_primary_variant` → sadece bir platform true olabilir

`games` tablosunda:
- `external_id` → IGDB canonical game ID
- `igdb_rating`, `igdb_url` → canonical fallback (platform eşleşmesi yoksa)

---

## 6. HTML Değiştirme Kuralları

- Mevcut çalışan bir özelliği kaldırmadan önce `project_todo.md` notlarını kontrol et
- `Retroid_Library_Dashboard.html` kritik dosya — büyük değişiklik öncesi kullanıcıya sor
- `index.html`'e yeni sayfa eklerken mevcut kartları bozmadığından emin ol

---

## 7. Çakışma Önleme

`project_todo.md` içindeki aktif maddelere bak.
Başka bir ajan aynı alan üzerinde çalışıyorsa dokunma — kullanıcıya sor.

Commit atmadan önce:
```bash
git fetch origin
git log origin/main -3 --oneline  # Son 3 commiti gör
```
Başkası commit attıysa önce pull/rebase yap.
