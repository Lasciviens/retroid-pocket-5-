-- migration_v14.sql
-- 1. v_games_summary  — Library liste görünümü (hafif, base64 yok)
-- 2. v_games_cleanup  — Admin anomali görünümü

BEGIN;

-- ─── 1. v_games_summary ──────────────────────────────────────────────────────
-- Yalnızca liste/kart UI için gereken alanlar.
-- Ağır alanlar çıkarıldı: description, storyline, screenshots, keywords,
--   themes, game_log, play_notes, coop_notes, age_rating, rating_count,
--   multiplayer_info
-- Platforms JSON'dan çıkarıldı: cover_url (base64 bloat), igdb_game_id,
--   igdb_slug, igdb_url, igdb_rating, igdb_release_year, version_title,
--   rom_url, folder_path, performance_notes
-- Sonuç: ~1.4 MB base64 yükü + ~0.5 MB metin yükü kalkar

DROP VIEW IF EXISTS public.v_games_summary;

CREATE VIEW public.v_games_summary AS
SELECT
  g.id,
  g.title,
  g.release_year,
  g.publisher,
  g.play_status,
  g.play_order,
  g.tier,
  g.rating,
  g.igdb_rating AS igdb_rating_canonical,
  g.is_coop,
  g.is_iconic,
  g.primary_cover_url,
  g.series_id,
  g.external_id,
  g.igdb_synced_at,
  g.created_at,
  g.updated_at,
  s.name AS series_name,

  COALESCE((
    SELECT array_agg(DISTINCT gnr.name ORDER BY gnr.name)
    FROM game_genres gg2
    JOIN genres gnr ON gnr.id = gg2.genre_id
    WHERE gg2.game_id = g.id AND gnr.name IS NOT NULL
  ), '{}') AS genres,

  COALESCE((
    SELECT json_agg(
      jsonb_build_object(
        'id',                 gp.id,
        'system',             sys.name,
        'system_id',          sys.id,
        'emulator',           emu.name,
        'emulator_id',        emu.id,
        'performance',        gp.performance,
        'rom_status',         gp.rom_status,
        'region',             gp.region,
        'is_primary_variant', gp.is_primary_variant
      )
      ORDER BY gp.is_primary_variant DESC NULLS LAST, gp.id
    )
    FROM game_platforms gp
    LEFT JOIN systems  sys ON sys.id = gp.system_id
    LEFT JOIN emulators emu ON emu.id = gp.emulator_id
    WHERE gp.game_id = g.id
  ), '[]') AS platforms

FROM games g
LEFT JOIN series s ON g.series_id = s.id;

-- ─── 2. v_games_cleanup ──────────────────────────────────────────────────────
-- Admin anomali görünümü. Her satır bir oyunu temsil eder.
-- Bayraklar: has_primary, base64_cover_count, missing_igdb, missing_rating,
--   missing_year, missing_publisher, missing_description, orphan_platform

DROP VIEW IF EXISTS public.v_games_cleanup;

CREATE VIEW public.v_games_cleanup AS
SELECT
  g.id,
  g.title,
  g.release_year,
  g.publisher,
  g.play_status,
  g.external_id,
  g.igdb_rating,
  g.igdb_synced_at,
  g.primary_cover_url,
  g.created_at,
  s.name AS series_name,

  -- Platform sayıları
  (SELECT COUNT(*) FROM game_platforms gp WHERE gp.game_id = g.id)
    AS platform_count,

  -- Primary variant var mı?
  (SELECT bool_or(gp.is_primary_variant)
   FROM game_platforms gp WHERE gp.game_id = g.id)
    AS has_primary_variant,

  -- Kaç platformda base64 cover var?
  (SELECT COUNT(*)
   FROM game_platforms gp
   WHERE gp.game_id = g.id
     AND gp.cover_url IS NOT NULL
     AND gp.cover_url LIKE 'data:%')
    AS base64_cover_count,

  -- Kaç platformda cover_url yok?
  (SELECT COUNT(*)
   FROM game_platforms gp
   WHERE gp.game_id = g.id
     AND gp.cover_url IS NULL)
    AS missing_platform_cover_count,

  -- Tür var mı?
  (SELECT COUNT(*) FROM game_genres gg WHERE gg.game_id = g.id)
    AS genre_count,

  -- Anomali bayrakları
  (g.external_id IS NULL)                                    AS missing_igdb,
  (g.igdb_rating IS NULL)                                    AS missing_igdb_rating,
  (g.release_year IS NULL)                                   AS missing_year,
  (g.publisher IS NULL OR g.publisher = '')                  AS missing_publisher,
  (g.description IS NULL OR g.description = '')             AS missing_description,
  (g.primary_cover_url IS NULL OR g.primary_cover_url = '') AS missing_primary_cover,
  (g.igdb_synced_at IS NULL)                                 AS never_synced,

  -- Sistemlerin listesi
  COALESCE((
    SELECT array_agg(sys.name ORDER BY sys.name)
    FROM game_platforms gp
    JOIN systems sys ON sys.id = gp.system_id
    WHERE gp.game_id = g.id
  ), '{}') AS systems

FROM games g
LEFT JOIN series s ON g.series_id = s.id
ORDER BY g.title;

COMMIT;

-- ─── DOĞRULAMA ───────────────────────────────────────────────────────────────
SELECT
  'v_games_summary' AS view_name,
  COUNT(*) AS row_count
FROM public.v_games_summary
UNION ALL
SELECT
  'v_games_cleanup',
  COUNT(*)
FROM public.v_games_cleanup;

-- Cleanup anomali özeti
SELECT
  COUNT(*) FILTER (WHERE missing_igdb)           AS no_igdb,
  COUNT(*) FILTER (WHERE missing_igdb_rating)    AS no_rating,
  COUNT(*) FILTER (WHERE missing_year)           AS no_year,
  COUNT(*) FILTER (WHERE missing_publisher)      AS no_publisher,
  COUNT(*) FILTER (WHERE missing_description)    AS no_desc,
  COUNT(*) FILTER (WHERE NOT has_primary_variant) AS no_primary,
  COUNT(*) FILTER (WHERE base64_cover_count > 0) AS has_base64_cover,
  COUNT(*) FILTER (WHERE never_synced)           AS never_synced
FROM public.v_games_cleanup;
