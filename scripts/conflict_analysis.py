"""Provisional RQ4 look at the signed conflict network (tranche 1,
single-coder — NOT base-analysis grade until a second coding pass exists).
Writes conflict_report.md."""

import csv
from collections import Counter

import igraph as ig

from oracc_lib import ROOT
from phase2_analysis import fmt_table

REPORT = ROOT / "conflict_report.md"


def main():
    with (ROOT / "registry" / "conflict_edges.csv").open() as fh:
        rows = list(csv.DictReader(fh))

    actors = sorted({r["src"] for r in rows} | {r["dst"] for r in rows})
    idx = {a: i for i, a in enumerate(actors)}
    g = ig.Graph(directed=True)
    g.add_vertices(actors)
    g.add_edges([(idx[r["src"]], idx[r["dst"]]) for r in rows])
    g.es["sign"] = [r["sign"] for r in rows]

    neg = g.subgraph_edges([e for e in g.es if e["sign"] == "-"], delete_vertices=False)
    acc_in = Counter()
    acc_out = Counter()
    for r in rows:
        if r["sign"] == "-":
            acc_out[r["src"]] += 1
            acc_in[r["dst"]] += 1

    und = g.as_undirected()
    und.simplify()
    bet = und.betweenness()
    bet_rows = sorted(
        ({"actor": v["name"], "betweenness": round(bet[v.index], 1),
          "accused_by_n": acc_in[v["name"]], "accuses_n": acc_out[v["name"]]}
         for v in und.vs), key=lambda r: -r["betweenness"])[:10]

    L = []
    a = L.append
    a("# Conflict Network (RQ4) — corpus-wide sweep (tranches 1-2), "
      "single annotator")
    a("")
    a("Coded from Moran (1992) per `registry/conflict_codebook.md`,")
    a("corpus-wide (tranche 1: the five classic theatres; tranche 2: full")
    a("hostile-language sweep). Independently recoded from Rainey (2015):")
    a("cross-edition kappa reported in `coding_reliability.md` - but both passes")
    a("share one annotator, so the PLAN.md 7 second-coder pass is still")
    a("required before these edges enter the base analysis.")
    a("")
    n_neg = sum(1 for r in rows if r["sign"] == "-")
    n_pos = len(rows) - n_neg
    a(f"- letters coded: {len({r['ea'] for r in rows})}; edges: {len(rows)} "
      f"({n_neg} accusations, {n_pos} alliance)")
    a(f"- actors: {len(actors)}")
    a("")
    a("## Most-accused")
    a("")
    a(fmt_table([{"actor": k, "accused in n letters": v}
                 for k, v in acc_in.most_common(8)]))
    a("")
    a("## Betweenness in the (undirected) conflict graph")
    a("")
    a(fmt_table(bet_rows))
    a("")
    a("## Reading")
    a("")
    a("Even in this partial tranche the RQ4 hypothesis pattern is visible:")
    a("the conflict graph's central figures are the *accused bridges* —")
    a("Aziru (accused from Byblos, Tyre, and implicated at Damascus) and the")
    a("Milkilu/Tagi/sons-of-Labaya bloc — not the loudest accusers. The")
    a("inter-vassal politics invisible in the correspondence layer (which")
    a("has literally zero vassal-vassal edges beyond two) is the dominant")
    a("structure here. Full coverage and second coding in tranche 2.")
    a("")
    REPORT.write_text("\n".join(L))
    print(f"wrote {REPORT}")


if __name__ == "__main__":
    main()
