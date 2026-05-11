#!/usr/bin/env python3
"""
IGDB Bulk Matcher — canonical game + platform variants

Kullanim:
  python3 scripts/igdb_bulk_match.py
  python3 scripts/igdb_bulk_match.py --all
  python3 scripts/igdb_bulk_match.py --output igdb_dry_run_variants.json
  python3 scripts/igdb_bulk_match.py --apply SERVICE_ROLE_KEY
"""
import argparse
import json
import re
import time
import unicodedata
import urllib.parse
import urllib.request
from datetime import datetime, timezone

SB_URL = "https://bniqmxbtvgwkaoswugds.supabase.co"
ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJuaXFteGJ0dmd3a2Fvc3d1Z2RzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc4NTExMTYsImV4cCI6MjA5MzQyNzExNn0.VXjnGv3uV8A2XfAW5jOBAkxyzc9c9q6adrA64JfwrQs"
IGDB_PROXY = f"{SB_URL}/functions/v1/igdb-search"

SYSTEM_IGDB_MAP = {
    "PS1": ["PS", "PlayStation", "PS1", "PSN"],
    "PS2": ["PS2", "PlayStation 2"],
    "PSP": ["PSP", "PlayStation Portable"],
    "GBA": ["GBA", "Game Boy Advance"],
    "GBC": ["GBC", "Game Boy Color"],
    "DS": ["NDS", "Nintendo DS"],
    "3DS": ["3DS", "Nintendo 3DS"],
    "N64": ["N64", "Nintendo 64"],
    "GameCube": ["NGC", "GameCube", "Nintendo GameCube"],
    "Wii": ["Wii"],
    "SNES": ["SNES", "Super Nintendo", "SFAM"],
    "NES": ["NES", "Nintendo Entertainment System", "Famicom"],
    "Genesis": ["GEN", "Sega Genesis", "Sega Mega Drive", "Genesis", "Mega Drive"],
    "Dreamcast": ["DC", "Dreamcast"],
    "PC": ["PC", "Windows", "Linux", "Mac"],
}

MIN_SCORE = 90
AMBIGUITY_GAP = 8


def normalize(text):
    text = (text or "").lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = re.sub(r"[^a-z0-9]+", " ", text).strip()
    return text


def unique_list(values):
    out = []
    seen = set()
    for value in values or []:
        if not value or value in seen:
            continue
        seen.add(value)
        out.append(value)
    return out


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


def score_match(query, item_name, item_year, expected_year):
    qn = normalize(query)
    nn = normalize(item_name)
    if not qn or not nn:
        return 0

    score = 0
    if qn == nn:
        score += 82
    elif nn.startswith(qn) or qn.startswith(nn):
        score += 58
    elif qn in nn or nn in qn:
        score += 44

    q_tokens = qn.split()
    n_tokens = nn.split()
    hits = sum(1 for token in q_tokens if token in set(n_tokens))
    if q_tokens:
        score += round(hits / len(q_tokens) * 12)
    if qn != nn:
        score -= max(0, len(n_tokens) - len(q_tokens)) * 8

    if expected_year and item_year:
        diff = abs(int(expected_year) - int(item_year))
        if diff == 0:
            score += 22
        elif diff == 1:
            score += 14
        elif diff <= 3:
            score += 6
        elif diff <= 8:
            score -= 10
        else:
            score -= 22

    return max(0, min(100, score))


def platform_overlap(local_systems, igdb_platforms):
    for system_name in local_systems:
        keywords = SYSTEM_IGDB_MAP.get(system_name, [system_name])
        for keyword in keywords:
            kw_low = keyword.lower()
            for platform in igdb_platforms:
                p_low = platform.lower()
                if kw_low in p_low or p_low in kw_low:
                    return True
    return False


def normalize_platform_name(value):
    raw = (value or "").strip()
    aliases = {
        "playstation": "PS1",
        "playstation 2": "PS2",
        "playstation portable": "PSP",
        "nintendo 64": "N64",
        "nintendo gamecube": "GameCube",
        "gamecube": "GameCube",
        "super nintendo entertainment system": "SNES",
        "nintendo entertainment system": "NES",
        "sega genesis": "Genesis",
        "sega mega drive/genesis": "Genesis",
        "game boy advance": "GBA",
        "game boy color": "GBC",
        "nintendo ds": "DS",
        "nintendo 3ds": "3DS",
        "windows pc": "PC",
        "pc (microsoft windows)": "PC",
    }
    return aliases.get(raw.lower(), raw)


def release_year_from_ts(timestamp):
    if not timestamp:
        return None
    try:
        return datetime.fromtimestamp(timestamp, tz=timezone.utc).year
    except Exception:
        return None


def iso_from_ts(timestamp):
    if not timestamp:
        return None
    try:
        return datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()
    except Exception:
        return None


def normalize_cover(url):
    if not url:
        return ""
    full = url if not url.startswith("//") else f"https:{url}"
    return full.replace("/t_thumb/", "/t_cover_big/")


def igdb_search(title):
    url = f"{IGDB_PROXY}?title={urllib.parse.quote(title)}"
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {ANON_KEY}", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=15) as response:
        payload = json.loads(response.read())
    return payload.get("results", [])


def process_igdb_result(row):
    company_rows = row.get("involved_companies") or []
    developers = [r.get("company", {}).get("name") for r in company_rows if r.get("developer")]
    publishers = [r.get("company", {}).get("name") for r in company_rows if r.get("publisher")]
    platforms = [(p.get("abbreviation") or p.get("name") or "").strip() for p in (row.get("platforms") or [])]
    return {
        "id": row.get("id"),
        "name": row.get("name", ""),
        "slug": row.get("slug", ""),
        "summary": row.get("summary", ""),
        "storyline": row.get("storyline", ""),
        "year": release_year_from_ts(row.get("first_release_date")),
        "first_release_date": row.get("first_release_date"),
        "platforms": unique_list(platforms),
        "genres": unique_list([g.get("name") for g in (row.get("genres") or [])]),
        "themes": unique_list([g.get("name") for g in (row.get("themes") or [])]),
        "keywords": unique_list([g.get("name") for g in (row.get("keywords") or [])]),
        "cover_url": normalize_cover((row.get("cover") or {}).get("url", "")),
        "rating": row.get("total_rating") or row.get("rating"),
        "rating_count": row.get("total_rating_count"),
        "developers": unique_list(developers),
        "publishers": unique_list(publishers),
        "franchises": unique_list([f.get("name") for f in (row.get("franchises") or [])]),
        "collections": unique_list([c.get("name") for c in (row.get("collections") or [])]),
        "screenshots": unique_list([normalize_cover(s.get("url", "")) for s in (row.get("screenshots") or [])]),
        "videos": unique_list([f"https://www.youtube.com/watch?v={v.get('video_id')}" for v in (row.get("videos") or []) if v.get("video_id")]),
        "websites": unique_list([w.get("url") for w in (row.get("websites") or []) if w.get("url")]),
        "igdb_url": row.get("url", ""),
        "multiplayer_signals": build_multiplayer_signals(row.get("multiplayer_modes") or []),
    }


def build_multiplayer_signals(modes):
    signals = []
    for mode in modes:
        if mode.get("offlinecoop"):
            signals.append(f"Offline co-op ({mode.get('offlinecoopmax') or '?'})")
        if mode.get("onlinecoop"):
            signals.append(f"Online co-op ({mode.get('onlinecoopmax') or '?'})")
        if mode.get("offlinemax"):
            signals.append(f"Offline max {mode.get('offlinemax')}")
        if mode.get("onlinemax"):
            signals.append(f"Online max {mode.get('onlinemax')}")
    return unique_list(signals)


def fetch_games_without_external_id(limit=None):
    select = (
        "id,title,release_year,description,developer,publisher,storyline,igdb_rating,igdb_url,"
        "primary_cover_url,external_id,is_coop,coop_notes,themes,age_rating,rating_count,multiplayer_info,keywords,screenshots,"
        "game_genres(genres(name)),"
        "game_platforms(id,system_id,is_preferred,cover_url,systems(name),igdb_game_id)"
    )
    params = f"select={urllib.parse.quote(select)}&external_id=is.null&order=title"
    if limit:
        params += f"&limit={limit}"
    url = f"{SB_URL}/rest/v1/games?{params}"
    req = urllib.request.Request(
        url,
        headers={"apikey": ANON_KEY, "Authorization": f"Bearer {ANON_KEY}"},
    )
    with urllib.request.urlopen(req, timeout=20) as response:
        return json.loads(response.read())


def normalize_payload(item, local_game):
    raw_platforms = unique_list([normalize_platform_name(name) for name in item.get("platforms", []) if name])
    local_systems = [p["systems"]["name"] for p in local_game.get("game_platforms", []) if p.get("systems")]
    preferred_platform = next((p["systems"]["name"] for p in local_game.get("game_platforms", []) if p.get("is_preferred") and p.get("systems")), "")
    primary_platform = preferred_platform if preferred_platform in raw_platforms else (raw_platforms[0] if raw_platforms else "")
    return {
        "canonical_game": {
            "title": item.get("name", ""),
            "summary": item.get("summary", ""),
            "storyline": item.get("storyline", ""),
            "developer": item.get("developers", [""])[0] if item.get("developers") else "",
            "publisher": item.get("publishers", [""])[0] if item.get("publishers") else "",
            "franchise": item.get("franchises", [""])[0] if item.get("franchises") else "",
            "collection": item.get("collections", [""])[0] if item.get("collections") else "",
            "genres": item.get("genres", []),
            "themes": item.get("themes", []),
            "keywords": item.get("keywords", []),
            "websites": item.get("websites", []),
            "screenshots": item.get("screenshots", []),
            "videos": item.get("videos", []),
            "multiplayer_signals": item.get("multiplayer_signals", []),
        },
        "platform_variants": [
            {
                "platform": platform,
                "igdb_game_id": item.get("id"),
                "igdb_slug": item.get("slug", ""),
                "igdb_url": item.get("igdb_url", ""),
                "release_year": item.get("year"),
                "first_release_date": item.get("first_release_date"),
                "rating": item.get("rating"),
                "rating_count": item.get("rating_count"),
                "cover_url": item.get("cover_url", ""),
                "version_title": item.get("name", ""),
                "multiplayer_signals": item.get("multiplayer_signals", []),
                "is_primary_variant": platform == primary_platform,
            }
            for platform in raw_platforms
        ],
        "local_systems": local_systems,
    }


def build_description(item):
    pieces = [item.get("summary", "")]
    if item.get("storyline"):
        pieces.append(f"Storyline: {item['storyline']}")
    text = "\n\n".join(piece for piece in pieces if piece)
    return text or None


def build_canonical_patch(game, normalized, item):
    patch = {"igdb_synced_at": datetime.now(timezone.utc).isoformat()}
    canonical = normalized["canonical_game"]
    primary = next((v for v in normalized["platform_variants"] if v["is_primary_variant"]), normalized["platform_variants"][0] if normalized["platform_variants"] else {})
    if not game.get("external_id") and primary.get("igdb_game_id"):
        patch["external_id"] = str(primary["igdb_game_id"])
    if not game.get("description") and build_description(item):
        patch["description"] = build_description(item)
    if not game.get("developer") and canonical.get("developer"):
        patch["developer"] = canonical["developer"]
    if not game.get("publisher") and canonical.get("publisher"):
        patch["publisher"] = canonical["publisher"]
    if not game.get("storyline") and canonical.get("storyline"):
        patch["storyline"] = canonical["storyline"]
    if game.get("igdb_rating") is None and primary.get("rating") is not None:
        patch["igdb_rating"] = primary["rating"]
    if not game.get("igdb_url") and primary.get("igdb_url"):
        patch["igdb_url"] = primary["igdb_url"]
    if not game.get("primary_cover_url") and primary.get("cover_url"):
        patch["primary_cover_url"] = primary["cover_url"]
    if not game.get("release_year") and primary.get("release_year"):
        patch["release_year"] = primary["release_year"]
    if item.get("name") and item["name"] != game["title"]:
        patch["title"] = item["name"]
    if not game.get("is_coop") and normalized["canonical_game"].get("multiplayer_signals"):
        patch["is_coop"] = any("co-op" in signal.lower() for signal in normalized["canonical_game"]["multiplayer_signals"])
    if not game.get("coop_notes") and normalized["canonical_game"].get("multiplayer_signals"):
        patch["coop_notes"] = " · ".join(normalized["canonical_game"]["multiplayer_signals"])
    if not game.get("age_rating") and item.get("age_rating"):
        patch["age_rating"] = item["age_rating"]
    if game.get("rating_count") is None and item.get("rating_count") is not None:
        patch["rating_count"] = item["rating_count"]
    themes = merge_unique_strings(game.get("themes"), canonical.get("themes"))
    if themes:
        patch["themes"] = themes
    keywords = merge_unique_strings(game.get("keywords"), canonical.get("keywords"), 20)
    if keywords:
        patch["keywords"] = keywords
    screenshots = merge_unique_strings(game.get("screenshots"), canonical.get("screenshots"), 10)
    if screenshots:
        patch["screenshots"] = screenshots
    multiplayer = merge_unique_strings(game.get("multiplayer_info"), canonical.get("multiplayer_signals"), 12)
    if multiplayer:
        patch["multiplayer_info"] = multiplayer
    return patch


def build_variant_patches(local_game, normalized):
    variants = normalized["platform_variants"]
    local_platforms = local_game.get("game_platforms") or []
    patches = []
    for local_platform in local_platforms:
        system_name = local_platform.get("systems", {}).get("name")
        match = next((variant for variant in variants if variant["platform"] == system_name), None)
        if not match:
            continue
        patches.append(
            {
                "id": local_platform["id"],
                "payload": {
                    "igdb_game_id": match["igdb_game_id"],
                    "igdb_slug": match["igdb_slug"] or None,
                    "igdb_url": match["igdb_url"] or None,
                    "igdb_rating": match["rating"],
                    "igdb_release_year": match["release_year"],
                    "igdb_first_release_date": iso_from_ts(match["first_release_date"]),
                    "version_title": match["version_title"] or None,
                    "is_primary_variant": bool(match["is_primary_variant"]),
                    "cover_url": local_platform.get("cover_url") or match["cover_url"] or None,
                },
            }
        )
    return patches


def apply_patch_request(table_path, payload, service_key):
    url = f"{SB_URL}/rest/v1/{table_path}"
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url,
        data=data,
        method="PATCH",
        headers={
            "apikey": service_key,
            "Authorization": f"Bearer {service_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        },
    )
    with urllib.request.urlopen(req, timeout=15) as response:
        return response.status


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--apply", metavar="SERVICE_ROLE_KEY")
    parser.add_argument("--output", metavar="FILE")
    args = parser.parse_args()

    limit = None if args.all else args.limit
    games = fetch_games_without_external_id(limit)
    matches = []
    no_match = []
    no_overlap = []
    ambiguous = []

    print(f"{len(games)} oyun taraniyor")
    for index, game in enumerate(games, start=1):
        title = game["title"]
        year = game.get("release_year")
        local_systems = [p["systems"]["name"] for p in (game.get("game_platforms") or []) if p.get("systems")]
        print(f"[{index}/{len(games)}] {title}", end=" ", flush=True)

        try:
            results = igdb_search(title)
        except Exception as exc:
            print(f"=> IGDB hatasi: {exc}")
            no_match.append({"title": title, "reason": f"igdb_error: {exc}"})
            continue

        if not results:
            print("=> sonuc yok")
            no_match.append({"title": title, "reason": "no_results"})
            continue

        scored = []
        for raw in results[:12]:
            item = process_igdb_result(raw)
            scored.append((score_match(title, item["name"], item["year"], year), item))
        scored.sort(key=lambda row: -row[0])

        best_score, best = scored[0]
        second_score = scored[1][0] if len(scored) > 1 else 0
        if best_score < MIN_SCORE:
            print(f"=> dusuk skor {best_score}")
            no_match.append({"title": title, "reason": f"low_score_{best_score}", "best": best["name"]})
            continue
        if (best_score - second_score) < AMBIGUITY_GAP and second_score > 50:
            print(f"=> belirsiz {best_score}/{second_score}")
            ambiguous.append({"title": title, "top1": best["name"], "score1": best_score, "top2": scored[1][1]["name"], "score2": second_score})
            continue
        if local_systems and not platform_overlap(local_systems, best["platforms"]):
            print("=> platform overlap yok")
            no_overlap.append({"title": title, "igdb": best["name"], "local_systems": local_systems, "igdb_platforms": best["platforms"]})
            continue

        normalized = normalize_payload(best, game)
        canonical_patch = build_canonical_patch(game, normalized, best)
        variant_patches = build_variant_patches(game, normalized)

        matches.append(
            {
                "game_id": game["id"],
                "title": title,
                "score": best_score,
                "igdb_name": best["name"],
                "canonical_patch": canonical_patch,
                "variant_patches": variant_patches,
                "normalized": normalized,
            }
        )
        print(f'=> eslesme {best_score} "{best["name"]}"')
        time.sleep(0.35)

    print(f"\nESLESME {len(matches)} | DUSUK {len(no_match)} | OVERLAP {len(no_overlap)} | BELIRSIZ {len(ambiguous)}")

    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            json.dump(
                {
                    "matches": matches,
                    "no_match": no_match,
                    "no_overlap": no_overlap,
                    "ambiguous": ambiguous,
                },
                handle,
                ensure_ascii=False,
                indent=2,
            )
        print(f"Kaydedildi: {args.output}")

    if args.apply and matches:
        success = 0
        fail = 0
        for match in matches:
            try:
                apply_patch_request(f"games?id=eq.{match['game_id']}", match["canonical_patch"], args.apply)
                for variant in match["variant_patches"]:
                    apply_patch_request(f"game_platforms?id=eq.{variant['id']}", variant["payload"], args.apply)
                success += 1
                print(f"✓ {match['title']}")
            except Exception as exc:
                fail += 1
                print(f"✗ {match['title']} => {exc}")
            time.sleep(0.2)
        print(f"Apply tamamlandi: {success} basarili / {fail} hatali")
    elif not args.apply:
        print("[DRY-RUN] Yazmak icin --apply <SERVICE_ROLE_KEY>")


if __name__ == "__main__":
    main()
