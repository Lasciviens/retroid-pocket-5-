#!/usr/bin/env python3
"""
Retroid DB Audit Auto-Fix

v_games_audit bulgularından auto-fixable sorunları düzeltir.
- Data silme yok
- Sadece NULL/boş alanları doldurur, mevcut değerleri ezmez
- base64_cover ve dup_title_suspect'e dokunmaz
- no_primary_variant: sadece "platform kaydı var ama primary yok" durumunu fix eder

Kullanim:
  python3 scripts/audit_autofix.py                               # dry-run
  python3 scripts/audit_autofix.py --apply --service-key KEY     # tümünü uygula
  python3 scripts/audit_autofix.py --phase primary_variant        # sadece primary variant
  python3 scripts/audit_autofix.py --phase igdb                   # sadece IGDB enrich
  python3 scripts/audit_autofix.py --phase igdb --limit 20        # max 20 oyun
"""

import argparse
import json
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone

SB = "https://bniqmxbtvgwkaoswugds.supabase.co"
ANON_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    ".eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJuaXFteGJ0dmd3a2Fvc3d1Z2RzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc4NTExMTYsImV4cCI6MjA5MzQyNzExNn0"
    ".VXjnGv3uV8A2XfAW5jOBAkxyzc9c9q6adrA64JfwrQs"
)
IGDB_PROXY = f"{SB}/functions/v1/igdb-search"


# ── Helpers ───────────────────────────────────────────────────────────────────

def now_iso():
    return datetime.now(timezone.utc).isoformat()


def year_from_ts(ts):
    if not ts:
        return None
    return datetime.fromtimestamp(ts, tz=timezone.utc).year


def ts_to_iso(ts):
    if not ts:
        return None
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def first_publisher(companies):
    for c in (companies or []):
        if c.get("publisher") and c.get("company", {}).get("name"):
            return c["company"]["name"]
    return None


def cover_big(url_raw):
    if not url_raw:
        return None
    return url_raw.replace("//", "https://").replace("/t_thumb/", "/t_cover_big/")


# ── HTTP ──────────────────────────────────────────────────────────────────────

def _do_get(url, headers):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read())


def _do_patch(url, payload, service_key):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        method="PATCH",
        headers={
            "apikey": service_key,
            "Authorization": f"Bearer {service_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        },
    )
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.status


def rest_get(endpoint, params):
    # Build URL without percent-encoding commas/dots in values
    # (PostgREST query params are safe ASCII only in this codebase)
    qs = "&".join(f"{k}={v}" for k, v in params.items())
    url = f"{SB}/rest/v1/{endpoint}?{qs}"
    hdrs = {"apikey": ANON_KEY, "Authorization": f"Bearer {ANON_KEY}", "Accept": "application/json"}
    return _do_get(url, hdrs)


def rest_patch(table, row_filter, payload, service_key, dry_run):
    if dry_run:
        return 200
    url = f"{SB}/rest/v1/{table}?{row_filter}"
    return _do_patch(url, payload, service_key)


# ── Audit snapshot ────────────────────────────────────────────────────────────

TRACKED = [
    ("p1_no_external_id",         "P1 no_external_id"),
    ("p1_no_primary_variant",     "P1 no_primary_variant"),
    ("p2_never_synced",           "P2 never_synced"),
    ("p2_no_igdb_rating",         "P2 no_igdb_rating"),
    ("p2_no_publisher",           "P2 no_publisher"),
    ("p2_no_release_year",        "P2 no_release_year"),
    ("p2_base64_cover",           "P2 base64_cover"),
    ("p2_dup_title_suspect",      "P2 dup_title_suspect"),
    ("p3_no_storyline",           "P3 no_storyline"),
    ("p3_no_primary_cover",       "P3 no_primary_cover"),
    ("p3_year_mismatch",          "P3 year_mismatch"),
    ("p3_platform_missing_cover", "P3 plat_missing_cover"),
    ("p3_platform_no_performance","P3 plat_no_perf"),
]
TRACKED_KEYS = [k for k, _ in TRACKED]


def get_audit_snapshot():
    rows = rest_get("v_games_audit", {
        "select": ",".join(["critical_issues", "important_issues", "audit_score"] + TRACKED_KEYS),
        "limit": "500",
    })
    snap = {k: 0 for k in TRACKED_KEYS}
    snap.update({"total": len(rows), "avg_score": 0, "games_p1": 0, "games_p2": 0})
    scores = []
    for r in rows:
        scores.append(r.get("audit_score", 100))
        if r.get("critical_issues", 0) > 0:
            snap["games_p1"] += 1
        if r.get("important_issues", 0) > 0:
            snap["games_p2"] += 1
        for k in TRACKED_KEYS:
            if r.get(k):
                snap[k] += 1
    if scores:
        snap["avg_score"] = round(sum(scores) / len(scores), 1)
    return snap


# ── Phase 1: Primary Variant ──────────────────────────────────────────────────

def run_primary_variant(dry_run, service_key):
    """
    platform_count > 0 olan oyunlarda primary variant yok ise:
    igdb_game_id'i olan ilk platformu (yoksa id sırasına göre) primary seç.

    platform_count == 0 olan oyunlar: platform kaydı yok, manuel müdahale gerekir.
    """
    candidates = rest_get("v_games_audit", {
        "p1_no_primary_variant": "eq.true",
        "select": "id,title,platform_count",
    })

    auto_fixed, manual = [], []

    for g in candidates:
        if g["platform_count"] == 0:
            manual.append({
                "title": g["title"],
                "reason": "platform kaydı yok — önce game_platforms'a ekle",
            })
            continue

        platforms = rest_get("game_platforms", {
            "game_id": f"eq.{g['id']}",
            "select": "id,igdb_game_id",
            "order": "igdb_game_id.desc.nullslast,id.asc",
            "limit": "1",
        })
        if not platforms:
            manual.append({"title": g["title"], "reason": "platform sorgusu boş döndü"})
            continue

        best_id = platforms[0]["id"]
        status = rest_patch(
            "game_platforms", f"id=eq.{best_id}",
            {"is_primary_variant": True},
            service_key, dry_run,
        )
        tag = "[dry]" if dry_run else ("✓" if status < 300 else "✗")
        print(f"  {tag} primary_variant: {g['title']}")
        auto_fixed.append(g["title"])

    return auto_fixed, manual


# ── Phase 2: IGDB Enrich ──────────────────────────────────────────────────────

# v_games_audit'ta olan sütunlar: release_year, igdb_rating, publisher,
# primary_cover_url, igdb_synced_at. "storyline" ve "igdb_url" görünümde yok;
# bunun yerine p3_no_storyline audit flag'ini kullanıyoruz.
IGDB_SELECT = (
    "id,title,external_id,release_year,igdb_rating,publisher,"
    "primary_cover_url,igdb_synced_at,"
    "p2_never_synced,p2_no_igdb_rating,p2_no_publisher,p2_no_release_year,"
    "p3_no_storyline,p3_no_primary_cover"
)


def get_igdb_candidates():
    """External_id si olan ve herhangi bir IGDB issue'su bulunan oyunlar."""
    rows = rest_get("v_games_audit", {
        "p1_no_external_id": "eq.false",
        "select": IGDB_SELECT,
        "order": "audit_score.asc",
        "limit": "500",
    })
    return [r for r in rows if (
        r.get("p2_never_synced")
        or r.get("p2_no_igdb_rating")
        or r.get("p2_no_publisher")
        or r.get("p2_no_release_year")
        or r.get("p3_no_storyline")
        or r.get("p3_no_primary_cover")
    )]


def fetch_igdb(igdb_id):
    url = f"{IGDB_PROXY}?id={urllib.parse.quote(str(igdb_id))}"
    hdrs = {"Authorization": f"Bearer {ANON_KEY}", "Accept": "application/json"}
    try:
        data = _do_get(url, hdrs)
        results = data.get("results", [])
        return results[0] if results else None
    except Exception as e:
        return None


def build_game_patch(game, igdb):
    """
    Mevcut değerleri ezmez; sadece NULL/boş alanları doldurur.
    storyline: v_games_audit'ta sütun olmadığı için p3_no_storyline flag'i kullanılır.
    igdb_url: görünümde yok; igdb_repair_missing.py ayrıca işler.
    """
    patch = {"igdb_synced_at": now_iso()}
    filled = []

    year = year_from_ts(igdb.get("first_release_date"))
    rating = igdb.get("total_rating") or igdb.get("rating")
    publisher = first_publisher(igdb.get("involved_companies"))
    storyline = igdb.get("storyline") or ""
    cover = cover_big((igdb.get("cover") or {}).get("url"))

    if game.get("release_year") is None and year:
        patch["release_year"] = year
        filled.append("release_year")
    if game.get("igdb_rating") is None and rating:
        patch["igdb_rating"] = round(float(rating), 2)
        filled.append("igdb_rating")
    if not game.get("publisher") and publisher:
        patch["publisher"] = publisher
        filled.append("publisher")
    # storyline: flag ile kontrol et (sütun görünümde yok)
    if game.get("p3_no_storyline") and storyline:
        patch["storyline"] = storyline
        filled.append("storyline")
    if not game.get("primary_cover_url") and cover:
        patch["primary_cover_url"] = cover
        filled.append("primary_cover_url")

    return patch, filled


def run_igdb_enrich(dry_run, service_key, limit):
    candidates = get_igdb_candidates()
    if limit:
        candidates = candidates[:limit]

    total = len(candidates)
    stamp_only, igdb_updated, igdb_no_data, igdb_nothing_new = [], [], [], []

    for idx, game in enumerate(candidates, 1):
        title = game["title"]
        ext_id = game["external_id"]
        sys.stdout.write(f"\r  [{idx:3}/{total}] {title[:45]:<45}")
        sys.stdout.flush()

        needs_data = any([
            game.get("release_year") is None,
            game.get("igdb_rating") is None,
            not game.get("publisher"),
            game.get("p3_no_storyline"),     # flag: storyline sütunu görünümde yok
            not game.get("primary_cover_url"),
        ])

        if not needs_data:
            # Tüm alanlar dolu; sadece igdb_synced_at damgası yeterli
            rest_patch("games", f"id=eq.{game['id']}", {"igdb_synced_at": now_iso()},
                       service_key, dry_run)
            stamp_only.append(title)
            continue

        igdb = fetch_igdb(ext_id)
        if not igdb:
            igdb_no_data.append(title)
            continue

        patch, filled = build_game_patch(game, igdb)
        if len(filled) == 0:
            # igdb_synced_at dışında yeni bir şey yok
            rest_patch("games", f"id=eq.{game['id']}", {"igdb_synced_at": now_iso()},
                       service_key, dry_run)
            igdb_nothing_new.append(title)
        else:
            rest_patch("games", f"id=eq.{game['id']}", patch, service_key, dry_run)
            igdb_updated.append({"title": title, "fields": filled})

        time.sleep(0.25)

    print()  # newline after progress
    return stamp_only, igdb_updated, igdb_no_data, igdb_nothing_new


# ── Report helpers ────────────────────────────────────────────────────────────

W = 70

def hline(char="─"):
    print(char * W)


def print_diff_table(before, after):
    print(f"  {'Issue':<30} {'Önce':>6}  {'Sonra':>6}  {'Δ':>6}")
    print(f"  {'-' * 28} {'------':>6}  {'------':>6}  {'------':>6}")
    for key, label in TRACKED:
        b, a = before.get(key, 0), after.get(key, 0)
        d = a - b
        ds = f"−{abs(d)}" if d < 0 else (f"+{d}" if d > 0 else "  =")
        print(f"  {label:<30} {b:>6}  {a:>6}  {ds:>6}")
    print(f"  {'avg audit_score':<30} {before.get('avg_score', 0):>6.1f}  {after.get('avg_score', 0):>6.1f}")


def main():
    p = argparse.ArgumentParser(description="Retroid DB Audit Auto-Fix")
    p.add_argument("--apply", action="store_true",
                   help="Değişiklikleri uygula (varsayılan: dry-run)")
    p.add_argument("--service-key", help="Supabase service role key")
    p.add_argument("--phase", choices=["all", "primary_variant", "igdb"], default="all")
    p.add_argument("--limit", type=int, help="IGDB phase: max işlenecek oyun sayısı")
    args = p.parse_args()

    if args.apply and not args.service_key:
        print("HATA: --apply için --service-key gerekli.", file=sys.stderr)
        sys.exit(1)

    dry_run = not args.apply
    mode = "DRY-RUN" if dry_run else "APPLY"

    print("=" * W)
    print(f"  RETROID AUDIT AUTO-FIX — {mode}")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}  |  phase: {args.phase}")
    print("=" * W)

    print("\n  Mevcut durum okunuyor...")
    before = get_audit_snapshot()
    print(f"  {before['total']} oyun  |  avg score: {before['avg_score']}  "
          f"|  P1: {before['games_p1']}  |  P2: {before['games_p2']}")

    results = {}

    # ── Phase 1 ────────────────────────────────────────────────────────────────
    if args.phase in ("all", "primary_variant"):
        print()
        hline()
        print("  PHASE 1: PRIMARY VARIANT FIX")
        hline()
        fixed, manual = run_primary_variant(dry_run, args.service_key)
        results["pv"] = {"fixed": fixed, "manual": manual}

        if not fixed and not manual:
            print("  Etkilenen oyun yok.")
        else:
            print(f"\n  {'[DRY] ' if dry_run else ''}Düzeltilebilir : {len(fixed)}")
            print(f"  Manuel bırakılan : {len(manual)}")
            if manual:
                for m in manual:
                    print(f"    • {m['title']} — {m['reason']}")

    # ── Phase 2 ────────────────────────────────────────────────────────────────
    if args.phase in ("all", "igdb"):
        print()
        hline()
        print("  PHASE 2: IGDB ENRICH")
        hline()
        if args.limit:
            print(f"  Limit: {args.limit} oyun")
        stamp, updated, no_data, nothing_new = run_igdb_enrich(
            dry_run, args.service_key, args.limit
        )
        results["igdb"] = {
            "stamp_only": stamp,
            "updated": updated,
            "no_data": no_data,
            "nothing_new": nothing_new,
        }

        tag = "[dry] " if dry_run else ""
        print(f"\n  {tag}Güncellendi (yeni alan)  : {len(updated)}")
        print(f"  {tag}Damgalandı (tüm alan dolu): {len(stamp) + len(nothing_new)}")
        print(f"  IGDB'de bulunamadı       : {len(no_data)}")

        if updated:
            print("\n  Güncellenen oyunlar ve alanlar:")
            for u in updated[:30]:
                print(f"    • {u['title']:<45} [{', '.join(u['fields'])}]")
            if len(updated) > 30:
                print(f"    ... ve {len(updated) - 30} tane daha")

        if no_data:
            print("\n  IGDB'de bulunamayanlar (manuel eşleştirme gerekebilir):")
            for t in no_data:
                print(f"    • {t}")

    # ── After snapshot ─────────────────────────────────────────────────────────
    if args.apply:
        print()
        hline()
        print("  SONUÇ: ÖNCE / SONRA")
        hline()
        after = get_audit_snapshot()
        print()
        print_diff_table(before, after)
    else:
        after = before

    # ── Final summary ──────────────────────────────────────────────────────────
    print()
    hline()
    print("  MANUEL REVIEW GEREKTİREN KONULAR (bilinçli olarak bırakıldı)")
    hline()
    manual_items = [
        ("no_external_id",        before.get("p1_no_external_id", 0),
         "igdb_bulk_match.py ile eşleşme bul"),
        ("no_primary_variant",    before.get("p1_no_primary_variant", 0),
         "Önce game_platforms kaydı ekle"),
        ("base64_cover",          before.get("p2_base64_cover", 0),
         "Supabase Storage'a taşıma kararı sende"),
        ("dup_title_suspect",     before.get("p2_dup_title_suspect", 0),
         "Mario Golf, Metal Gear Solid — kasıtlı multi-platform"),
        ("year_mismatch",         before.get("p3_year_mismatch", 0),
         "ROM hack yıl farkı — kasıtlı olabilir"),
        ("platform_no_performance", before.get("p3_platform_no_performance", 0),
         "Test edip elle gir"),
        ("platform_missing_cover", before.get("p3_platform_missing_cover", 0),
         "igdb_repair_missing.py platform cover'larını da doldurur"),
    ]
    print(f"  {'Issue':<28} {'Sayı':>5}  Neden / Nasıl")
    print(f"  {'-' * 26} {'-----':>5}  {'-' * 32}")
    for issue, cnt, note in manual_items:
        print(f"  {issue:<28} {cnt:>5}  {note}")

    if dry_run:
        print()
        print("  DRY-RUN tamamlandı. Değişiklik yapılmadı.")
        print("  Uygulamak için: --apply --service-key <SERVICE_ROLE_KEY>")

    print("=" * W)


if __name__ == "__main__":
    main()
