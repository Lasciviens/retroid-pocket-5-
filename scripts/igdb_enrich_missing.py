#!/usr/bin/env python3
"""
IGDB Enrich Missing

Amaç:
- external_id ile IGDB'ye exact gidip eksik metadata'yi tamamlamak
- mevcut kullanıcı verisini ezmemek
- array alanları merge etmek
- dry-run raporu ile ne değişeceğini önceden görmek

Kullanim:
  python3 scripts/igdb_enrich_missing.py --dry-run
  python3 scripts/igdb_enrich_missing.py --dry-run --limit 20
  python3 scripts/igdb_enrich_missing.py --dry-run --fields core
  python3 scripts/igdb_enrich_missing.py --apply --service-key <SERVICE_ROLE_KEY>
  python3 scripts/igdb_enrich_missing.py --apply --service-key <SERVICE_ROLE_KEY> --title "Tomb Raider"
"""

import argparse
import json
import time
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone

SB = "https://bniqmxbtvgwkaoswugds.supabase.co"
ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJuaXFteGJ0dmd3a2Fvc3d1Z2RzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc4NTExMTYsImV4cCI6MjA5MzQyNzExNn0.VXjnGv3uV8A2XfAW5jOBAkxyzc9c9q6adrA64JfwrQs"
IGDB_PROXY = f"{SB}/functions/v1/igdb-search"

FIELD_GROUPS = {
    "core": {
        "release_year",
        "igdb_rating",
        "igdb_url",
        "description",
        "storyline",
        "developer",
        "publisher",
        "primary_cover_url",
    },
    "extended": {
        "keywords",
        "screenshots",
        "themes",
        "age_rating",
        "rating_count",
        "multiplayer_info",
        "is_coop",
        "coop_notes",
    },
}


def req_json(url, headers):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read())


def patch_json(url, payload, service_key):
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
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.status


def merge_unique_strings(current_value, incoming_value, limit=None):
    current = current_value if isinstance(current_value, list) else []
    incoming = incoming_value if isinstance(incoming_value, list) else []
    merged = []
    seen = set()
    for value in current + incoming:
        clean = str(value or "").strip()
        if not clean or clean in seen:
            continue
        seen.add(clean)
        merged.append(clean)
    return merged[:limit] if limit else merged


def release_year(timestamp):
    if not timestamp:
        return None
    try:
        return datetime.fromtimestamp(timestamp, tz=timezone.utc).year
    except Exception:
        return None


def normalize_cover(url):
    if not url:
        return ""
    full = url if not url.startswith("//") else f"https:{url}"
    return full.replace("/t_thumb/", "/t_cover_big/")


def parse_age_rating(ratings):
    if not isinstance(ratings, list):
        return None
    pegi_map = {1: "3", 2: "7", 3: "12", 4: "16", 5: "18"}
    esrb_map = {6: "E", 7: "E10+", 8: "T", 9: "M", 10: "AO"}
    for row in ratings:
        if row.get("category") == 2 and pegi_map.get(row.get("rating")):
            return f"PEGI {pegi_map[row['rating']]}"
    for row in ratings:
        if row.get("category") == 1 and esrb_map.get(row.get("rating")):
            return f"ESRB {esrb_map[row['rating']]}"
    return None


def first_company(rows, key):
    for row in rows or []:
        if row.get(key) and row.get("company", {}).get("name"):
            return row["company"]["name"]
    return None


def build_description(igdb):
    summary = igdb.get("summary") or ""
    storyline = igdb.get("storyline") or ""
    parts = [summary, f"Storyline: {storyline}" if storyline else ""]
    return "\n\n".join(part for part in parts if part) or None


def build_multiplayer_signals(modes):
    signals = []
    for mode in modes or []:
        if mode.get("offlinecoop"):
            signals.append(f"Offline co-op ({mode.get('offlinecoopmax') or '?'})")
        if mode.get("onlinecoop"):
            signals.append(f"Online co-op ({mode.get('onlinecoopmax') or '?'})")
        if mode.get("offlinemax") and not mode.get("offlinecoop"):
            signals.append(f"Offline max {mode.get('offlinemax')}")
        if mode.get("onlinemax") and not mode.get("onlinecoop"):
            signals.append(f"Online max {mode.get('onlinemax')}")
    return merge_unique_strings([], signals, 12)


def get_games(title=None, limit=None, offset=None):
    select = (
        "id,title,release_year,external_id,igdb_rating,igdb_url,description,storyline,publisher,developer,"
        "primary_cover_url,is_coop,coop_notes,keywords,screenshots,themes,age_rating,rating_count,multiplayer_info"
    )
    url = f"{SB}/rest/v1/games?select={urllib.parse.quote(select)}&external_id=not.is.null&order=title"
    if title:
        url += f"&title=eq.{urllib.parse.quote(title)}"
    if limit:
        url += f"&limit={int(limit)}"
    if offset:
        url += f"&offset={int(offset)}"
    headers = {"apikey": ANON_KEY, "Authorization": f"Bearer {ANON_KEY}"}
    return req_json(url, headers)


def fetch_igdb(igdb_id):
    url = f"{IGDB_PROXY}?id={urllib.parse.quote(str(igdb_id))}"
    headers = {"Authorization": f"Bearer {ANON_KEY}", "Accept": "application/json"}
    payload = req_json(url, headers)
    results = payload.get("results", [])
    return results[0] if results else None


def normalize_igdb(igdb):
    companies = igdb.get("involved_companies") or []
    return {
        "release_year": release_year(igdb.get("first_release_date")),
        "igdb_rating": igdb.get("total_rating") or igdb.get("rating"),
        "igdb_url": igdb.get("url"),
        "description": build_description(igdb),
        "storyline": igdb.get("storyline") or None,
        "developer": first_company(companies, "developer"),
        "publisher": first_company(companies, "publisher"),
        "primary_cover_url": normalize_cover((igdb.get("cover") or {}).get("url", "")) or None,
        "keywords": [k.get("name", "") for k in (igdb.get("keywords") or []) if k.get("name")][:20],
        "screenshots": [normalize_cover(s.get("url", "")) for s in (igdb.get("screenshots") or []) if s.get("url")][:10],
        "themes": [t.get("name", "") for t in (igdb.get("themes") or []) if t.get("name")][:15],
        "age_rating": parse_age_rating(igdb.get("age_ratings") or []),
        "rating_count": igdb.get("total_rating_count") or igdb.get("rating_count"),
        "multiplayer_info": build_multiplayer_signals(igdb.get("multiplayer_modes") or []),
    }


def build_patch(game, incoming, enabled_fields):
    patch = {}

    if "release_year" in enabled_fields and game.get("release_year") is None and incoming.get("release_year") is not None:
        patch["release_year"] = incoming["release_year"]
    if "igdb_rating" in enabled_fields and game.get("igdb_rating") is None and incoming.get("igdb_rating") is not None:
        patch["igdb_rating"] = round(incoming["igdb_rating"], 2)
    if "igdb_url" in enabled_fields and not game.get("igdb_url") and incoming.get("igdb_url"):
        patch["igdb_url"] = incoming["igdb_url"]
    if "description" in enabled_fields and not game.get("description") and incoming.get("description"):
        patch["description"] = incoming["description"]
    if "storyline" in enabled_fields and not game.get("storyline") and incoming.get("storyline"):
        patch["storyline"] = incoming["storyline"]
    if "developer" in enabled_fields and not game.get("developer") and incoming.get("developer"):
        patch["developer"] = incoming["developer"]
    if "publisher" in enabled_fields and not game.get("publisher") and incoming.get("publisher"):
        patch["publisher"] = incoming["publisher"]
    if "primary_cover_url" in enabled_fields and not game.get("primary_cover_url") and incoming.get("primary_cover_url"):
        patch["primary_cover_url"] = incoming["primary_cover_url"]
    if "age_rating" in enabled_fields and not game.get("age_rating") and incoming.get("age_rating"):
        patch["age_rating"] = incoming["age_rating"]
    if "rating_count" in enabled_fields and game.get("rating_count") is None and incoming.get("rating_count") is not None:
        patch["rating_count"] = int(incoming["rating_count"])

    if "keywords" in enabled_fields:
        merged = merge_unique_strings(game.get("keywords"), incoming.get("keywords"), 20)
        if merged and merged != (game.get("keywords") or []):
            patch["keywords"] = merged
    if "screenshots" in enabled_fields:
        merged = merge_unique_strings(game.get("screenshots"), incoming.get("screenshots"), 10)
        if merged and merged != (game.get("screenshots") or []):
            patch["screenshots"] = merged
    if "themes" in enabled_fields:
        merged = merge_unique_strings(game.get("themes"), incoming.get("themes"), 15)
        if merged and merged != (game.get("themes") or []):
            patch["themes"] = merged
    if "multiplayer_info" in enabled_fields:
        merged = merge_unique_strings(game.get("multiplayer_info"), incoming.get("multiplayer_info"), 12)
        if merged and merged != (game.get("multiplayer_info") or []):
            patch["multiplayer_info"] = merged
    if "is_coop" in enabled_fields and not game.get("is_coop") and any("co-op" in s.lower() for s in incoming.get("multiplayer_info", [])):
        patch["is_coop"] = True
    if "coop_notes" in enabled_fields and not game.get("coop_notes") and incoming.get("multiplayer_info"):
        patch["coop_notes"] = " · ".join(incoming["multiplayer_info"][:5])

    if patch:
        patch["igdb_synced_at"] = datetime.now(timezone.utc).isoformat()
    return patch


def expand_fields(raw):
    if raw == "all":
        return FIELD_GROUPS["core"] | FIELD_GROUPS["extended"]
    if raw in FIELD_GROUPS:
        return set(FIELD_GROUPS[raw])
    values = {part.strip() for part in raw.split(",") if part.strip()}
    return values


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--title")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--fields", default="all", help="core | extended | all | comma list")
    parser.add_argument("--dry-run", action="store_true", help="Acikca dry-run belirtmek icin; varsayilan zaten dry-run")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--service-key")
    parser.add_argument("--sleep", type=float, default=0.15)
    parser.add_argument("--report")
    args = parser.parse_args()

    enabled_fields = expand_fields(args.fields)
    if args.apply and not args.service_key:
        raise SystemExit("--apply icin --service-key gerekli")

    games = get_games(title=args.title, limit=args.limit, offset=args.offset)
    print(f"{len(games)} oyun taranacak | fields={sorted(enabled_fields)} | mode={'APPLY' if args.apply else 'DRY-RUN'}")

    stats = Counter()
    changes = []

    for index, game in enumerate(games, start=1):
        igdb_id = game.get("external_id")
        if not igdb_id:
            stats["missing_external_id"] += 1
            continue

        try:
            igdb = fetch_igdb(igdb_id)
        except Exception as exc:
            stats["igdb_fetch_error"] += 1
            print(f"ERR [{index}] {game['title']}: {exc}")
            continue

        if not igdb:
            stats["igdb_not_found"] += 1
            continue

        incoming = normalize_igdb(igdb)
        patch = build_patch(game, incoming, enabled_fields)
        if not patch:
            stats["no_change"] += 1
            continue

        changes.append({"id": game["id"], "title": game["title"], "patch": patch})
        stats["changed_games"] += 1
        for key in patch:
            if key != "igdb_synced_at":
                stats[f"field_{key}"] += 1

        if args.apply:
            patch_json(f"{SB}/rest/v1/games?id=eq.{game['id']}", patch, args.service_key)

        print(f"{'APPLY' if args.apply else 'PLAN '} [{index}/{len(games)}] {game['title']} -> {', '.join(sorted(k for k in patch if k != 'igdb_synced_at'))}")
        if index % 25 == 0:
            print(f"PROGRESS {index}/{len(games)} | changed={stats['changed_games']} no_change={stats['no_change']}")
        time.sleep(args.sleep)

    print("\n=== OZET ===")
    for key in sorted(stats):
        print(f"{key}: {stats[key]}")

    if args.report:
        with open(args.report, "w", encoding="utf-8") as handle:
            json.dump({"stats": stats, "changes": changes}, handle, ensure_ascii=False, indent=2)
        print(f"Rapor kaydedildi: {args.report}")


if __name__ == "__main__":
    main()
