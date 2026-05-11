-- ============================================================
-- RETROID POCKET 5 — Migration v7
-- IGDB canonical + platform variant model
-- Canli schema ile uzlastirilmis surum
-- ============================================================

-- Amaç:
-- 1. games tablosundaki mevcut IGDB alanlarini canonical fallback olarak korumak
-- 2. platform varyantina ait IGDB kimligini game_platforms seviyesine indirmek
-- 3. ayni isim / farkli platform oyunlarini duplicate etmeden yonetmek

-- ------------------------------------------------------------
-- 1) Canonical oyun metadata kolonlari
-- ------------------------------------------------------------
ALTER TABLE public.games
  ADD COLUMN IF NOT EXISTS storyline TEXT,
  ADD COLUMN IF NOT EXISTS publisher TEXT,
  ADD COLUMN IF NOT EXISTS igdb_synced_at TIMESTAMPTZ;

-- ------------------------------------------------------------
-- 2) Platform varyant kolonlari
-- ------------------------------------------------------------
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

CREATE INDEX IF NOT EXISTS idx_game_platforms_igdb_slug
  ON public.game_platforms(igdb_slug);

-- game_platforms(game_id, system_id) icin unique constraint zaten canli schema'da var.
-- Burada tekrar create etmiyoruz.

CREATE UNIQUE INDEX IF NOT EXISTS uq_game_platforms_primary_variant
  ON public.game_platforms(game_id)
  WHERE is_primary_variant = TRUE;

-- ------------------------------------------------------------
-- 3) Mevcut canonical IGDB alanlarini primary varyanta backfill et
-- ------------------------------------------------------------
WITH ranked_platforms AS (
  SELECT
    gp.id,
    gp.game_id,
    g.title,
    g.release_year,
    g.external_id,
    g.igdb_url,
    g.igdb_rating,
    g.primary_cover_url,
    ROW_NUMBER() OVER (
      PARTITION BY gp.game_id
      ORDER BY gp.is_preferred DESC, gp.id
    ) AS rn
  FROM public.game_platforms gp
  JOIN public.games g
    ON g.id = gp.game_id
),
primary_targets AS (
  SELECT *
  FROM ranked_platforms
  WHERE rn = 1
)
UPDATE public.game_platforms gp
SET
  igdb_game_id = COALESCE(
    gp.igdb_game_id,
    NULLIF(REGEXP_REPLACE(pt.external_id, '[^0-9]', '', 'g'), '')::BIGINT
  ),
  igdb_url = COALESCE(gp.igdb_url, pt.igdb_url),
  igdb_rating = COALESCE(gp.igdb_rating, pt.igdb_rating),
  igdb_release_year = COALESCE(gp.igdb_release_year, pt.release_year),
  version_title = COALESCE(gp.version_title, pt.title),
  cover_url = COALESCE(gp.cover_url, pt.primary_cover_url),
  is_primary_variant = TRUE
FROM primary_targets pt
WHERE gp.id = pt.id;

UPDATE public.games
SET igdb_synced_at = COALESCE(igdb_synced_at, NOW())
WHERE external_id IS NOT NULL
   OR igdb_url IS NOT NULL
   OR igdb_rating IS NOT NULL;

-- ------------------------------------------------------------
-- 4) Dogrulama
-- ------------------------------------------------------------
SELECT table_name, column_name
FROM information_schema.columns
WHERE table_schema = 'public'
  AND (
    (table_name = 'games' AND column_name IN ('storyline', 'publisher', 'igdb_synced_at'))
    OR
    (table_name = 'game_platforms' AND column_name IN (
      'igdb_game_id',
      'igdb_slug',
      'igdb_url',
      'igdb_rating',
      'igdb_release_year',
      'igdb_first_release_date',
      'version_title',
      'is_primary_variant'
    ))
  )
ORDER BY table_name, column_name;
