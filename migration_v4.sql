-- ============================================================
-- RETROID POCKET 5 — Migration v4
-- primary_cover_url kolonu + mevcut data doldurma
-- Supabase SQL Editor'de tümünü seç + Run
-- ============================================================

-- 1. games tablosuna primary_cover_url ekle
ALTER TABLE public.games
  ADD COLUMN IF NOT EXISTS primary_cover_url TEXT;

-- 2. Mevcut oyunların cover'larını doldur (game_platforms[0]'dan al)
UPDATE public.games g
SET primary_cover_url = (
  SELECT cover_url FROM public.game_platforms
  WHERE game_id = g.id AND cover_url IS NOT NULL AND cover_url != ''
  ORDER BY id
  LIMIT 1
)
WHERE g.primary_cover_url IS NULL;

-- 3. Doğrulama
SELECT title, primary_cover_url IS NOT NULL AS cover_var
FROM games ORDER BY title LIMIT 10;
