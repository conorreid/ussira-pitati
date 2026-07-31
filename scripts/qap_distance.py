"""RQ5 — the geography contrast, with QAP permutation inference.

Prediction (PLAN.md §1.2): distance decays ties in the conflict/mention
layer (neighbors accuse neighbors) but NOT in the correspondence layer
(every vassal writes to distant Egypt regardless).

Tests:
1. Mention layer: point-biserial correlation between dyadic distance and
   tie presence among located actors, QAP node-permutation null (2000
   perms).
2. Conflict layer: same, on the signed conflict edges (tranches 1-2 -
   single-coder, provisional).
3. Correspondence layer: Spearman correlation between a vassal's distance
   to Akhetaten and letters sent (prediction: ~0), permutation null.

Writes phase4_qap.md and, if phase4_ergm.md exists (from
phase4_models.R), assembles both into phase4_report.md.
"""

import csv
import math
import random
from collections import Counter

from oracc_lib import DERIVED, ROOT

SEED = 4711
N_PERM = 2000


def haversine(a, b):
    lat1, lon1, lat2, lon2 = map(math.radians, (*a, *b))
    h = (math.sin((lat2 - lat1) / 2) ** 2
         + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2)
    return 2 * 6371 * math.asin(math.sqrt(h))


def load_actor_coords():
    coords = {}
    with (ROOT / "registry" / "polity_coords.csv").open() as fh:
        pol = {r["polity"]: (float(r["lat"]), float(r["lon"]))
               for r in csv.DictReader(fh) if r["lat"]}
    with (DERIVED / "nodes.csv").open() as fh:
        for r in csv.DictReader(fh):
            if r["polity"] in pol and r["actor_id"] != "pharaoh":
                coords[r["actor_id"]] = pol[r["polity"]]
    return coords, pol


def qap_pointbiserial(actors, ties, dist, rng):
    """Correlation between tie indicator and distance over dyads, with
    QAP (joint row/col relabeling of the distance matrix) null."""
    def corr(perm):
        xs, ys = [], []
        for i, a in enumerate(actors):
            for j in range(i + 1, len(actors)):
                b = actors[j]
                xs.append(dist[(actors[perm[i]], actors[perm[j]])])
                ys.append(1.0 if (a, b) in ties or (b, a) in ties else 0.0)
        mx = sum(xs) / len(xs)
        my = sum(ys) / len(ys)
        cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        vx = math.sqrt(sum((x - mx) ** 2 for x in xs))
        vy = math.sqrt(sum((y - my) ** 2 for y in ys))
        return cov / (vx * vy) if vx and vy else 0.0

    ident = list(range(len(actors)))
    obs = corr(ident)
    null = []
    for _ in range(N_PERM):
        p = ident[:]
        rng.shuffle(p)
        null.append(corr(p))
    p_le = sum(1 for x in null if x <= obs) / N_PERM  # decay = negative corr
    return obs, p_le


def main():
    rng = random.Random(SEED)
    coords, pol_coords = load_actor_coords()

    # Distances between all located actors
    def distmat(actors):
        return {(a, b): haversine(coords[a], coords[b])
                for a in actors for b in actors if a != b}

    # Mention ties
    mention = set()
    with (DERIVED / "edges_mention.csv").open() as fh:
        for r in csv.DictReader(fh):
            mention.add((r["actor_i"], r["actor_j"]))
    m_actors = sorted({a for e in mention for a in e if a in coords})
    obs_m, p_m = qap_pointbiserial(m_actors, mention, distmat(m_actors), rng)

    # Conflict ties (tranche 1)
    conflict = set()
    with (ROOT / "registry" / "conflict_edges.csv").open() as fh:
        for r in csv.DictReader(fh):
            conflict.add((r["src"], r["dst"]))
    c_actors = sorted({a for e in conflict for a in e if a in coords})
    obs_c, p_c = qap_pointbiserial(c_actors, conflict, distmat(c_actors), rng)

    # Correspondence: letters sent vs distance to Akhetaten.
    # VASSALS ONLY - mixing in Great Powers (far away, few letters each)
    # would manufacture spurious distance decay across tiers.
    tier_of = {}
    with (DERIVED / "nodes.csv").open() as fh:
        for r in csv.DictReader(fh):
            tier_of[r["actor_id"]] = r["tier"]
    akhet = pol_coords.get("Egypt")
    sent = Counter()
    with (DERIVED / "edges_corr.csv").open() as fh:
        for r in csv.DictReader(fh):
            if (r["dst"] == "pharaoh" and r["src"] in coords
                    and tier_of.get(r["src"]) == "vassal"):
                sent[r["src"]] += 1
    pairs = [(haversine(coords[a], akhet), n) for a, n in sent.items()]

    def spearman(ps):
        def rank(v):
            # Tie-averaged ranks: letter counts are tie-heavy (many
            # one-letter senders), and raw order ranks would make rho
            # depend on input row order.
            order = sorted(range(len(v)), key=lambda i: v[i])
            rk = [0.0] * len(v)
            i = 0
            while i < len(order):
                j = i
                while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                    j += 1
                for k in range(i, j + 1):
                    rk[order[k]] = (i + j) / 2.0
                i = j + 1
            return rk
        xs = rank([p[0] for p in ps])
        ys = rank([p[1] for p in ps])
        mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
        cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        vx = math.sqrt(sum((x - mx) ** 2 for x in xs))
        vy = math.sqrt(sum((y - my) ** 2 for y in ys))
        return cov / (vx * vy) if vx and vy else 0.0

    def perm_p(ps):
        obs = spearman(ps)
        ys_orig = [p[1] for p in ps]
        null = []
        for _ in range(N_PERM):
            ys = ys_orig[:]
            rng.shuffle(ys)
            null.append(spearman([(p[0], y) for p, y in zip(ps, ys)]))
        return obs, sum(1 for x in null if abs(x) >= abs(obs)) / N_PERM

    obs_s, p_s = perm_p(pairs)
    pairs_norib = [(haversine(coords[a], akhet), n) for a, n in sent.items()
                   if a != "ribhadda"]
    obs_nr, p_nr = perm_p(pairs_norib)

    L = []
    a = L.append
    a("## QAP / permutation tests — the RQ5 geography contrast")
    a("")
    a(f"Located actors: {len(coords)} (via registry/polity_coords.csv). "
      "Seed 4711, 2000 permutations.")
    a("")
    a("| layer | n actors | statistic | observed | p |")
    a("|---|---|---|---|---|")
    a(f"| mention co-occurrence | {len(m_actors)} | point-biserial r(tie, km) "
      f"| {obs_m:.3f} | {p_m:.3f} (P(r_null <= obs)) |")
    a(f"| conflict (tranches 1-2, provisional) | {len(c_actors)} | point-biserial "
      f"r(tie, km) | {obs_c:.3f} | {p_c:.3f} (P(r_null <= obs)) |")
    a(f"| correspondence: letters to pharaoh vs km to Akhetaten (vassals) | {len(pairs)} "
      f"| Spearman rho | {obs_s:.3f} | {p_s:.3f} (two-sided) |")
    a(f"| ... same, without Rib-Hadda | {len(pairs_norib)} "
      f"| Spearman rho | {obs_nr:.3f} | {p_nr:.3f} (two-sided) |")
    a("")
    a("Prediction: negative and significant in mention/conflict; null in")
    a("correspondence. A negative r with small P(r_null <= obs) supports")
    a("distance decay.")
    a("")
    (ROOT / "phase4_qap.md").write_text("\n".join(L))
    print("\n".join(L[4:10]))

    ergm_frag = ROOT / "phase4_ergm.md"
    if ergm_frag.exists():
        report = ["# Phase 4 Report — Inferential Models", "",
                  "Generated by `scripts/phase4_models.R`, `phase4_gof.R`, "
                  "`phase4_bergm.R`, and `qap_distance.py`.",
                  "", ergm_frag.read_text()]
        bergm_frag = ROOT / "phase4_bergm.md"
        if bergm_frag.exists():
            report += ["", bergm_frag.read_text()]
        report += ["", (ROOT / "phase4_qap.md").read_text()]
        (ROOT / "phase4_report.md").write_text("\n".join(report))
        print("assembled phase4_report.md")


if __name__ == "__main__":
    main()
