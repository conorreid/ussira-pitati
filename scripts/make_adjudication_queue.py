"""Generate registry/adjudication_queue.csv: every parser-vs-catalogue
disagreement, one row per question, for hand-adjudication against the print
editions. Fill in `verdict` (parser | catalogue | both-wrong | unresolvable)
and `moran_says` / `notes`, then set adjudicated=yes. Rerunning preserves
adjudicated rows.
"""

import csv

from oracc_lib import DERIVED, ROOT

OUT = ROOT / "registry" / "adjudication_queue.csv"


def main():
    existing = {}
    if OUT.exists():
        with OUT.open() as fh:
            for r in csv.DictReader(fh):
                if r.get("adjudicated") == "yes":
                    existing[(r["designation"], r["role"])] = r

    rows = []
    with (DERIVED / "headers.csv").open() as fh:
        for r in csv.DictReader(fh):
            for role, cat_key in (("sender", "cat_sender"),
                                  ("addressee", "cat_recipient")):
                if r[f"{role}_agree"] == "False":
                    key = (r["designation"], role)
                    rows.append(existing.get(key, {
                        "designation": r["designation"], "id_text": r["id_text"],
                        "role": role,
                        "parsed": r[f"parsed_{role}"],
                        "catalogue": r[cat_key],
                        "moran_says": "", "verdict": "", "notes": "",
                        "adjudicated": "no",
                    }))

    with OUT.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} questions -> {OUT} "
          f"({sum(1 for r in rows if r['adjudicated'] == 'yes')} already adjudicated)")


if __name__ == "__main__":
    main()
