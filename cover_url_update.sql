-- ============================================================
-- COVER URL GÜNCELLEME REHBERİ
-- Supabase SQL Editor'de kullan
-- ============================================================

-- ── Cover URL neden tek yerde? ────────────────────────────
-- Cover, game_platforms tablosunda tutuluyor çünkü:
-- Bir oyunun PS2 ve PSP versiyonları farklı kapak görseline sahip.
-- games tablosunda cover yok — orada görüyorsan bir view'den geliyor.
-- Doğru yer: game_platforms.cover_url (platform başına bir tane)
-- ─────────────────────────────────────────────────────────

-- ── 1. Hangi oyunda hangi cover var? (önce bak) ──────────
SELECT
  g.title,
  sys.name AS system,
  gp.cover_url,
  gp.id AS platform_id
FROM game_platforms gp
JOIN games g   ON g.id  = gp.game_id
JOIN systems sys ON sys.id = gp.system_id
WHERE g.title ILIKE '%buraya oyun adini yaz%'
ORDER BY g.title, sys.name;


-- ── 2. Tek bir platform'un cover'ını güncelle ────────────
-- platform_id'yi yukarıdaki sorgudan al
UPDATE game_platforms
SET cover_url = 'https://...'         -- yeni URL buraya
WHERE id = 'buraya-platform-id-uuid';


-- ── 3. Bir oyunun TÜM platformlarının cover'ını güncelle ─
-- Aynı oyun birden fazla sistemde varsa ama aynı kapak kullanılacaksa:
UPDATE game_platforms
SET cover_url = 'https://...'
WHERE game_id = (
  SELECT id FROM games WHERE title = 'Buraya Tam Oyun Adı'
);


-- ── 4. Hızlı arama — cover'ı eksik olan oyunlar ─────────
SELECT
  g.title,
  sys.name AS system,
  gp.id AS platform_id
FROM game_platforms gp
JOIN games g   ON g.id  = gp.game_id
JOIN systems sys ON sys.id = gp.system_id
WHERE gp.cover_url IS NULL OR gp.cover_url = ''
ORDER BY g.title;


-- ── 5. Tüm oyunların cover durumu (genel bakış) ──────────
SELECT
  g.title,
  COUNT(gp.id) AS platform_sayisi,
  SUM(CASE WHEN gp.cover_url IS NOT NULL AND gp.cover_url != '' THEN 1 ELSE 0 END) AS cover_olan,
  SUM(CASE WHEN gp.cover_url IS NULL OR gp.cover_url = '' THEN 1 ELSE 0 END) AS cover_eksik
FROM games g
LEFT JOIN game_platforms gp ON gp.game_id = g.id
GROUP BY g.title
ORDER BY cover_eksik DESC, g.title;
