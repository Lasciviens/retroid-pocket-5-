-- migration_v15.sql
-- Audit pipeline: v_game_platform_audit + v_games_audit
-- Her view read-only. Data write yok.

BEGIN;

-- ─── 1. v_game_platform_audit ────────────────────────────────────────────────
-- Her game_platform satırı için issue flag'leri.
-- PostgREST filtresi: ?p2_base64_cover=eq.true

DROP VIEW IF EXISTS public.v_game_platform_audit;

CREATE VIEW public.v_game_platform_audit AS
SELECT
  gp.id,
  gp.game_id,
  COALESCE(g.title, '[orphan]')  AS game_title,
  sys.name                        AS system_name,
  gp.rom_status,
  gp.is_primary_variant,
  gp.is_preferred,
  gp.emulator_id,
  gp.performance,
  gp.igdb_game_id,
  gp.version_title,

  -- ── P1 Critical ──
  -- orphan: game_id references non-existent game
  (g.id IS NULL)                                                                  AS p1_orphan_platform,

  -- ── P2 Important ──
  -- base64 image stored directly in cover_url (storage bloat)
  (gp.cover_url IS NOT NULL AND gp.cover_url LIKE 'data:%')                       AS p2_base64_cover,

  -- ── P3 Info ──
  -- no cover at all for this platform
  (gp.cover_url IS NULL OR gp.cover_url = '')                                     AS p3_no_cover,
  -- is_preferred=true but is_primary_variant=false (UI inconsistency)
  (gp.is_preferred = true
     AND (gp.is_primary_variant IS NULL OR gp.is_primary_variant = false))        AS p3_preferred_not_primary,
  -- version_title is identical to the canonical game title (useless duplication)
  (gp.version_title IS NOT NULL
     AND gp.version_title != ''
     AND LOWER(TRIM(gp.version_title)) = LOWER(TRIM(COALESCE(g.title,''))))       AS p3_version_title_redundant,
  -- no emulator assigned
  (gp.emulator_id IS NULL)                                                        AS p3_no_emulator,
  -- no performance rating set
  (gp.performance IS NULL OR gp.performance = '')                                 AS p3_no_performance,

  -- ── Severity counts for this row ──
  (CASE WHEN g.id IS NULL THEN 1 ELSE 0 END)                                     AS critical_count,

  (CASE WHEN gp.cover_url IS NOT NULL AND gp.cover_url LIKE 'data:%' THEN 1 ELSE 0 END) AS important_count,

  (CASE WHEN gp.cover_url IS NULL OR gp.cover_url = '' THEN 1 ELSE 0 END
   + CASE WHEN gp.is_preferred = true AND (gp.is_primary_variant IS NULL OR gp.is_primary_variant = false) THEN 1 ELSE 0 END
   + CASE WHEN gp.version_title IS NOT NULL AND gp.version_title != '' AND LOWER(TRIM(gp.version_title)) = LOWER(TRIM(COALESCE(g.title,''))) THEN 1 ELSE 0 END
   + CASE WHEN gp.emulator_id IS NULL THEN 1 ELSE 0 END
   + CASE WHEN gp.performance IS NULL OR gp.performance = '' THEN 1 ELSE 0 END)  AS info_count

FROM public.game_platforms gp
LEFT JOIN public.games    g   ON g.id  = gp.game_id
LEFT JOIN public.systems  sys ON sys.id = gp.system_id;


-- ─── 2. v_games_audit ────────────────────────────────────────────────────────
-- Her oyun için tüm issue flag'leri + audit_score.
-- audit_score = GREATEST(0, 100 - critical*20 - important*5 - info*1)
-- PostgREST filtresi: ?p1_no_external_id=eq.true&order=audit_score.asc

DROP VIEW IF EXISTS public.v_games_audit;

CREATE VIEW public.v_games_audit AS
WITH platform_agg AS (
  SELECT
    gp.game_id,
    COUNT(*)                                                                       AS platform_count,
    BOOL_OR(gp.is_primary_variant = true)                                         AS has_primary_variant,
    COUNT(*) FILTER (WHERE gp.is_primary_variant = true)                          AS primary_count,
    BOOL_OR(gp.cover_url IS NOT NULL AND gp.cover_url LIKE 'data:%')              AS has_base64_cover,
    BOOL_OR(gp.cover_url IS NULL OR gp.cover_url = '')                            AS has_missing_cover,
    BOOL_OR(gp.is_preferred = true
              AND (gp.is_primary_variant IS NULL OR gp.is_primary_variant = false)) AS has_preferred_not_primary,
    BOOL_OR(
      gp.version_title IS NOT NULL
      AND gp.version_title != ''
      AND LOWER(TRIM(gp.version_title)) = LOWER(TRIM(COALESCE(g.title,'')))
    )                                                                              AS has_redundant_version_title,
    BOOL_OR(gp.emulator_id IS NULL)                                               AS has_no_emulator,
    BOOL_OR(gp.performance IS NULL OR gp.performance = '')                        AS has_no_performance
  FROM public.game_platforms gp
  LEFT JOIN public.games g ON g.id = gp.game_id
  GROUP BY gp.game_id
),
primary_plat AS (
  SELECT DISTINCT ON (game_id)
    game_id,
    igdb_release_year
  FROM public.game_platforms
  WHERE is_primary_variant = true
  ORDER BY game_id
),
dup_title_check AS (
  SELECT title, release_year
  FROM public.games
  GROUP BY title, release_year
  HAVING COUNT(*) > 1
)
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

  -- Platform summary
  COALESCE(pa.platform_count, 0)      AS platform_count,
  COALESCE(pa.has_primary_variant, false) AS has_primary_variant,
  COALESCE(pa.primary_count, 0)       AS primary_variant_count,

  -- ── P1 Critical Flags ──────────────────────────────────────────────────────
  -- No IGDB match: enrichment and rating impossible
  (g.external_id IS NULL)                                       AS p1_no_external_id,
  -- No primary variant: UI can't determine which platform to show
  (NOT COALESCE(pa.has_primary_variant, false))                 AS p1_no_primary_variant,
  -- Multiple primaries: unique constraint should prevent this; flag if it slips
  (COALESCE(pa.primary_count, 0) > 1)                          AS p1_multiple_primaries,

  -- ── P2 Important Flags ─────────────────────────────────────────────────────
  -- Missing release year: filtering/sorting broken
  (g.release_year IS NULL)                                      AS p2_no_release_year,
  -- Missing publisher: metadata incomplete
  (g.publisher IS NULL OR g.publisher = '')                     AS p2_no_publisher,
  -- Missing description: modal content empty
  (g.description IS NULL OR g.description = '')                 AS p2_no_description,
  -- Missing IGDB rating: score display broken
  (g.igdb_rating IS NULL)                                       AS p2_no_igdb_rating,
  -- Never synced with IGDB: stale or unprocessed record
  (g.igdb_synced_at IS NULL)                                    AS p2_never_synced,
  -- Platform cover stored as base64 (~23KB/image, ~1.4MB total)
  COALESCE(pa.has_base64_cover, false)                          AS p2_base64_cover,
  -- Same title+year exists in another game record (possible accidental duplicate)
  EXISTS (
    SELECT 1 FROM dup_title_check dtc
    WHERE dtc.title = g.title
      AND dtc.release_year IS NOT DISTINCT FROM g.release_year
  )                                                             AS p2_dup_title_suspect,

  -- ── P3 Info Flags ──────────────────────────────────────────────────────────
  -- No primary cover URL: list card will show placeholder
  (g.primary_cover_url IS NULL OR g.primary_cover_url = '')     AS p3_no_primary_cover,
  -- No storyline: secondary metadata absent
  (g.storyline IS NULL OR g.storyline = '')                     AS p3_no_storyline,
  -- Canonical year vs primary platform IGDB year differ by >1 year
  (
    pp.igdb_release_year IS NOT NULL
    AND g.release_year IS NOT NULL
    AND ABS(g.release_year - pp.igdb_release_year) > 1
  )                                                             AS p3_year_mismatch,
  -- Platform marked is_preferred but not is_primary_variant
  COALESCE(pa.has_preferred_not_primary, false)                 AS p3_preferred_not_primary,
  -- version_title is identical to canonical title (redundant data)
  COALESCE(pa.has_redundant_version_title, false)               AS p3_redundant_version_title,
  -- Any platform missing emulator assignment
  COALESCE(pa.has_no_emulator, false)                           AS p3_platform_no_emulator,
  -- Any platform missing performance rating
  COALESCE(pa.has_no_performance, false)                        AS p3_platform_no_performance,
  -- Any platform missing cover
  COALESCE(pa.has_missing_cover, false)                         AS p3_platform_missing_cover,

  -- ── Severity counts ────────────────────────────────────────────────────────
  (
    CASE WHEN g.external_id IS NULL THEN 1 ELSE 0 END
    + CASE WHEN NOT COALESCE(pa.has_primary_variant, false) THEN 1 ELSE 0 END
    + CASE WHEN COALESCE(pa.primary_count, 0) > 1 THEN 1 ELSE 0 END
  ) AS critical_issues,

  (
    CASE WHEN g.release_year IS NULL THEN 1 ELSE 0 END
    + CASE WHEN g.publisher IS NULL OR g.publisher = '' THEN 1 ELSE 0 END
    + CASE WHEN g.description IS NULL OR g.description = '' THEN 1 ELSE 0 END
    + CASE WHEN g.igdb_rating IS NULL THEN 1 ELSE 0 END
    + CASE WHEN g.igdb_synced_at IS NULL THEN 1 ELSE 0 END
    + CASE WHEN COALESCE(pa.has_base64_cover, false) THEN 1 ELSE 0 END
    + CASE WHEN EXISTS (
        SELECT 1 FROM dup_title_check dtc
        WHERE dtc.title = g.title
          AND dtc.release_year IS NOT DISTINCT FROM g.release_year
      ) THEN 1 ELSE 0 END
  ) AS important_issues,

  (
    CASE WHEN g.primary_cover_url IS NULL OR g.primary_cover_url = '' THEN 1 ELSE 0 END
    + CASE WHEN g.storyline IS NULL OR g.storyline = '' THEN 1 ELSE 0 END
    + CASE WHEN pp.igdb_release_year IS NOT NULL AND g.release_year IS NOT NULL
              AND ABS(g.release_year - pp.igdb_release_year) > 1 THEN 1 ELSE 0 END
    + CASE WHEN COALESCE(pa.has_preferred_not_primary, false) THEN 1 ELSE 0 END
    + CASE WHEN COALESCE(pa.has_redundant_version_title, false) THEN 1 ELSE 0 END
    + CASE WHEN COALESCE(pa.has_no_emulator, false) THEN 1 ELSE 0 END
    + CASE WHEN COALESCE(pa.has_no_performance, false) THEN 1 ELSE 0 END
    + CASE WHEN COALESCE(pa.has_missing_cover, false) THEN 1 ELSE 0 END
  ) AS info_issues,

  -- ── Composite audit score (0-100, higher = healthier) ─────────────────────
  GREATEST(0,
    100
    - (CASE WHEN g.external_id IS NULL THEN 1 ELSE 0 END
       + CASE WHEN NOT COALESCE(pa.has_primary_variant, false) THEN 1 ELSE 0 END
       + CASE WHEN COALESCE(pa.primary_count, 0) > 1 THEN 1 ELSE 0 END) * 20
    - (CASE WHEN g.release_year IS NULL THEN 1 ELSE 0 END
       + CASE WHEN g.publisher IS NULL OR g.publisher = '' THEN 1 ELSE 0 END
       + CASE WHEN g.description IS NULL OR g.description = '' THEN 1 ELSE 0 END
       + CASE WHEN g.igdb_rating IS NULL THEN 1 ELSE 0 END
       + CASE WHEN g.igdb_synced_at IS NULL THEN 1 ELSE 0 END
       + CASE WHEN COALESCE(pa.has_base64_cover, false) THEN 1 ELSE 0 END
       + CASE WHEN EXISTS (
           SELECT 1 FROM dup_title_check dtc
           WHERE dtc.title = g.title
             AND dtc.release_year IS NOT DISTINCT FROM g.release_year
         ) THEN 1 ELSE 0 END) * 5
    - (CASE WHEN g.primary_cover_url IS NULL OR g.primary_cover_url = '' THEN 1 ELSE 0 END
       + CASE WHEN g.storyline IS NULL OR g.storyline = '' THEN 1 ELSE 0 END
       + CASE WHEN pp.igdb_release_year IS NOT NULL AND g.release_year IS NOT NULL
                 AND ABS(g.release_year - pp.igdb_release_year) > 1 THEN 1 ELSE 0 END
       + CASE WHEN COALESCE(pa.has_preferred_not_primary, false) THEN 1 ELSE 0 END
       + CASE WHEN COALESCE(pa.has_redundant_version_title, false) THEN 1 ELSE 0 END
       + CASE WHEN COALESCE(pa.has_no_emulator, false) THEN 1 ELSE 0 END
       + CASE WHEN COALESCE(pa.has_no_performance, false) THEN 1 ELSE 0 END
       + CASE WHEN COALESCE(pa.has_missing_cover, false) THEN 1 ELSE 0 END) * 1
  ) AS audit_score,

  -- ── Issue type labels (for display / frontend badges) ─────────────────────
  ARRAY_REMOVE(ARRAY[
    CASE WHEN g.external_id IS NULL THEN 'no_external_id' END,
    CASE WHEN NOT COALESCE(pa.has_primary_variant, false) THEN 'no_primary_variant' END,
    CASE WHEN COALESCE(pa.primary_count, 0) > 1 THEN 'multiple_primaries' END,
    CASE WHEN g.release_year IS NULL THEN 'no_release_year' END,
    CASE WHEN g.publisher IS NULL OR g.publisher = '' THEN 'no_publisher' END,
    CASE WHEN g.description IS NULL OR g.description = '' THEN 'no_description' END,
    CASE WHEN g.igdb_rating IS NULL THEN 'no_igdb_rating' END,
    CASE WHEN g.igdb_synced_at IS NULL THEN 'never_synced' END,
    CASE WHEN COALESCE(pa.has_base64_cover, false) THEN 'base64_cover' END,
    CASE WHEN EXISTS (
      SELECT 1 FROM dup_title_check dtc
      WHERE dtc.title = g.title AND dtc.release_year IS NOT DISTINCT FROM g.release_year
    ) THEN 'dup_title_suspect' END,
    CASE WHEN g.primary_cover_url IS NULL OR g.primary_cover_url = '' THEN 'no_primary_cover' END,
    CASE WHEN g.storyline IS NULL OR g.storyline = '' THEN 'no_storyline' END,
    CASE WHEN pp.igdb_release_year IS NOT NULL AND g.release_year IS NOT NULL
              AND ABS(g.release_year - pp.igdb_release_year) > 1 THEN 'year_mismatch' END,
    CASE WHEN COALESCE(pa.has_preferred_not_primary, false) THEN 'preferred_not_primary' END,
    CASE WHEN COALESCE(pa.has_redundant_version_title, false) THEN 'redundant_version_title' END,
    CASE WHEN COALESCE(pa.has_no_emulator, false) THEN 'platform_no_emulator' END,
    CASE WHEN COALESCE(pa.has_no_performance, false) THEN 'platform_no_performance' END,
    CASE WHEN COALESCE(pa.has_missing_cover, false) THEN 'platform_missing_cover' END
  ], NULL) AS issue_types

FROM public.games g
LEFT JOIN public.series       s  ON s.id  = g.series_id
LEFT JOIN platform_agg        pa ON pa.game_id = g.id
LEFT JOIN primary_plat        pp ON pp.game_id = g.id
ORDER BY g.title;

COMMIT;

-- ─── DOĞRULAMA ───────────────────────────────────────────────────────────────
SELECT
  COUNT(*)                                               AS total_games,
  COUNT(*) FILTER (WHERE critical_issues > 0)           AS games_with_p1,
  COUNT(*) FILTER (WHERE important_issues > 0)          AS games_with_p2,
  COUNT(*) FILTER (WHERE info_issues > 0)               AS games_with_p3,
  ROUND(AVG(audit_score), 1)                            AS avg_score,
  MIN(audit_score)                                      AS min_score,
  MAX(audit_score)                                      AS max_score
FROM public.v_games_audit;
