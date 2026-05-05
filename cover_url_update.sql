-- ============================================================
-- COVER URL GÜNCELLEME
-- ============================================================

-- Mevcut tüm oyunların primary_cover_url'sini gör
SELECT title, primary_cover_url IS NOT NULL AS cover_var, primary_cover_url
FROM games ORDER BY title;

-- Tek oyun güncelle
UPDATE games SET primary_cover_url = 'https://YENİ_URL' WHERE title = 'Oyun Adı';

-- ============================================================
-- EKSİK COVER'LAR — sen doldur (Wikipedia veya başka kaynak)
-- Bu 5 oyunun libretro'da cover'ı yok, URL'yi kendin bul
-- ============================================================

-- Mario & Luigi: Superstar Saga (GBA)
UPDATE games SET primary_cover_url = 'https://...' WHERE title = 'Mario & Luigi: Superstar Saga';

-- Pokemon FireRed (GBA)
UPDATE games SET primary_cover_url = 'https://...' WHERE title = 'Pokemon FireRed';

-- Pokemon LeafGreen (GBA)
UPDATE games SET primary_cover_url = 'https://...' WHERE title = 'Pokemon LeafGreen';

-- Ratchet & Clank (PS2)
UPDATE games SET primary_cover_url = 'https://...' WHERE title = 'Ratchet & Clank';

-- Resident Evil: Code Veronica X (PS2)
UPDATE games SET primary_cover_url = 'https://...' WHERE title = 'Resident Evil: Code Veronica X';
