"""Join node polities to Pleiades coordinates (Weeks 5-7, RQ5 groundwork).

Reads the Pleiades bulk dumps (data/raw/, see README for fetch commands) and
writes registry/polity_coords.csv: one row per distinct polity in nodes.csv
with Pleiades id/title/lat/lon where matched, and needs_review=yes where not.

Match order: (1) folded exact match on any slash-component of a Pleiades
title; (2) folded exact match on transliterated alternate names from the
names dump; (3) the CLASSICAL hand-map below (Amarna name -> the classical
name Pleiades files it under), then (1)-(2) again on that name.

The output lives in registry/ (not data/derived/) because unmatched rows are
meant to be hand-completed from the World Historical Gazetteer; rerunning
this script preserves hand-filled rows unless --overwrite is passed.
"""

import csv
import sys

from oracc_lib import ROOT, fold

RAW = ROOT / "data" / "raw"
OUT = ROOT / "registry" / "polity_coords.csv"

# Amarna toponym -> name Pleiades actually files the place under.
# Curated; each is a well-known equivalence, but verify=review stays 'yes'
# for hand-confirmation of the matched coordinates.
CLASSICAL = {
    "Akka": "Ake",
    "Ashkelon": "Askalon",
    "Ashdod": "Azotus",
    "Beirut": "Berytus",
    "Gazru": "Gazara",
    "Gimtu": "Gath",
    "Jerusalem": "Hierosolyma",
    "Lakiša": "Lachish",
    "Pihilu": "Pella",
    "Qadesh": "Kadesh",
    "Qatna": "Qatna",
    "Tyre": "Tyrus",
    "Šakmu": "Shechem",
    "Irqata": "Arca",
    "Kumidu": "Kumidi",
    "Megiddo": "Tel Megiddo",
    "Qadesh": "Qadesh on the Orontes",
    "Egypt": "Akhetaten",
    "Hatti": "Hattusa",
    "Alašiya": "Cyprus",
    "Assyria": "Assyria",
}


def load_places():
    by_component = {}
    with (RAW / "pleiades-places-latest.csv").open() as fh:
        for r in csv.DictReader(fh):
            rec = dict(id=r["id"], title=r["title"],
                       lat=r.get("reprLat", ""), lon=r.get("reprLong", ""))
            for comp in r["title"].split("/"):
                by_component.setdefault(fold(comp), []).append(rec)
    return by_component


def load_names():
    by_name = {}
    with (RAW / "pleiades-names-latest.csv").open() as fh:
        for r in csv.DictReader(fh):
            rec = dict(id=r["pid"].strip("/").split("/")[-1], title=r["title"],
                       lat=r.get("reprLat", ""), lon=r.get("reprLong", ""))
            for form in (r.get("nameTransliterated", ""), r.get("nameAttested", "")):
                for alt in form.split(","):
                    if alt.strip():
                        by_name.setdefault(fold(alt), []).append(rec)
    return by_name


def match(polity, by_title, by_name):
    for query, method_prefix in ((polity, ""), (CLASSICAL.get(polity, ""), "classical:")):
        if not query:
            continue
        f = fold(query)
        for source, method in ((by_title, "title"), (by_name, "name")):
            recs = source.get(f, [])
            if recs:
                # Rank: exact single-component title first, then presence of
                # coordinates. Keeps Mesopotamian 'Babylon' ahead of
                # 'Babylon/al-Fustat/Old Cairo'.
                recs = sorted(recs, key=lambda r: (fold(r["title"]) != f,
                                                   not r["lat"]))
                rec = recs[0]
                ambiguous = len({r["id"] for r in recs}) > 1
                return rec, method_prefix + method, ambiguous
    return None, "none", False


def main():
    overwrite = "--overwrite" in sys.argv
    existing = {}
    if OUT.exists() and not overwrite:
        with OUT.open() as fh:
            for r in csv.DictReader(fh):
                # Keep hand-filled rows AND rows with coordinates already
                # resolved (e.g. live-fetched for places missing from the
                # bulk dump) - a plain rerun must not degrade the table.
                if r.get("hand_filled") == "yes" or r.get("lat"):
                    existing[r["polity"]] = r

    polities = sorted({r["polity"] for r in
                       csv.DictReader((ROOT / "data" / "derived" / "nodes.csv").open())
                       if r["polity"]})
    by_title = load_places()
    by_name = load_names()

    rows = []
    n_matched = 0
    for pol in polities:
        if pol in existing:
            rows.append(existing[pol])
            n_matched += 1
            continue
        rec, method, ambiguous = match(pol, by_title, by_name)
        if rec:
            n_matched += 1
            rows.append(dict(
                polity=pol, pleiades_id=rec["id"], pleiades_title=rec["title"],
                lat=rec["lat"], lon=rec["lon"], match_method=method,
                needs_review="yes" if (ambiguous or method.startswith("classical")) else "no",
                hand_filled="no"))
        else:
            rows.append(dict(polity=pol, pleiades_id="", pleiades_title="",
                             lat="", lon="", match_method="none",
                             needs_review="yes", hand_filled="no"))

    if "--fetch" in sys.argv:
        import requests
        for r in rows:
            if r["pleiades_id"] and not r["lat"]:
                url = f"https://pleiades.stoa.org/places/{r['pleiades_id']}/json"
                try:
                    j = requests.get(url, timeout=30).json()
                    pt = j.get("reprPoint")
                    if pt:
                        r["lon"], r["lat"] = str(pt[0]), str(pt[1])
                        r["match_method"] += "+live"
                        print(f"  fetched {r['polity']}: {pt[1]:.3f}, {pt[0]:.3f}")
                except Exception as e:
                    print(f"  fetch failed for {r['polity']}: {e}")

    with OUT.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    print(f"{n_matched}/{len(polities)} polities matched -> {OUT}")
    print("\nunmatched (hand-fill from WHG/Goren, set hand_filled=yes):")
    for r in rows:
        if r["match_method"] == "none":
            print(f"  {r['polity']}")
    print("\nmatched but flagged for review:")
    for r in rows:
        if r["match_method"] != "none" and r["needs_review"] == "yes":
            print(f"  {r['polity']:12s} -> {r['pleiades_title']} ({r['match_method']})")


if __name__ == "__main__":
    main()
