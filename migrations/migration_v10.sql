-- migration_v10.sql
-- v_games_full view yenile: themes, age_rating, rating_count, multiplayer_info eklendi
-- Supabase SQL Editor'de calistir

DROP VIEW IF EXISTS public.v_games_full;

CREATE VIEW public.v_games_full AS
SELECT
  g.id, g.title, g.release_year, g.developer, g.publisher,
  g.description, g.storyline,
  g.keywords, g.screenshots, g.themes,
  g.age_rating, g.rating_count, g.multiplayer_info,
  g.play_status, g.play_notes, g.game_log, g.play_order, g.tier,
  g.rating, g.is_coop, g.coop_notes, g.is_iconic,
  g.primary_cover_url,
  g.series_id, g.external_id,
  g.igdb_rating      AS igdb_rating_canonical,
  g.igdb_url         AS igdb_url_canonical,
  g.igdb_synced_at,
  g.created_at, g.updated_at,
  s.name AS series_name,
  COALESCE(
    array_agg(DISTINCT gnr.name) FILTER (WHERE gnr.name IS NOT NULL),
    '{}'
  ) AS genres,
  COALESCE(
    json_agg(
      jsonb_build_object(
        'id',                   gp.id,
        'system',               sys.name,
        'system_id',            sys.id,
        'emulator',             emu.name,
        'emulator_id',          emu.id,
        'performance',          gp.performance,
        'performance_notes',    gp.performance_notes,
        'cover_url',            gp.cover_url,
        'rom_status',           gp.rom_status,
        'rom_url',              gp.rom_url,
        'region',               gp.region,
        'folder_path',          gp.folder_path,
        'is_primary_variant',   gp.is_primary_variant,
        'igdb_game_id',         gp.igdb_game_id,
        'igdb_slug',            gp.igdb_slug,
        'igdb_rating',          gp.igdb_rating,
        'igdb_url',             gp.igdb_url,
        'igdb_release_year',    gp.igdb_release_year,
        'version_title',        gp.version_title
      )
      ORDER BY gp.is_primary_variant DESC NULLS LAST, gp.id
    ) FILTER (WHERE gp.id IS NOT NULL),
    '[]'
  ) AS platforms
FROM public.games g
LEFT JOIN public.series        s   ON g.series_id    = s.id
LEFT JOIN public.game_genres   gg  ON gg.game_id     = g.id
LEFT JOIN public.genres        gnr ON gnr.id         = gg.genre_id
LEFT JOIN public.game_platforms gp ON gp.game_id     = g.id
LEFT JOIN public.systems       sys ON sys.id         = gp.system_id
LEFT JOIN public.emulators     emu ON emu.id         = gp.emulator_id
GROUP BY g.id, s.name, s.id;

-- Dogrulama
SELECT title, themes, age_rating, rating_count, multiplayer_info
FROM v_games_full LIMIT 3;
