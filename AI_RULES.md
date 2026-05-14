# AI Ajan Çalışma Kuralları

> Claude · Codex App · Codex Web için bağlayıcı protokol.
> Bu dosya okunmadan yazma işlemi yapılmaz.

---

## Oturum Protokolü

### Başlarken — 3 Zorunlu Adım (sırayla)

```
1. git log --oneline -5          → son 5 commit'e bak, neler değişmiş
2. cat CURRENT_STATE.md          → DB + UI anlık durumu, açık görevler, bitti listesi
3. cat project_todo.md           → aktif backlog
```

**Sonra ve ancak sonra** ilgili dosyaya geç.

### Biterken — 3 Zorunlu Adım

```
1. CURRENT_STATE.md güncelle     → ne değişti, hangi açık sorunlar çözüldü/eklendi
2. project_todo.md güncelle      → tamamlanan görevi kaldır, yeni görev ekle
3. Commit at                     → ajan: claude — veya ajan: codex — prefix ile
```

### Diğer Ajana Brief Yapmadan Önce

```
1. CURRENT_STATE.md'deki "Bir Daha Analiz Etme" listesine bak
2. "UI Katmanı" veya "DB Katmanı" bölümünde ✓ işareti var mı kontrol et
3. Zaten yapılmışsa brief gönderme — sadece ihtiyaç duyduğun şeyi söyle
```

> Bugün yaşanan sorun: Claude `v_games_summary` geçişini Codex'ten istedi.
> Codex bunu commit 84c632b'de çoktan yapmıştı.
> CURRENT_STATE.md olsaydı bu 3 saniyede görülürdü.

---

## Sahiplik

| Alan | Sahip | Dosyalar |
|------|-------|----------|
| DB · migration · script · audit | **Claude** | `migrations/` `scripts/` `docs/` `supabase/` |
| HTML · UX · site davranışı | **Codex** | `*.html` `rp5_*.js` |
| Ortak | **İkisi** | `CURRENT_STATE.md` `project_todo.md` `AI_RULES.md` |

**Çakışma riski olan dosyalar:** `rp5_igdb.js`, `ARCHITECTURE.md`
→ Birinin dokunmadan önce diğerinin CURRENT_STATE'ini kontrol etmesi yeterli.

---

## DB Yazma Kuralları

### YAPMA
- `game_log` alanını kullanıcı onayı olmadan temizleme
- `rating` kolonunu yazma (kullanıcıya ayrılmış)
- Oyun DELETE yapma — kullanıcıya sor
- Mevcut migration SQL'ini değiştirme

### YAP
- Yeni migration için `migrations/migration_vN.sql` dosyası ekle (N = bir sonraki)
- `primary_cover_url` → games tablosuna
- `cover_url` → game_platforms tablosuna (platform bazlı)
- `is_primary_variant = true` → her oyunda en fazla bir platform

### Duplicate önleme
```
GET /rest/v1/games?title=ilike.*OYUN_ADI*&select=id,title
```
Benzer isim varsa kullanıcıya sor.

---

## Commit Formatı

```
ajan: claude — feat: kısa açıklama
ajan: codex — fix: kısa açıklama
```

---

## Dosya Dokunulmazlık

| Dosya / Klasör | Kural |
|----------------|-------|
| `migrations/` | Sadece yeni dosya ekle, mevcut SQL'e dokunma |
| `rp5_auth.js` | Değiştirmeden önce kullanıcıya sor |
| `rp5_igdb.js` | Değiştirmeden önce koordine et |
| `Retroid_Library_Dashboard.html` | Büyük değişiklik öncesi kullanıcıya sor |

---

## IGDB Yazma Kontratı

`game_platforms` yazarken:
- `igdb_game_id` → IGDB platform release ID
- `igdb_rating` → ham 0-100 değer (bölme/yuvarlama yapma)
- `igdb_url` → tam URL
- `is_primary_variant` → oyun başına tek true

`games` yazarken:
- `external_id` → IGDB canonical game ID
- `igdb_rating`, `igdb_url` → canonical fallback
- Mevcut değeri EZME — sadece NULL alanları doldur

---

## Push Öncesi Kontrol

```bash
git fetch origin
git log origin/main -3 --oneline   # başkası commit attı mı?
```

Attıysa önce pull/rebase yap.

---

## Çakışma Önleme

`CURRENT_STATE.md`'deki "Sahiplik" tablosuna bak.
Başka ajan aynı dosyada aktif çalışıyorsa — dur, kullanıcıya sor.
