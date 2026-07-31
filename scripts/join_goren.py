"""Join Goren et al. 2004 petrographic provenance to the letter table.

- Maps each tablet's book section (the petrographic provenance
  determination) to a site name and, where possible, coordinates from
  registry/polity_coords.csv.
- Cross-validates against the Oracc catalogue's provenience field.
- Writes data/derived/letter_provenance.csv.

Sections in Ch.15 ('Unidentified Cities in Canaan') and fragment bins stay
unlocated - that is Goren's own verdict, not a gap in the join.
"""

import csv
import re

from oracc_lib import DERIVED, ROOT, fold

# Book section -> canonical site label (as used in polity_coords where
# possible). Only sections that assert a writing location are mapped.
SECTION_SITE = {
    "BYBLOS": "Byblos", "GEZER": "Gazru", "AMURRU": "Amurru",
    "SHECHEM": "Šakmu", "ASHKELON": "Ashkelon", "TYRE": "Tyre",
    "BEIRUT": "Beirut", "SIDON": "Sidon", "QATNA": "Qatna",
    "MEGIDDO": "Megiddo", "REHOB": "Rehob", "JERUSALEM": "Jerusalem",
    "MITANNI": "Mittani", "HATTI": "Hatti", "EGYPT": "Egypt",
    "ALASHIYA": "Alašiya", "BABYLONIA": "Babylon", "ASSYRIA": "Assyria",
    "ARZAWA": "Arzawa", "AKKO": "Akka", "ACHSHAPH": "Akšapa",
    "HAZOR": "Hazor", "LACHISH": "Lakiša", "GATH": "Gimtu",
    "GAZA": "Gaza", "ASHDOD": "Ashdod", "QADESH": "Qadesh",
    "KUMIDI": "Kumidu", "DAMASCUS": "Damascus", "PELLA": "Pihilu",
    "SHIMON": "Šamhuna", "ANAHARATH": "Anaharath",
}


def site_for(section):
    up = section.upper()
    for key, site in SECTION_SITE.items():
        if key in up:
            return site
    return ""


def main():
    coords = {}
    with (ROOT / "registry" / "polity_coords.csv").open() as fh:
        for r in csv.DictReader(fh):
            if r["lat"]:
                coords[r["polity"]] = (r["lat"], r["lon"])

    prov_by_letter = {}
    with (ROOT / "data" / "derived" / "edges_corr.csv").open() as fh:
        for r in csv.DictReader(fh):
            prov_by_letter[r["ea"]] = r["provenience"]

    rows = []
    n_agree = n_cmp = n_new = 0
    with (ROOT / "registry" / "goren2004_provenance.csv").open() as fh:
        for g in csv.DictReader(fh):
            ea = re.sub(r"^EA 0*", "EA ", g["ea"])
            ea_padded = g["ea"]
            site = site_for(g["section"])
            cat_prov = prov_by_letter.get(ea_padded, "")
            cat_site = site_for(cat_prov) or cat_prov  # normalize name variants
            agree = None
            if site and cat_prov and cat_prov != "Unknown location":
                agree = fold(site) == fold(cat_site) or fold(cat_site) in fold(site) \
                    or fold(site) in fold(cat_site)
                n_cmp += 1
                n_agree += agree
            if site and cat_prov == "Unknown location":
                n_new += 1
            lat, lon = coords.get(site, ("", ""))
            rows.append({
                "ea": ea_padded, "goren_section": g["section"],
                "goren_site": site, "catalogue_provenience": cat_prov,
                "agree": agree, "lat": lat, "lon": lon,
            })

    out = DERIVED / "letter_provenance.csv"
    with out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    located = sum(1 for r in rows if r["lat"])
    print(f"{len(rows)} tablets -> {out}")
    print(f"catalogue-comparable: {n_cmp}, agree: {n_agree} "
          f"({100*n_agree/n_cmp:.0f}%)")
    print(f"newly located (catalogue 'Unknown location'): {n_new}")
    print(f"with coordinates: {located}")
    print("\ndisagreements:")
    for r in rows:
        if r["agree"] is False:
            print(f"  {r['ea']}: Goren={r['goren_site']} vs catalogue={r['catalogue_provenience']}")


if __name__ == "__main__":
    main()
