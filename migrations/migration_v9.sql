-- migration_v9.sql
-- Yeni kolonlar: themes, age_rating, rating_count, multiplayer_info
-- Supabase SQL Editor'de calistir

ALTER TABLE public.games
  ADD COLUMN IF NOT EXISTS themes           TEXT[]  DEFAULT '{}',
  ADD COLUMN IF NOT EXISTS age_rating       TEXT    DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS rating_count     INTEGER DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS multiplayer_info TEXT[]  DEFAULT '{}';
-- multiplayer_info: ["Offline co-op (2)", "Online co-op (4)"] gibi
-- is_coop ve coop_notes mevcut kolonlar, multiplayer_modes'dan otomatik doldurulacak

-- Dogrulama
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'games'
  AND column_name IN ('themes','age_rating','rating_count','multiplayer_info')
ORDER BY column_name;
