#!/usr/bin/env python3
"""
IGDB Top List Import
Verilen oyun+platform listesini IGDB'den cekip DB'ye yazar.
Varsa platform variant ekler, yoksa yeni oyun olusturur.
"""
import json, re, time, unicodedata, urllib.parse, urllib.request, uuid

SB   = 'https://bniqmxbtvgwkaoswugds.supabase.co'
KEY  = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJuaXFteGJ0dmd3a2Fvc3d1Z2RzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3Nzg1MTExNiwiZXhwIjoyMDkzNDI3MTE2fQ.j7fQEewwxb_IRicNOmYTwsEJONvHbrj3TvqGyNozVwM'
ANON = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJuaXFteGJ0dmd3a2Fvc3d1Z2RzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc4NTExMTYsImV4cCI6MjA5MzQyNzExNn0.VXjnGv3uV8A2XfAW5jOBAkxyzc9c9q6adrA64JfwrQs'
IGDB_PROXY = f'{SB}/functions/v1/igdb-search'

SYSTEM_IDS = {
    'GameCube': 8, 'N64': 7, 'PS1': 1, 'PS2': 2, 'PSP': 3,
    'GBA': 4, 'DS': 5, '3DS': 6, 'Wii': 9, 'SNES': 10,
    'NES': 11, 'Genesis': 12, 'Dreamcast': 13, 'PC': 15,
}

SYSTEM_IGDB_MAP = {
    'GameCube': ['NGC', 'GameCube', 'Nintendo GameCube'],
    'N64':      ['N64', 'Nintendo 64'],
    'PS1':      ['PS', 'PlayStation', 'PS1', 'PSN'],
    'PS2':      ['PS2', 'PlayStation 2'],
    'PSP':      ['PSP', 'PlayStation Portable'],
}

# Oyun + platform listesi
IMPORT_LIST = [
    # GameCube
    ("Tales of Symphonia",                          "GameCube"),
    ("NBA Street",                                  "GameCube"),
    ("Beyond Good & Evil",                          "GameCube"),
    ("Star Wars: Rogue Squadron II - Rogue Leader", "GameCube"),
    ("TimeSplitters: Future Perfect",               "GameCube"),
    ("Tom Clancy's Splinter Cell: Chaos Theory",    "GameCube"),
    ("Fire Emblem: Path of Radiance",               "GameCube"),
    ("Star Wars: Jedi Knight II - Jedi Outcast",    "GameCube"),
    ("Resident Evil 2",                             "GameCube"),
    ("SpongeBob SquarePants: Battle for Bikini Bottom", "GameCube"),
    ("Need for Speed: Underground",                 "GameCube"),
    ("Eternal Darkness: Sanity's Requiem",          "GameCube"),
    # N64
    ("Perfect Dark",                                "N64"),
    ("Banjo-Tooie",                                 "N64"),
    ("GoldenEye 007",                               "N64"),
    ("Star Fox 64",                                 "N64"),
    ("Banjo-Kazooie",                               "N64"),
    ("Command & Conquer",                           "N64"),
    ("Worms Armageddon",                            "N64"),
    ("Conker's Bad Fur Day",                        "N64"),
    ("FIFA: Road to World Cup 98",                  "N64"),
    ("Rayman 2: The Great Escape",                  "N64"),
    ("FIFA 99",                                     "N64"),
    ("Diddy Kong Racing",                           "N64"),
    ("F-Zero X",                                    "N64"),
    ("Re-Volt",                                     "N64"),
    ("Tom Clancy's Rainbow Six",                    "N64"),
    # PS2
    ("Silent Hill 2",                               "PS2"),
    ("Metal Gear Solid 2: Sons of Liberty",         "PS2"),
    ("Half-Life",                                   "PS2"),
    ("NBA 2K11",                                    "PS2"),
    ("Katamari Damacy",                             "PS2"),
    ("Rock Band 2",                                 "PS2"),
    ("Mafia",                                       "PS2"),
    ("NBA Street",                                  "PS2"),
    ("Age of Empires II: The Age of Kings",         "PS2"),
    ("Oni",                                         "PS2"),
    ("Max Payne 2: The Fall of Max Payne",          "PS2"),
    ("Max Payne",                                   "PS2"),
    # PSP
    ("Steins;Gate",                                 "PSP"),
    ("Suikoden II",                                 "PSP"),
    ("NBA 2K11",                                    "PSP"),
    ("Xenogears",                                   "PSP"),
    ("R4: Ridge Racer Type 4",                      "PSP"),
    ("The Legend of Heroes: Trails in the Sky",     "PSP"),
    ("Final Fantasy Tactics",                       "PSP"),
    ("Star Wars: Battlefront II",                   "PSP"),
    ("Chrono Cross",                                "PSP"),
    ("Command & Conquer: Red Alert",                "PSP"),
    ("Silent Hill",                                 "PSP"),
    ("Suikoden",                                    "PSP"),
    ("Resident Evil 2",                             "PSP"),
    ("Oddworld: Abe's Exoddus",                     "PSP"),
    ("The Legend of Dragoon",                       "PSP"),
    ("Breath of Fire IV",                           "PSP"),
    ("Danganronpa 2: Goodbye Despair",              "PSP"),
    ("Parasite Eve",                                "PSP"),
]

def normalize(text):
    text = (text or '').lower()
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9]+', ' ', text).strip()

def igdb_search(title):
    url = f'{IGDB_PROXY}?title={urllib.parse.quote(title)}'
    req = urllib.request.Request(url, headers={'Authorization': f'Bearer {ANON}', 'Accept': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=12) as r:
            return json.loads(r.read()).get('results', [])
    except Exception as e:
        print(f'    IGDB hata: {e}')
        return []

def score(query, igdb_name, igdb_year, our_year):
    qn, nn = normalize(query), normalize(igdb_name)
    if not qn or not nn: return 0
    s = 0
    if qn == nn:                              s += 82
    elif nn.startswith(qn) or qn.startswith(nn): s += 58
    elif qn in nn or nn in qn:               s += 44
    hits = sum(1 for t in qn.split() if t in set(nn.split()))
    if qn.split(): s += round(hits / len(qn.split()) * 12)
    s -= max(0, len(nn.split()) - len(qn.split())) * 8
    if igdb_year and our_year:
        d = abs(int(igdb_year) - int(our_year))
        s += [22,14,6,0,0,-10,-22][min(d,6)] if d < 7 else -22
    return max(0, min(100, s))

def platform_match(system, igdb_platforms):
    kws = SYSTEM_IGDB_MAP.get(system, [system])
    return any(kw.lower() in p.lower() or p.lower() in kw.lower()
               for kw in kws for p in igdb_platforms)

def release_year(ts):
    if not ts: return None
    from datetime import datetime, timezone
    try: return datetime.fromtimestamp(ts, tz=timezone.utc).year
    except: return None

def normalize_cover(url):
    if not url: return ''
    full = url if not url.startswith('//') else f'https:{url}'
    return full.replace('/t_thumb/', '/t_cover_big/')

def sb_get(path):
    req = urllib.request.Request(f'{SB}/rest/v1/{path}',
        headers={'apikey': KEY, 'Authorization': f'Bearer {KEY}'})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())

def sb_post(path, data):
    body = json.dumps(data).encode()
    req = urllib.request.Request(f'{SB}/rest/v1/{path}', data=body, method='POST',
        headers={'apikey': KEY, 'Authorization': f'Bearer {KEY}',
                 'Content-Type': 'application/json', 'Prefer': 'return=representation'})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())

def sb_patch(path, data):
    body = json.dumps(data).encode()
    req = urllib.request.Request(f'{SB}/rest/v1/{path}', data=body, method='PATCH',
        headers={'apikey': KEY, 'Authorization': f'Bearer {KEY}',
                 'Content-Type': 'application/json', 'Prefer': 'return=minimal'})
    with urllib.request.urlopen(req, timeout=10) as r:
        return r.status

def get_existing_games():
    games = sb_get('games?select=id,title,external_id,series_id,release_year&order=title')
    return {normalize(g['title']): g for g in games}

def get_existing_platforms(game_id):
    rows = sb_get(f'game_platforms?select=id,system_id&game_id=eq.{game_id}')
    return {r['system_id'] for r in rows}

def main():
    print('Mevcut oyunlar yükleniyor...')
    existing = get_existing_games()
    print(f'  {len(existing)} oyun DB\'de\n')

    inserted = updated = skipped = failed = 0

    # Tekrar önleme: aynı (title, system) ikilisini bir kez işle
    seen = set()

    for title, system in IMPORT_LIST:
        key = (normalize(title), system)
        if key in seen:
            continue
        seen.add(key)

        sys_id = SYSTEM_IDS.get(system)
        if not sys_id:
            print(f'  [SKIP] Bilinmeyen sistem: {system}')
            skipped += 1
            continue

        print(f'  {title} ({system})', end=' ... ', flush=True)

        # IGDB'den ara
        results = igdb_search(title)
        time.sleep(0.35)

        if not results:
            print('IGDB sonuç yok')
            skipped += 1
            continue

        # En iyi eşleşmeyi bul (platform + skor)
        best = None
        best_score = 0
        for r in results[:8]:
            platforms = [p.get('abbreviation') or p.get('name', '') for p in (r.get('platforms') or [])]
            yr = release_year(r.get('first_release_date'))
            s = score(title, r.get('name', ''), yr, None)
            plat_ok = platform_match(system, platforms)
            # Platform eşleşmesi varsa bonus
            if plat_ok: s = min(100, s + 5)
            if s > best_score:
                best_score = s
                best = r

        if not best or best_score < 75:
            print(f'düşük skor ({best_score})')
            skipped += 1
            continue

        igdb_id   = best.get('id')
        igdb_name = best.get('name', title)
        igdb_slug = best.get('slug', '')
        igdb_url  = best.get('url') or (f'https://www.igdb.com/games/{igdb_slug}' if igdb_slug else '')
        yr        = release_year(best.get('first_release_date'))
        rating    = best.get('total_rating') or best.get('rating')
        cover     = normalize_cover((best.get('cover') or {}).get('url', ''))
        summary   = best.get('summary', '')
        genres    = [g.get('name', '') for g in (best.get('genres') or [])]
        # DB'de var mı?
        norm_key = normalize(igdb_name)
        norm_our = normalize(title)
        game_row = existing.get(norm_key) or existing.get(norm_our)

        if game_row:
            game_id = game_row['id']
            # Platform zaten ekli mi?
            existing_plats = get_existing_platforms(game_id)
            if sys_id in existing_plats:
                print(f'zaten var ({igdb_name})')
                skipped += 1
                continue
            # Platform variant ekle
            variant = {
                'game_id':    game_id,
                'system_id':  sys_id,
                'rom_status': 'missing',
                'igdb_game_id': igdb_id,
                'igdb_slug':    igdb_slug,
                'igdb_url':     igdb_url,
                'igdb_rating':  round(float(rating), 2) if rating else None,
                'igdb_release_year': yr,
                'is_primary_variant': False,
            }
            try:
                sb_post('game_platforms', variant)
                print(f'platform eklendi → {game_row["title"]} ({igdb_name}, skor:{best_score})')
                updated += 1
            except Exception as e:
                print(f'PLATFORM HATA: {e}')
                failed += 1
        else:
            # Yeni oyun + platform
            new_game = {
                'title':             igdb_name,
                'release_year':      yr,
                'description':       summary,
                'primary_cover_url': cover,
                'external_id':       str(igdb_id),
                'igdb_rating':       round(float(rating), 2) if rating else None,
                'igdb_url':          igdb_url,
                'play_status':       'backlog',
            }
            try:
                created = sb_post('games', new_game)
                new_id = created[0]['id']

                # Genre bağlantıları
                for gname in genres:
                    try:
                        genre_rows = sb_get(f'genres?select=id&name=eq.{urllib.parse.quote(gname)}')
                        if genre_rows:
                            sb_post('game_genres', {'game_id': new_id, 'genre_id': genre_rows[0]['id']})
                    except: pass

                # Platform variant
                variant = {
                    'game_id':    new_id,
                    'system_id':  sys_id,
                    'rom_status': 'missing',
                    'igdb_game_id': igdb_id,
                    'igdb_slug':    igdb_slug,
                    'igdb_url':     igdb_url,
                    'igdb_rating':  round(float(rating), 2) if rating else None,
                    'igdb_release_year': yr,
                    'is_primary_variant': True,
                }
                sb_post('game_platforms', variant)

                existing[normalize(igdb_name)] = {'id': new_id, 'title': igdb_name}
                print(f'YENİ → "{igdb_name}" ({yr}, {system}, skor:{best_score})')
                inserted += 1
            except Exception as e:
                print(f'INSERT HATA: {e}')
                failed += 1

        time.sleep(0.35)

    print(f'\n{"="*55}')
    print(f'Yeni oyun    : {inserted}')
    print(f'Platform eklendi: {updated}')
    print(f'Atlanan      : {skipped}')
    print(f'Hata         : {failed}')

if __name__ == '__main__':
    main()
