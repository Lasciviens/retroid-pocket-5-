# Retroid DB Audit System

Read-only kalite kontrol katmanı. Sorunlu kayıtları tespit eder, sınıflandırır ve raporlar.

## Bileşenler

| Dosya | Tür | Açıklama |
|-------|-----|----------|
| `migrations/migration_v15.sql` | SQL | `v_games_audit` ve `v_game_platform_audit` view'larını oluşturur |
| `scripts/audit_report.py` | Python | CLI rapor aracı |
| `docs/audit_system.md` | Bu dosya | Sistem dokümantasyonu |

## View Mimarisi

```
v_game_platform_audit  ← her game_platform satırı için flag'ler
v_games_audit          ← her game için toplu flag'ler + audit_score
```

PostgREST ile doğrudan filtrelenebilir:
```
GET /rest/v1/v_games_audit?p1_no_external_id=eq.true
GET /rest/v1/v_games_audit?audit_score=lte.70&order=audit_score.asc
GET /rest/v1/v_game_platform_audit?p2_base64_cover=eq.true
```

## Kural Kataloğu

### P1 — Kritik (audit_score -20 her biri)

| Kural | Koşul | Düzeltme |
|-------|-------|----------|
| `no_external_id` | `games.external_id IS NULL` | Manuel: IGDB'de bul, `igdb_bulk_match.py` ile eşleştir |
| `no_primary_variant` | Hiçbir platform `is_primary_variant=true` değil | Auto: migration_v13 mantığı — `igdb_repair_missing.py` sonrası otomatik |
| `multiple_primaries` | 2+ platform `is_primary_variant=true` | Manuel: Fazla primary'yi false yap |

### P2 — Önemli (audit_score -5 her biri)

| Kural | Koşul | Düzeltme |
|-------|-------|----------|
| `no_release_year` | `games.release_year IS NULL` | Auto: `igdb_repair_missing.py` |
| `no_publisher` | `publisher IS NULL` | Auto: `igdb_repair_missing.py` |
| `no_description` | `description IS NULL` | Auto: `igdb_repair_missing.py` |
| `no_igdb_rating` | `igdb_rating IS NULL` | Auto: `igdb_repair_missing.py` |
| `never_synced` | `igdb_synced_at IS NULL` | Auto: `igdb_repair_missing.py` |
| `base64_cover` | `platform.cover_url LIKE 'data:%'` | Manuel: Supabase Storage'a taşı |
| `dup_title_suspect` | Aynı title+year başka game'de var | Manuel: İncele, gerekirse merge et |

### P3 — Bilgi (audit_score -1 her biri)

| Kural | Koşul | Düzeltme |
|-------|-------|----------|
| `no_primary_cover` | `primary_cover_url IS NULL` | Auto: `igdb_repair_missing.py` |
| `no_storyline` | `storyline IS NULL` | Auto: `igdb_repair_missing.py` |
| `year_mismatch` | `\|canonical_year - igdb_year\| > 1` | Manuel: ROM hack veya farklı baskı olabilir |
| `preferred_not_primary` | `is_preferred=true, is_primary_variant=false` | Manuel: primary'yi güncelle |
| `redundant_version_title` | `version_title == canonical title` | Auto: NULL yapılabilir |
| `platform_no_emulator` | `emulator_id IS NULL` | Manuel: Emulator ata |
| `platform_no_performance` | `performance IS NULL` | Manuel: Test et, değer gir |
| `platform_missing_cover` | `platform.cover_url IS NULL` | Auto: `igdb_repair_missing.py` |

## Audit Score

```
audit_score = MAX(0, 100 - P1×20 - P2×5 - P3×1)
```

| Skor | Yorum |
|------|-------|
| 100 | Mükemmel |
| 80-99 | İyi, küçük eksikler |
| 60-79 | Orta, önemli eksikler var |
| < 60 | Kötü, kritik sorunlar |

## Nasıl Çalıştırılır

```bash
# Genel özet rapor
python3 scripts/audit_report.py

# Markdown formatında
python3 scripts/audit_report.py --format markdown > audit_$(date +%Y%m%d).md

# Sadece sorunlu oyunlar (skor ≤ 70)
python3 scripts/audit_report.py --max-score 70

# Belirli issue türü
python3 scripts/audit_report.py --issue no_igdb_rating

# Belirli oyun
python3 scripts/audit_report.py --title "Metal Gear Solid"
```

## Codex — Frontend Entegrasyon Notları

`v_games_audit` view'ı **Cleanup Workspace** sayfasında kullanılabilir:

```javascript
// Sorunlu oyunları skor sırasına göre getir
fetch('/rest/v1/v_games_audit?audit_score=lte.85&order=audit_score.asc&select=id,title,audit_score,critical_issues,important_issues,issue_types')

// Belirli issue türüne göre filtrele
fetch('/rest/v1/v_games_audit?p1_no_external_id=eq.true&select=id,title,audit_score,issue_types')

// Platform audit (base64 cover listesi)
fetch('/rest/v1/v_game_platform_audit?p2_base64_cover=eq.true&select=id,game_title,system_name,game_id')
```

`issue_types` alanı bir string array'i: `["no_igdb_rating", "never_synced", "no_storyline"]`

Renk önerisi: P1 → kırmızı badge, P2 → sarı badge, P3 → gri badge.

## Auto-Fix Tetikleme

P2 auto-fixable issue'ları `igdb_repair_missing.py` ile giderilebilir:

```bash
# Tüm eksik alanları doldur (service key gerekli)
python3 scripts/igdb_repair_missing.py --service-key <KEY>

# Belirli oyun
python3 scripts/igdb_repair_missing.py --service-key <KEY> --title "Crash Bandicoot"
```
