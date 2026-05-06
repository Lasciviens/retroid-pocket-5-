-- Migration v5: game_platforms tablosuna rom_url kolonu ekle
ALTER TABLE public.game_platforms
  ADD COLUMN IF NOT EXISTS rom_url TEXT;
