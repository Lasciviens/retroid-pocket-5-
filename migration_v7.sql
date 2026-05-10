-- ============================================================
-- RETROID POCKET 5 — Migration v7
-- IGDB varyant modeline gecis taslagi
-- Bu migration HENUZ uygulanmadi.
-- Once mevcut canli schema ile reconcile et.
-- ============================================================

-- Amaç:
-- Ayni kutuphane oyununun farkli platformlardaki IGDB kimliklerini
-- duplicate yaratmadan game_platforms seviyesinde saklamak.

ALTER TABLE public.game_platforms
  ADD COLUMN IF NOT EXISTS igdb_game_id BIGINT,
  ADD COLUMN IF NOT EXISTS igdb_slug TEXT,
  ADD COLUMN IF NOT EXISTS igdb_url TEXT,
  ADD COLUMN IF NOT EXISTS igdb_rating NUMERIC(5,2),
  ADD COLUMN IF NOT EXISTS igdb_release_year INTEGER,
  ADD COLUMN IF NOT EXISTS igdb_first_release_date TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS version_title TEXT,
  ADD COLUMN IF NOT EXISTS is_primary_variant BOOLEAN DEFAULT FALSE;

CREATE INDEX IF NOT EXISTS idx_game_platforms_igdb_game_id
  ON public.game_platforms(igdb_game_id);

CREATE INDEX IF NOT EXISTS idx_game_platforms_game_system
  ON public.game_platforms(game_id, system_id);

CREATE UNIQUE INDEX IF NOT EXISTS uq_game_platforms_game_system
  ON public.game_platforms(game_id, system_id);

CREATE UNIQUE INDEX IF NOT EXISTS uq_game_platforms_primary_variant
  ON public.game_platforms(game_id)
  WHERE is_primary_variant = TRUE;

SELECT column_name
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'game_platforms'
  AND column_name IN (
    'igdb_game_id',
    'igdb_slug',
    'igdb_url',
    'igdb_rating',
    'igdb_release_year',
    'igdb_first_release_date',
    'version_title',
    'is_primary_variant'
  );
