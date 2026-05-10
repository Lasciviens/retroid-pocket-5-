#!/usr/bin/env python3
"""
IGDB Repair Pass

Exact external_id / igdb_game_id kullanarak eslesmis ama metadata'si eksik
kayitlari tamamlar. Mevcut degeri ezmez; sadece bos alanlari doldurur.

Kullanim:
  python3 scripts/igdb_repair_missing.py --service-key <SERVICE_ROLE_KEY>
  python3 scripts/igdb_repair_missing.py --service-key <SERVICE_ROLE_KEY> --title "Crash: Mind Over Mutant"
"""
import argparse
import json
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone

SB = "https://bniqmxbtvgwkaoswugds.supabase.co"
ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJuaXFteGJ0dmd3a2Fvc3d1Z2RzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc4NTExMTYsImV4cCI6MjA5MzQyNzExNn0.VXjnGv3uV8A2XfAW5jOBAkxyzc9c9q6adrA64JfwrQs"
IGDB_PROXY = f"{SB}/functions/v1/igdb-search"


def req_json(url, headers):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as response:
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
    with urllib.request.urlopen(req, timeout=20) as response:
        return response.status


def release_year(timestamp):
    if not timestamp:
        return None
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).year


def first_publisher(rows):
    for row in rows or []:
        if row.get("publisher") and row.get("company", {}).get("name"):
            return row["company"]["name"]
    return None


def first_developer(rows):
    for row in rows or []:
        if row.get("developer") and row.get("company", {}).get("name"):
            return row["company"]["name"]
    return None


def get_games(title=None):
    select = (
        "id,title,release_year,external_id,igdb_rating,igdb_url,description,storyline,publisher,developer,"
        "primary_cover_url,game_platforms(id,system_id,is_preferred,cover_url,igdb_game_id,igdb_slug,igdb_url,igdb_rating,igdb_release_year,igdb_first_release_date,version_title,is_primary_variant,systems(name))"
    )
    url = f"{SB}/rest/v1/games?select={urllib.parse.quote(select)}&external_id=not.is.null&order=title"
    if title:
      url += f"&title=eq.{urllib.parse.quote(title)}"
    headers = {"apikey": ANON_KEY, "Authorization": f"Bearer {ANON_KEY}"}
    return req_json(url, headers)


def fetch_igdb(igdb_id):
    url = f"{IGDB_PROXY}?id={urllib.parse.quote(str(igdb_id))}"
    headers = {"Authorization": f"Bearer {ANON_KEY}", "Accept": "application/json"}
    payload = req_json(url, headers)
    results = payload.get("results", [])
    return results[0] if results else None


def choose_primary_variant(game, igdb):
    local_preferred = None
    for platform in game.get("game_platforms") or []:
        if platform.get("is_preferred") and platform.get("systems", {}).get("name"):
            local_preferred = platform["systems"]["name"]
            break

    variants = []
    for platform in igdb.get("platforms") or []:
        name = platform.get("abbreviation") or platform.get("name")
        variants.append(
            {
                "platform": name,
                "igdb_game_id": igdb.get("id"),
                "igdb_slug": igdb.get("slug"),
                "igdb_url": igdb.get("url"),
                "igdb_rating": igdb.get("total_rating") or igdb.get("rating"),
                "igdb_release_year": release_year(igdb.get("first_release_date")),
                "igdb_first_release_date": datetime.fromtimestamp(igdb["first_release_date"], tz=timezone.utc).isoformat() if igdb.get("first_release_date") else None,
                "version_title": igdb.get("name"),
                "cover_url": ((igdb.get("cover") or {}).get("url") or "").replace("//", "https://").replace("/t_thumb/", "/t_cover_big/"),
                "is_primary_variant": False,
            }
        )

    if variants:
        chosen = None
        if local_preferred:
            chosen = next((variant for variant in variants if variant["platform"] == local_preferred), None)
        if not chosen:
            chosen = variants[0]
        chosen["is_primary_variant"] = True
    return variants


def build_description(igdb):
    summary = igdb.get("summary") or ""
    storyline = igdb.get("storyline") or ""
    parts = [part for part in [summary, f"Storyline: {storyline}" if storyline else ""] if part]
    return "\n\n".join(parts) if parts else None


def repair_game(game, igdb, service_key):
    variants = choose_primary_variant(game, igdb)
    primary = next((variant for variant in variants if variant["is_primary_variant"]), variants[0] if variants else {})
    canonical_patch = {"igdb_synced_at": datetime.now(timezone.utc).isoformat()}

    if game.get("release_year") is None and primary.get("igdb_release_year") is not None:
        canonical_patch["release_year"] = primary["igdb_release_year"]
    if game.get("igdb_rating") is None and primary.get("igdb_rating") is not None:
        canonical_patch["igdb_rating"] = round(primary["igdb_rating"], 2)
    if not game.get("igdb_url") and primary.get("igdb_url"):
        canonical_patch["igdb_url"] = primary["igdb_url"]
    if not game.get("description"):
        description = build_description(igdb)
        if description:
            canonical_patch["description"] = description
    if not game.get("storyline") and igdb.get("storyline"):
        canonical_patch["storyline"] = igdb["storyline"]
    if not game.get("publisher"):
        publisher = first_publisher(igdb.get("involved_companies") or [])
        if publisher:
            canonical_patch["publisher"] = publisher
    if not game.get("developer"):
        developer = first_developer(igdb.get("involved_companies") or [])
        if developer:
            canonical_patch["developer"] = developer
    if not game.get("primary_cover_url") and primary.get("cover_url"):
        canonical_patch["primary_cover_url"] = primary["cover_url"]

    if len(canonical_patch) > 1:
        patch_json(f"{SB}/rest/v1/games?id=eq.{game['id']}", canonical_patch, service_key)

    local_platforms = game.get("game_platforms") or []
    for local_platform in local_platforms:
        system_name = local_platform.get("systems", {}).get("name")
        variant = next((row for row in variants if row["platform"] == system_name), None)
        if not variant:
            continue
        patch = {}
        if not local_platform.get("igdb_game_id") and variant.get("igdb_game_id"):
            patch["igdb_game_id"] = variant["igdb_game_id"]
        if not local_platform.get("igdb_slug") and variant.get("igdb_slug"):
            patch["igdb_slug"] = variant["igdb_slug"]
        if not local_platform.get("igdb_url") and variant.get("igdb_url"):
            patch["igdb_url"] = variant["igdb_url"]
        if local_platform.get("igdb_rating") is None and variant.get("igdb_rating") is not None:
            patch["igdb_rating"] = round(variant["igdb_rating"], 2)
        if local_platform.get("igdb_release_year") is None and variant.get("igdb_release_year") is not None:
            patch["igdb_release_year"] = variant["igdb_release_year"]
        if not local_platform.get("igdb_first_release_date") and variant.get("igdb_first_release_date"):
            patch["igdb_first_release_date"] = variant["igdb_first_release_date"]
        if not local_platform.get("version_title") and variant.get("version_title"):
            patch["version_title"] = variant["version_title"]
        if not local_platform.get("cover_url") and variant.get("cover_url"):
            patch["cover_url"] = variant["cover_url"]
        if variant.get("is_primary_variant") and not local_platform.get("is_primary_variant"):
            patch["is_primary_variant"] = True
        if patch:
            patch_json(f"{SB}/rest/v1/game_platforms?id=eq.{local_platform['id']}", patch, service_key)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--service-key", required=True)
    parser.add_argument("--title")
    args = parser.parse_args()

    games = get_games(args.title)
    print(f"{len(games)} oyun kontrol ediliyor")
    updated = 0
    skipped = 0

    for game in games:
        missing = any(
            [
                game.get("release_year") is None,
                game.get("igdb_rating") is None,
                not game.get("publisher"),
                not game.get("storyline"),
            ]
        )
        if not missing:
            skipped += 1
            continue
        igdb = fetch_igdb(game.get("external_id"))
        if not igdb:
            print(f"✗ {game['title']} => IGDB bulunamadi")
            continue
        repair_game(game, igdb, args.service_key)
        updated += 1
        print(f"✓ {game['title']}")
        time.sleep(0.25)

    print(f"Tamam: {updated} guncellendi / {skipped} zaten doluydu")


if __name__ == "__main__":
    main()
