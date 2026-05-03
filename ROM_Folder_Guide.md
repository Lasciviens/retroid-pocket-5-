# 📁 ROM Klasör Yapısı — Retroid Pocket 5

> **Mantık:** Önce sisteme göre klasör, içinde hangi emülatörle açılacağı belirtilmiş.
> RP5'teki standart frontend (Daijisho / RetroArch) zaten bu yapıyı bekliyor.

---

## 📂 Önerilen Klasör Yapısı

```
ROMs/
├── PS1/                    → DuckStation (standalone) veya SwanStation (RetroArch core)
├── PS2/                    → AetherSX2 (standalone) — en iyi performans bu
├── PSP/                    → PPSSPP (standalone veya RetroArch core)
├── GBA/                    → mGBA (RetroArch core) veya MyBoy (standalone)
├── DS/                     → DraStic (standalone) veya MelonDS (RetroArch core)
├── 3DS/                    → Citra (RetroArch core) — performans sınırlı olabilir
├── N64/                    → Mupen64Plus-Next (RetroArch core)
├── GameCube/               → Dolphin (standalone) — en iyi uyumluluk
├── Wii/                    → Dolphin (standalone) — GameCube ile aynı emülatör
├── Genesis/                → Genesis Plus GX (RetroArch core)
├── SNES/                   → Snes9x (RetroArch core)
├── NES/                    → Mesen (RetroArch core)
├── Dreamcast/              → Flycast (RetroArch core veya standalone)
├── BIOS/                   → Tüm BIOS dosyaları buraya (emülatörler kendi path'ini ayarlar)
└── _TODO/                  → Henüz hangi sisteme ait olduğunu bilmediğin ROM'lar
```

---

## 🎮 Sistem → Emülatör → Notlar

| Sistem | Emülatör | Tür | Not |
|--------|----------|------|-----|
| **PS1** | DuckStation | Standalone | PGXP desteği var — 3D grafikleri düzeltir |
| **PS2** | AetherSX2 | Standalone | RP5 için en iyi seçenek |
| **PSP** | PPSSPP | Standalone/Core | 1080p upscale destekli |
| **GBA** | mGBA | RetroArch Core | Cycle-accurate, en doğrusu |
| **DS** | DraStic / MelonDS | Her ikisi | DraStic ücretli ama hızlı |
| **3DS** | Citra | RetroArch Core | Bazı oyunlar yavaş olabilir |
| **N64** | Mupen64Plus-Next | RetroArch Core | ParaLLEl-N64 alternatif (doğruluğu yüksek) |
| **GameCube** | Dolphin | Standalone | Wii ile aynı emülatör |
| **Wii** | Dolphin | Standalone | Wiimote simülasyonu sınırlı |
| **Genesis** | Genesis Plus GX | RetroArch Core | Altın standart Genesis emülatörü |
| **SNES** | Snes9x | RetroArch Core | Hız/doğruluk dengesi en iyi |
| **Dreamcast** | Flycast | Core/Standalone | CHD format tercih et |

---

## 📦 ROM Formatları — Hangisi Daha İyi?

| Format | Sistemler | Avantaj |
|--------|-----------|---------|
| `.chd` | PS1, PS2, Dreamcast | Sıkıştırılmış, hızlı yükleme |
| `.cso` | PSP | Sıkıştırılmış ISO, PPSSPP destekler |
| `.iso` | PS2, PSP, GameCube | Evrensel, her yerde çalışır |
| `.cia` / `.3ds` | 3DS | İki ayrı format, Citra ikisini de destekler |
| `.gba` | GBA | Tek dosya, basit |
| `.nds` | DS | Tek dosya, basit |
| `.zip` / `.7z` | GBA, SNES, NES, Genesis | RetroArch sıkıştırılmış ROM'ları açabilir |

> **Öneri:** PS1/PS2/Dreamcast için CHD kullan — hem yer kaplamaz hem hızlı yüklenir.

---

## 🗂️ BIOS Dosyaları

Bazı emülatörler BIOS olmadan çalışmaz (özellikle PS1, PS2, DS).

```
BIOS/
├── scph5501.bin        → PS1 BIOS (USA)
├── PS2 BIOS/           → AetherSX2 için birden fazla dosya gerekebilir
├── bios9.bin           → DS BIOS
├── bios7.bin           → DS BIOS
└── firmware.bin        → DS Firmware
```

> BIOS dosyalarının nasıl edinileceği konusunda yardım edemiyorum (telif hakkı), ama hangi dosyaların gerekli olduğunu söyleyebilirim.

---

## ✅ Kütüphanedeki Oyunların Sisteme Göre Dağılımı

*(Dashboard'daki oyunlar referans alındı — ROM bulmadan önce bu listeyi kullan)*

### PS2 → AetherSX2
- God of War 1 & 2
- Grand Theft Auto III, Vice City, San Andreas
- Jak and Daxter serisi
- Ratchet & Clank serisi
- Shadow of the Colossus
- Sly Cooper serisi
- Tekken 5
- Crash Wrath of Cortex, Twinsanity
- Kingdom Hearts 1 & 2
- Final Fantasy X, XII
- Silent Hill 2
- Persona 3, 4
- Devil May Cry 1, 2, 3
- Okami
- Ico
- Baldur's Gate: Dark Alliance (varsa)

### PSP → PPSSPP
- God of War: Chains of Olympus & Ghost of Sparta
- GTA: Liberty City Stories & Vice City Stories
- GTA: Chinatown Wars
- Tekken: Dark Resurrection
- Crisis Core: Final Fantasy VII
- Persona 3 Portable
- Castlevania: The Dracula X Chronicles

### GBA → mGBA
- Pokemon FireRed / LeafGreen
- Pokemon Emerald
- Castlevania: Aria of Sorrow
- Castlevania: Circle of the Moon
- Advance Wars 1 & 2
- Metroid Fusion
- Metroid: Zero Mission
- Final Fantasy VI Advance

### DS → DraStic / MelonDS
- Pokemon HeartGold / SoulSilver
- Pokemon Platinum / Black / White
- Professor Layton serisi
- Castlevania: Portrait of Ruin, Order of Ecclesia
- The World Ends With You
- Phoenix Wright serisi
- Brain Age

### GameCube → Dolphin
- Super Mario Sunshine
- Mario Kart: Double Dash
- Paper Mario: The Thousand-Year Door
- Metroid Prime 1 & 2
- Legend of Zelda: The Wind Waker
- Legend of Zelda: Twilight Princess
- Sonic Adventure 2: Battle
- Sonic Heroes
- Pikmin 1 & 2
- TimeSplitters serisi
- Soulcalibur II

### Wii → Dolphin
- Super Mario Galaxy 1 & 2
- Mario Kart Wii
- New Super Mario Bros. Wii
- Super Smash Bros. Brawl
- Legend of Zelda: Skyward Sword
- Metroid Prime 3

### N64 → Mupen64Plus-Next
- Super Mario 64
- Mario Kart 64
- Legend of Zelda: Ocarina of Time
- Legend of Zelda: Majora's Mask
- Super Smash Bros.

### Genesis → Genesis Plus GX
- Sonic the Hedgehog 1, 2, 3
- Sonic & Knuckles

### PS1 → DuckStation
- Crash Bandicoot 1, 2, 3
- Crash Team Racing
- Tekken 3
- Final Fantasy VII, VIII, IX
- Castlevania: Symphony of the Night
- Metal Gear Solid
- Silent Hill 1
- Resident Evil 1, 2, 3
- Tony Hawk's Pro Skater 1, 2

### 3DS → Citra
- Pokemon X / Y
- Pokemon Sun / Moon
- Legend of Zelda: A Link Between Worlds

---

*Son güncelleme: 2026-05-01*
