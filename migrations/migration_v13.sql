-- migration_v13.sql
-- 1. games tablosuna eksik indexler
-- 2. is_primary_variant NULL → false standardizasyonu
-- 3. 13 oyunda primary variant otomatik seç
-- 4. Duplicate oyun merge: FIFA Soccer 07, Pro Evolution Soccer 2013
-- 5. Metal Gear Solid GBC yanlış external_id temizliği

BEGIN;

-- ─── 1. INDEXLER ────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_games_external_id  ON public.games (external_id);
CREATE INDEX IF NOT EXISTS idx_games_series_id    ON public.games (series_id);
CREATE INDEX IF NOT EXISTS idx_games_play_status  ON public.games (play_status);

-- ─── 2. is_primary_variant NULL → false ─────────────────────────────────────
UPDATE public.game_platforms
SET is_primary_variant = false
WHERE is_primary_variant IS NULL;

-- ─── 3. Primary variant eksik oyunlara otomatik seç ─────────────────────────
-- Kural: igdb_game_id varsa onu, yoksa id sırasıyla ilkini seç
UPDATE public.game_platforms
SET is_primary_variant = true
WHERE id IN (
  SELECT DISTINCT ON (game_id) id
  FROM public.game_platforms
  WHERE game_id NOT IN (
    SELECT game_id FROM public.game_platforms WHERE is_primary_variant = true
  )
  ORDER BY game_id, igdb_game_id NULLS LAST, id
);

-- ─── 4a. FIFA Soccer 07 merge ────────────────────────────────────────────────
-- Tut:    d45d8210 (GameCube + PSP platformları, zaten primary_variant var)
-- Absorb: e3d0a58b (PS2 platformu buraya taşınacak)

-- Taşınacak platform tek oyunun primary'siydi; non-primary yap, sonra taşı
UPDATE public.game_platforms
SET is_primary_variant = false
WHERE game_id = 'e3d0a58b-443c-46fb-a74c-d88891362edf';

UPDATE public.game_platforms
SET game_id = 'd45d8210-080c-44af-8fb6-25a1fd1447ec'
WHERE game_id = 'e3d0a58b-443c-46fb-a74c-d88891362edf';

-- Absorb satırında kalan genre (d45d8210'da zaten var)
DELETE FROM public.game_genres
WHERE game_id = 'e3d0a58b-443c-46fb-a74c-d88891362edf';

DELETE FROM public.games
WHERE id = 'e3d0a58b-443c-46fb-a74c-d88891362edf';

-- ─── 4b. Pro Evolution Soccer 2013 merge ────────────────────────────────────
-- Tut:    2cb30de4 (PS2 platformu, zaten primary_variant var)
-- Absorb: ec1126f3 (PSP platformu buraya taşınacak)

UPDATE public.game_platforms
SET is_primary_variant = false
WHERE game_id = 'ec1126f3-1b01-4266-a703-45200eb0ed95';

UPDATE public.game_platforms
SET game_id = '2cb30de4-7dd5-4f11-a1c5-683dc8771693'
WHERE game_id = 'ec1126f3-1b01-4266-a703-45200eb0ed95';

DELETE FROM public.game_genres
WHERE game_id = 'ec1126f3-1b01-4266-a703-45200eb0ed95';

DELETE FROM public.games
WHERE id = 'ec1126f3-1b01-4266-a703-45200eb0ed95';

-- ─── 5. Metal Gear Solid GBC — yanlış external_id temizle ───────────────────
-- GBC satırı PS1'in IGDB verisini (id=375) kopyalamış
-- external_id, igdb_rating, igdb_url, igdb_synced_at temizle
-- → bir sonraki enrich pass'ta GBC'ye özgü doğru ID bulunacak
UPDATE public.games
SET
  external_id    = NULL,
  igdb_rating    = NULL,
  igdb_url       = NULL,
  igdb_synced_at = NULL
WHERE id = '1a520249-67b0-4d8f-a3ed-a6b02e798b93';

COMMIT;

-- ─── DOĞRULAMA ───────────────────────────────────────────────────────────────
SELECT title, COUNT(DISTINCT gp.id) AS variant_count,
  array_agg(sys.name ORDER BY sys.name) AS systems,
  bool_or(gp.is_primary_variant) AS has_primary
FROM games g
JOIN game_platforms gp ON gp.game_id = g.id
JOIN systems sys ON sys.id = gp.system_id
WHERE g.title IN ('FIFA Soccer 07','Pro Evolution Soccer 2013','Metal Gear Solid')
GROUP BY g.id, g.title
ORDER BY g.title;
