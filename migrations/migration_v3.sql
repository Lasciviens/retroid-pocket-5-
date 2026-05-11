-- ============================================================
-- RETROID POCKET 5 — Migration v3
-- Supabase SQL Editor'de çalıştır (tek seferde tümünü seç + Run)
-- Data kaybı yok. Tüm adımlar güvenli.
-- ============================================================

-- ─────────────────────────────────────────────
-- 1. emulator_systems junction tablosu oluştur
--    (emulators.supported_systems text[] yerini alır)
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.emulator_systems (
  emulator_id INTEGER NOT NULL REFERENCES public.emulators(id) ON DELETE CASCADE,
  system_id   INTEGER NOT NULL REFERENCES public.systems(id)   ON DELETE CASCADE,
  PRIMARY KEY (emulator_id, system_id)
);

-- Mevcut supported_systems text[] datasını junction tablosuna kopyala
INSERT INTO public.emulator_systems (emulator_id, system_id)
SELECT e.id, s.id
FROM public.emulators e
JOIN public.systems s ON s.name = ANY(e.supported_systems)
ON CONFLICT DO NOTHING;

-- ─────────────────────────────────────────────
-- 2. notes tablosuna opsiyonel game_id FK ekle
--    (Tips ve Requests standalone kullanmaya devam eder,
--     game'e bağlı notlar için game_id doldurulabilir)
-- ─────────────────────────────────────────────
ALTER TABLE public.notes
  ADD COLUMN IF NOT EXISTS game_id UUID REFERENCES public.games(id) ON DELETE SET NULL;

-- ─────────────────────────────────────────────
-- 3. roms tablosunu temizle (boş, hiç data yok)
-- ─────────────────────────────────────────────
DROP TABLE IF EXISTS public.roms;

-- ─────────────────────────────────────────────
-- 4. games_full view'ini yeniden oluştur (düzgün isim ile)
--    Eski view çalışmaya devam eder, buna ek olarak
--    v_games_full da oluşturulur
-- ─────────────────────────────────────────────
CREATE OR REPLACE VIEW public.v_games_full AS
SELECT
  g.id,
  g.title,
  g.release_year,
  g.play_status,
  g.rating,
  g.is_coop,
  g.coop_notes,
  g.is_iconic,
  g.description,
  g.play_notes,
  g.game_log,
  g.tier,
  g.play_order,
  g.external_id,
  s.name AS series_name,
  COALESCE(
    json_agg(DISTINCT jsonb_build_object('id', gnr.id, 'name', gnr.name))
    FILTER (WHERE gnr.id IS NOT NULL), '[]'
  ) AS genres,
  COALESCE(
    json_agg(DISTINCT jsonb_build_object(
      'id', gp.id,
      'system', sys.name,
      'emulator', emu.name,
      'performance', gp.performance,
      'performance_notes', gp.performance_notes,
      'cover_url', gp.cover_url,
      'rom_status', gp.rom_status,
      'region', gp.region,
      'folder_path', gp.folder_path
    )) FILTER (WHERE gp.id IS NOT NULL), '[]'
  ) AS platforms
FROM public.games g
LEFT JOIN public.series s        ON g.series_id = s.id
LEFT JOIN public.game_genres gg  ON gg.game_id = g.id
LEFT JOIN public.genres gnr      ON gnr.id = gg.genre_id
LEFT JOIN public.game_platforms gp ON gp.game_id = g.id
LEFT JOIN public.systems sys     ON sys.id = gp.system_id
LEFT JOIN public.emulators emu   ON emu.id = gp.emulator_id
GROUP BY g.id, s.name;

-- ─────────────────────────────────────────────
-- 5. Doğrulama — çalıştırdıktan sonra kontrol et
-- ─────────────────────────────────────────────
SELECT 'emulator_systems satır sayısı:' AS check, COUNT(*) FROM public.emulator_systems;
SELECT 'games_full view çalışıyor:' AS check, COUNT(*) FROM public.games_full;
SELECT 'v_games_full view çalışıyor:' AS check, COUNT(*) FROM public.v_games_full;
