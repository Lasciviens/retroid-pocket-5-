#!/usr/bin/env python3
"""
Retroid DB Audit Report

v_games_audit ve v_game_platform_audit view'larından veri okur,
özet rapor üretir. Read-only, write yapmaz.

Kullanim:
  python3 scripts/audit_report.py
  python3 scripts/audit_report.py --format markdown > audit.md
  python3 scripts/audit_report.py --title "Metal Gear Solid"
  python3 scripts/audit_report.py --max-score 70
  python3 scripts/audit_report.py --issue no_igdb_rating
"""

import argparse
import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime

SB       = "https://bniqmxbtvgwkaoswugds.supabase.co"
ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJuaXFteGJ0dmd3a2Fvc3d1Z2RzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc4NTExMTYsImV4cCI6MjA5MzQyNzExNn0.VXjnGv3uV8A2XfAW5jOBAkxyzc9c9q6adrA64JfwrQs"
HEADERS  = {"apikey": ANON_KEY, "Authorization": f"Bearer {ANON_KEY}"}

# Issue catalog: code -> (severity, label, fix_type, description)
ISSUE_CATALOG = {
    # P1 Critical
    "no_external_id":       ("P1", "No IGDB ID",              "manual",  "IGDB match bulunamadı, enrich imkansız"),
    "no_primary_variant":   ("P1", "No Primary Variant",      "auto",    "UI hangi platformu göstereceğini bilmiyor"),
    "multiple_primaries":   ("P1", "Multiple Primaries",      "manual",  "Unique constraint ihlali — sadece 1 olmalı"),
    # P2 Important
    "no_release_year":      ("P2", "No Release Year",         "auto",    "Sıralama ve filtreler bozuk"),
    "no_publisher":         ("P2", "No Publisher",            "auto",    "Metadata eksik"),
    "no_description":       ("P2", "No Description",          "auto",    "Modal içeriği boş"),
    "no_igdb_rating":       ("P2", "No IGDB Rating",          "auto",    "Puan gösterimi çalışmıyor"),
    "never_synced":         ("P2", "Never IGDB Synced",       "auto",    "Hiç enrich edilmemiş"),
    "base64_cover":         ("P2", "Base64 Cover Image",      "manual",  "~23KB platform başı depolama yükü"),
    "dup_title_suspect":    ("P2", "Duplicate Title Suspect", "manual",  "Aynı title+year başka kayıtta da var"),
    # P3 Info
    "no_primary_cover":     ("P3", "No Primary Cover",        "auto",    "Kart placeholder gösterir"),
    "no_storyline":         ("P3", "No Storyline",            "auto",    "İkincil metadata eksik"),
    "year_mismatch":        ("P3", "Year Mismatch",           "manual",  "Canonical yıl ile IGDB yılı >1 fark"),
    "preferred_not_primary":("P3", "Preferred≠Primary",       "manual",  "is_preferred=true ama primary_variant değil"),
    "redundant_version_title":("P3","Redundant Version Title","auto",    "version_title == title (gereksiz)"),
    "platform_no_emulator": ("P3", "Platform No Emulator",   "manual",  "Emulator atanmamış"),
    "platform_no_performance":("P3","Platform No Performance","manual",  "Performans değerlendirmesi yok"),
    "platform_missing_cover":("P3","Platform Missing Cover",  "auto",    "Platform için kapak görseli yok"),
}

AUTO_FIXABLE = {k for k, v in ISSUE_CATALOG.items() if v[2] == "auto"}


def req(endpoint, params=None):
    url = f"{SB}/rest/v1/{endpoint}"
    if params:
        url += "?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    r = urllib.request.Request(url, headers={**HEADERS, "Accept": "application/json"})
    with urllib.request.urlopen(r, timeout=30) as resp:
        return json.loads(resp.read())


def fetch_audit(title=None, max_score=None, issue=None):
    params = {"order": "audit_score.asc,title.asc", "limit": "1000"}
    if title:
        params["title"] = f"eq.{title}"
    if max_score is not None:
        params["audit_score"] = f"lte.{max_score}"
    if issue:
        col = f"p1_{issue}" if issue in _p1_cols() else \
              f"p2_{issue}" if issue in _p2_cols() else \
              f"p3_{issue}"
        params[col] = "eq.true"
    return req("v_games_audit", params)


def _p1_cols():
    return {"no_external_id", "no_primary_variant", "multiple_primaries"}

def _p2_cols():
    return {"no_release_year", "no_publisher", "no_description",
            "no_igdb_rating", "never_synced", "base64_cover", "dup_title_suspect"}


def fetch_platform_audit():
    return req("v_game_platform_audit", {"limit": "2000"})


def compute_summary(games):
    total = len(games)
    if total == 0:
        return {}

    issue_counts = {k: 0 for k in ISSUE_CATALOG}
    scores = []
    p1_games = p2_games = p3_games = 0

    for g in games:
        scores.append(g.get("audit_score", 100))
        if g.get("critical_issues", 0) > 0:
            p1_games += 1
        if g.get("important_issues", 0) > 0:
            p2_games += 1
        if g.get("info_issues", 0) > 0:
            p3_games += 1
        for issue in (g.get("issue_types") or []):
            if issue in issue_counts:
                issue_counts[issue] += 1

    avg_score = sum(scores) / total
    sev_order = {"P1": 0, "P2": 1, "P3": 2}
    top_issues = sorted(
        [(k, v) for k, v in issue_counts.items() if v > 0],
        key=lambda x: (sev_order.get(ISSUE_CATALOG[x[0]][0], 9), -x[1])
    )

    return {
        "total": total,
        "p1_games": p1_games,
        "p2_games": p2_games,
        "p3_games": p3_games,
        "avg_score": round(avg_score, 1),
        "min_score": min(scores),
        "max_score": max(scores),
        "issue_counts": issue_counts,
        "top_issues": top_issues,
    }


def print_text_report(games, summary):
    W = 72
    print("=" * W)
    print("  RETROID DB AUDIT REPORT")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * W)
    print()
    print(f"  Toplam oyun  : {summary['total']}")
    print(f"  Ort. skor    : {summary['avg_score']} / 100")
    print(f"  Min skor     : {summary['min_score']}  |  Max: {summary['max_score']}")
    print(f"  P1 olan oyun : {summary['p1_games']}")
    print(f"  P2 olan oyun : {summary['p2_games']}")
    print(f"  P3 olan oyun : {summary['p3_games']}")
    print()

    print("─" * W)
    print("  ISSUE TÜRÜ SAYIMLARI")
    print("─" * W)
    print(f"  {'Kod':<30} {'SEV':>4}  {'Oyun':>5}  {'Düzeltme':>10}  Açıklama")
    print(f"  {'-'*28} {'---':>4}  {'----':>5}  {'-'*10}  {'-'*20}")
    for code, cnt in summary["top_issues"]:
        sev, label, fix_type, desc = ISSUE_CATALOG[code]
        fix_tag = "AUTO" if fix_type == "auto" else "MANUEL"
        print(f"  {code:<30} {sev:>4}  {cnt:>5}  {fix_tag:>10}  {desc}")
    print()

    if summary["p1_games"] > 0:
        print("─" * W)
        print("  P1 KRİTİK — DETAY")
        print("─" * W)
        for g in games:
            if g.get("critical_issues", 0) > 0:
                issues = ", ".join(
                    i for i in (g.get("issue_types") or [])
                    if ISSUE_CATALOG.get(i, ("",))[0] == "P1"
                )
                print(f"  [{g['audit_score']:3}] {g['title']:<45} {issues}")
        print()

    print("─" * W)
    print(f"  OTO DÜZELTİLEBİLİR: {sum(v for k,v in summary['issue_counts'].items() if k in AUTO_FIXABLE)} issue türü auto-fixable")
    print(f"  MANUEL GEREKLİ    : {sum(v for k,v in summary['issue_counts'].items() if k not in AUTO_FIXABLE)} issue türü manuel review")
    print("=" * W)


def print_markdown_report(games, summary):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"# Retroid DB Audit Report — {now}\n")
    print(f"| Metrik | Değer |")
    print(f"|--------|-------|")
    print(f"| Toplam oyun | {summary['total']} |")
    print(f"| Ortalama skor | **{summary['avg_score']}** / 100 |")
    print(f"| P1 (kritik) olan oyun | {summary['p1_games']} |")
    print(f"| P2 (önemli) olan oyun | {summary['p2_games']} |")
    print(f"| P3 (bilgi) olan oyun | {summary['p3_games']} |")
    print()

    print("## Issue Türleri\n")
    print("| Kod | Sev | Oyun Sayısı | Düzeltme | Açıklama |")
    print("|-----|-----|-------------|----------|----------|")
    for code, cnt in summary["top_issues"]:
        sev, label, fix_type, desc = ISSUE_CATALOG[code]
        fix_tag = "✅ auto" if fix_type == "auto" else "👤 manuel"
        print(f"| `{code}` | {sev} | {cnt} | {fix_tag} | {desc} |")
    print()

    if summary["p1_games"] > 0:
        print("## P1 Kritik Oyunlar\n")
        print("| Oyun | Skor | Issues |")
        print("|------|------|--------|")
        for g in games:
            if g.get("critical_issues", 0) > 0:
                issues = ", ".join(
                    f"`{i}`" for i in (g.get("issue_types") or [])
                    if ISSUE_CATALOG.get(i, ("",))[0] == "P1"
                )
                print(f"| {g['title']} | {g['audit_score']} | {issues} |")
        print()

    auto_cnt = sum(v for k, v in summary["issue_counts"].items() if k in AUTO_FIXABLE)
    manual_cnt = sum(v for k, v in summary["issue_counts"].items() if k not in AUTO_FIXABLE)
    print(f"## Özet\n")
    print(f"- **Auto-fixable issues:** {auto_cnt} kayıt (igdb_repair_missing.py ile)")
    print(f"- **Manuel review:** {manual_cnt} kayıt")
    print(f"\n_Audit view: `v_games_audit` — Platform audit: `v_game_platform_audit`_")


def main():
    parser = argparse.ArgumentParser(description="Retroid DB Audit Report")
    parser.add_argument("--format", choices=["text", "markdown"], default="text")
    parser.add_argument("--title", help="Belirli bir oyunu filtrele")
    parser.add_argument("--max-score", type=int, help="Sadece bu skora eşit veya düşük oyunları göster")
    parser.add_argument("--issue", help="Belirli bir issue türüne sahip oyunları filtrele (ör: no_igdb_rating)")
    args = parser.parse_args()

    try:
        games = fetch_audit(
            title=args.title,
            max_score=args.max_score,
            issue=args.issue,
        )
    except Exception as e:
        print(f"HATA: {e}", file=sys.stderr)
        sys.exit(1)

    if not games:
        print("Kritere uyan oyun bulunamadı.")
        return

    summary = compute_summary(games)

    if args.format == "markdown":
        print_markdown_report(games, summary)
    else:
        print_text_report(games, summary)


if __name__ == "__main__":
    main()
