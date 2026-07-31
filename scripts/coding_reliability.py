"""Cross-edition coding reliability for the conflict network.

Compares the Moran-based pass (registry/conflict_edges.csv) with the
Rainey-based pass (registry/conflict_edges_rainey.csv). Same annotator,
independent source editions - this measures edition-robustness of the
coding, NOT coder-independence (which still requires a second human).

Units for kappa: for every letter coded in either pass, the candidate
directed dyads = {letter sender} x {persons appearing in that letter}
(from letter_persons.csv) plus any dyad actually coded by either pass.
Each unit is labeled edge/no-edge by each pass; Cohen's kappa over units.

EA 104 is excluded: the Rainey text extraction for that letter is
incomplete (no candidate passage recoverable), so absence there would be
an artifact. Writes coding_reliability.md.
"""

import csv

from oracc_lib import DERIVED, ROOT

EXCLUDE = {"EA 104"}


def load_edges(path):
    out = set()
    with path.open() as fh:
        for r in csv.DictReader(fh):
            if r["ea"] in EXCLUDE:
                continue
            out.add((r["ea"], r["src"], r["dst"], r["sign"]))
    return out


def main():
    moran = load_edges(ROOT / "registry" / "conflict_edges.csv")
    rainey = load_edges(ROOT / "registry" / "conflict_edges_rainey.csv")

    letters = {e[0] for e in moran | rainey}
    persons = {}
    sender = {}
    with (DERIVED / "letter_persons.csv").open() as fh:
        for r in csv.DictReader(fh):
            persons[r["designation"]] = [p for p in r["persons"].split(";") if p]
            sender[r["designation"]] = r["sender"]

    units = set()
    for ea in letters:
        s = sender.get(ea, "")
        for p in persons.get(ea, []):
            if s and p != s:
                units.add((ea, s, p, "-"))
    for e in moran | rainey:
        units.add(e)

    n = len(units)
    both = sum(1 for u in units if u in moran and u in rainey)
    only_m = sum(1 for u in units if u in moran and u not in rainey)
    only_r = sum(1 for u in units if u in rainey and u not in moran)
    neither = n - both - only_m - only_r
    po = (both + neither) / n
    p_yes_m = (both + only_m) / n
    p_yes_r = (both + only_r) / n
    pe = p_yes_m * p_yes_r + (1 - p_yes_m) * (1 - p_yes_r)
    kappa = (po - pe) / (1 - pe) if pe < 1 else float("nan")
    jaccard = both / (both + only_m + only_r)

    L = []
    a = L.append
    a("# Conflict-Coding Reliability: Moran pass vs Rainey pass")
    a("")
    a("Same annotator, independent editions (edition-robustness, not")
    a("coder-independence). EA 104 excluded (incomplete Rainey extraction).")
    a("")
    a(f"- letters compared: {len(letters)}")
    a(f"- candidate units (letter-dyads): {n}")
    a(f"- edges in both passes: {both}; Moran-only: {only_m}; "
      f"Rainey-only: {only_r}; coded by neither: {neither}")
    a(f"- **raw agreement: {100*po:.1f}%; edge Jaccard: {jaccard:.2f}; "
      f"Cohen's kappa: {kappa:.2f}**")
    a("")
    a("## Divergent units")
    a("")
    a("| unit | Moran pass | Rainey pass |")
    a("|---|---|---|")
    for u in sorted(moran ^ rainey):
        a(f"| {u[0]} {u[1]} -> {u[2]} ({u[3]}) "
          f"| {'edge' if u in moran else '-'} | {'edge' if u in rainey else '-'} |")
    a("")
    a("Divergences are of three kinds: (a) genuine edition differences in")
    a("the underlying text (EA 75 Miya as perpetrator vs victim; EA 101")
    a("Ḫaya; EA 116/138/149/161 passages present in Rainey's collation but")
    a("not Moran's rendering); (b) passages not surfaced by the extraction")
    a("of one edition (Ḫaapi in EA 149, Tagi in EA 287); (c) none arise")
    a("from the coding rules themselves.")
    a("")
    (ROOT / "coding_reliability.md").write_text("\n".join(L))
    print(f"kappa={kappa:.3f} agreement={100*po:.1f}% jaccard={jaccard:.2f} "
          f"(both={both} onlyM={only_m} onlyR={only_r} units={n})")


if __name__ == "__main__":
    main()
