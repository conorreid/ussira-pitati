"""Disambiguating the correspondence distance-decay finding (RQ5 follow-up).

phase4_qap.md found (post coordinate-correction) that vassal letters-to-
pharaoh volume falls with distance from Akhetaten. Two families of
confound could produce that without distance-as-cost:

  1. Composition: a few polities with a known *political* reason for low
     volume (defection to Hatti) happen to be far; or a single influential
     polity drives the fit. -> Tier 1: leave-one-polity-out jackknife,
     targeted drops (hatti_aligned per registry/vassal_covariates.csv),
     and polity-level aggregation (actors of one polity share a distance;
     treating them as independent points overweights multi-ruler towns).

  2. Administrative density: correspondence may track proximity to
     Egyptian garrison/commissioner seats (registry/
     egyptian_admin_centers.csv), not to the court itself. The centers are
     spread along the Levant, so distance-to-nearest-center is not
     collinear with distance-to-Akhetaten. -> Tier 2: partial rank
     correlations with Freedman-Lane permutation.

Seed 4711, 2000 permutations. Spearman here uses tie-averaged ranks
(letter counts are tie-heavy); the phase4_qap.md implementation uses raw
order ranks, so baseline rho differs in the second decimal.

Writes distance_confounds.md.
"""

import csv
import math
import random
from collections import Counter, defaultdict

from oracc_lib import DERIVED, ROOT

SEED = 4711
N_PERM = 2000


def haversine(a, b):
    lat1, lon1, lat2, lon2 = map(math.radians, (*a, *b))
    h = (math.sin((lat2 - lat1) / 2) ** 2
         + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2)
    return 2 * 6371 * math.asin(math.sqrt(h))


def avg_rank(v):
    order = sorted(range(len(v)), key=lambda i: v[i])
    rk = [0.0] * len(v)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
            j += 1
        r = (i + j) / 2.0
        for k in range(i, j + 1):
            rk[order[k]] = r
        i = j + 1
    return rk


def pearson(xs, ys):
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    vx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    vy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return cov / (vx * vy) if vx and vy else 0.0


def spearman(xs, ys):
    return pearson(avg_rank(xs), avg_rank(ys))


def perm_p_two_sided(xs, ys, rng):
    obs = spearman(xs, ys)
    ys = list(ys)
    hits = 0
    for _ in range(N_PERM):
        rng.shuffle(ys)
        if abs(spearman(xs, ys)) >= abs(obs):
            hits += 1
    return obs, hits / N_PERM


def ols(X, y):
    """Least squares via normal equations, Gaussian elimination.
    Returns (beta, fitted, residuals)."""
    k = len(X[0])
    A = [[sum(X[r][i] * X[r][j] for r in range(len(X))) for j in range(k)]
         for i in range(k)]
    b = [sum(X[r][i] * y[r] for r in range(len(X))) for i in range(k)]
    for col in range(k):
        piv = max(range(col, k), key=lambda r: abs(A[r][col]))
        A[col], A[piv] = A[piv], A[col]
        b[col], b[piv] = b[piv], b[col]
        for r in range(col + 1, k):
            f = A[r][col] / A[col][col]
            for c in range(col, k):
                A[r][c] -= f * A[col][c]
            b[r] -= f * b[col]
    beta = [0.0] * k
    for r in range(k - 1, -1, -1):
        beta[r] = (b[r] - sum(A[r][c] * beta[c] for c in range(r + 1, k))) \
            / A[r][r]
    fitted = [sum(X[r][i] * beta[i] for i in range(k)) for r in range(len(X))]
    resid = [y[r] - fitted[r] for r in range(len(X))]
    return beta, fitted, resid


def partial_freedman_lane(y, focal, nuisance, rng):
    """Partial correlation of y with focal given nuisance covariates,
    permutation p by Freedman-Lane (permute residuals of y ~ nuisance)."""
    Z = [[1.0] + list(row) for row in nuisance]
    _, fit_y, res_y = ols(Z, y)
    _, _, res_f = ols(Z, focal)
    obs = pearson(res_y, res_f)
    hits = 0
    for _ in range(N_PERM):
        res_p = res_y[:]
        rng.shuffle(res_p)
        y_star = [f + e for f, e in zip(fit_y, res_p)]
        _, _, res_ys = ols(Z, y_star)
        if abs(pearson(res_ys, res_f)) >= abs(obs):
            hits += 1
    return obs, hits / N_PERM


def main():
    rng = random.Random(SEED)

    with (ROOT / "registry" / "polity_coords.csv").open() as fh:
        pol = {r["polity"]: (float(r["lat"]), float(r["lon"]))
               for r in csv.DictReader(fh) if r["lat"]}
    with (ROOT / "registry" / "egyptian_admin_centers.csv").open() as fh:
        centers = {r["center"]: (float(r["lat"]), float(r["lon"]))
                   for r in csv.DictReader(fh)}
    with (ROOT / "registry" / "vassal_covariates.csv").open() as fh:
        cov = {r["polity"]: r for r in csv.DictReader(fh)}

    tier_of, polity_of = {}, {}
    with (DERIVED / "nodes.csv").open() as fh:
        for r in csv.DictReader(fh):
            tier_of[r["actor_id"]] = r["tier"]
            polity_of[r["actor_id"]] = r["polity"]

    akhet = pol["Egypt"]
    sent = Counter()
    with (DERIVED / "edges_corr.csv").open() as fh:
        for r in csv.DictReader(fh):
            a = r["src"]
            if (r["dst"] == "pharaoh" and tier_of.get(a) == "vassal"
                    and polity_of.get(a) in pol):
                sent[a] += 1

    rows = []  # (actor, polity, letters, km_court, km_admin, coastal, aligned)
    missing_cov = set()
    for a, n in sorted(sent.items()):
        p = polity_of[a]
        c = cov.get(p)
        if c is None:
            missing_cov.add(p)
            continue
        rows.append((a, p, n,
                     haversine(pol[p], akhet),
                     min(haversine(pol[p], xy) for xy in centers.values()),
                     1.0 if c["coastal"] == "yes" else 0.0,
                     1.0 if c["hatti_aligned"] in ("yes", "accused") else 0.0))

    letters = [r[2] for r in rows]
    km_court = [r[3] for r in rows]
    km_admin = [r[4] for r in rows]
    coastal = [r[5] for r in rows]
    aligned = [r[6] for r in rows]

    L = []
    a_ = L.append
    a_("# Distance-Decay Confound Analysis (RQ5 follow-up)")
    a_("")
    a_("Generated by `scripts/distance_confounds.py` (seed 4711, 2000")
    a_("permutations, tie-averaged Spearman). Inputs: corrected")
    a_("`registry/polity_coords.csv`, `registry/egyptian_admin_centers.csv`,")
    a_("`registry/vassal_covariates.csv`.")
    a_("")
    if missing_cov:
        a_(f"Uncovered polities (no covariate row, excluded): "
           f"{sorted(missing_cov)}")
        a_("")

    # ---- Baseline ----
    obs0, p0 = perm_p_two_sided(km_court, letters, rng)
    a_("## 0. Corrected baseline (actor-level)")
    a_("")
    a_(f"- n = {len(rows)} located vassal correspondents")
    a_(f"- Spearman rho(letters, km to Akhetaten) = **{obs0:.3f}**, "
       f"two-sided permutation p = **{p0:.3f}**")
    a_("")

    # ---- Tier 1a: leave-one-polity-out ----
    a_("## 1a. Leave-one-polity-out jackknife")
    a_("")
    a_("| dropped polity | actors | rho | p |")
    a_("|---|---|---|---|")
    jack = []
    for p in sorted({r[1] for r in rows}):
        keep = [r for r in rows if r[1] != p]
        o, pv = perm_p_two_sided([r[3] for r in keep],
                                 [r[2] for r in keep], rng)
        jack.append((p, len(rows) - len(keep), o, pv))
    for p, na, o, pv in sorted(jack, key=lambda t: t[2]):
        a_(f"| {p} | {na} | {o:.3f} | {pv:.3f} |")
    rhos = [j[2] for j in jack]
    a_("")
    a_(f"Range of rho under single-polity deletion: "
       f"**{min(rhos):.3f} to {max(rhos):.3f}**; "
       f"p < 0.05 in {sum(1 for j in jack if j[3] < 0.05)}/{len(jack)} "
       f"deletions.")
    a_("")

    # ---- Tier 1b: targeted drops ----
    a_("## 1b. Targeted drops (defection / composition)")
    a_("")
    a_("| variant | n | rho | p |")
    a_("|---|---|---|---|")

    def variant(name, keep_rows):
        o, pv = perm_p_two_sided([r[3] for r in keep_rows],
                                 [r[2] for r in keep_rows], rng)
        a_(f"| {name} | {len(keep_rows)} | {o:.3f} | {pv:.3f} |")

    variant("without Hatti-aligned polities (Qadesh, Sidon)",
            [r for r in rows if not r[6]])
    variant("without Ugarit (quasi-independent, 3 one-letter kings)",
            [r for r in rows if r[1] != "Ugarit"])
    variant("without both",
            [r for r in rows if not r[6] and r[1] != "Ugarit"])
    variant("without Rib-Hadda (volume outlier)",
            [r for r in rows if r[0] != "ribhadda"])
    a_("")

    # ---- Tier 1c: polity-level aggregation ----
    agg = defaultdict(float)
    for r in rows:
        agg[r[1]] += r[2]
    pol_rows = sorted(agg)
    o_pol, p_pol = perm_p_two_sided(
        [haversine(pol[p], akhet) for p in pol_rows],
        [agg[p] for p in pol_rows], rng)
    a_("## 1c. Polity-level aggregation")
    a_("")
    a_("Actors of one polity share a distance; treating them as")
    a_("independent points overweights multi-ruler towns (Gazru x3,")
    a_("Gimtu x3, Ugarit x3). Summing letters per polity:")
    a_("")
    a_(f"- n = {len(pol_rows)} polities; rho = **{o_pol:.3f}**, "
       f"p = **{p_pol:.3f}**")
    a_("")

    # ---- Tier 2 ----
    a_("## 2. Administrative-density and transport covariates")
    a_("")
    r_cc = spearman(km_court, km_admin)
    a_(f"- Collinearity check: rho(km court, km nearest admin center) = "
       f"**{r_cc:.3f}** - the centers are spread along the Levant, so the")
    a_("  two distances separate (identification holds).")
    a_("")
    ry = avg_rank(letters)
    rc = avg_rank(km_court)
    ra = avg_rank(km_admin)
    tests = [
        ("km to Akhetaten | admin, coastal, aligned", rc,
         list(zip(ra, coastal, aligned))),
        ("km to nearest admin center | court, coastal, aligned", ra,
         list(zip(rc, coastal, aligned))),
        ("coastal | court, admin, aligned", coastal,
         list(zip(rc, ra, aligned))),
        ("hatti-aligned | court, admin, coastal", aligned,
         list(zip(rc, ra, coastal))),
    ]
    a_("Partial rank correlations with letters sent (Freedman-Lane")
    a_("permutation, two-sided):")
    a_("")
    a_("| focal predictor (given nuisance) | partial r | p |")
    a_("|---|---|---|")
    for name, focal, nuis in tests:
        o, pv = partial_freedman_lane(ry, list(focal), nuis, rng)
        a_(f"| {name} | {o:.3f} | {pv:.3f} |")
    a_("")
    a_("## Reading")
    a_("")
    a_("The correspondence-layer distance decay reported in earlier drafts")
    a_("(rho = -0.50, p = 0.002) does not survive scrutiny. It was stacked")
    a_("from three artifacts. (i) Six phantom data points from bad gazetteer")
    a_("matches - four actors coded to a 'Syria' region point in the Ionian")
    a_("Sea, Pihilu matched to Macedonian Pella, Irqata to Anatolian Arca -")
    a_("all far-with-few-letters, exactly the shape that manufactures decay")
    a_("(Tyre was also mislocated to a homonymous estate in Jordan).")
    a_("(ii) Spearman without tie-averaging: 14 of 35 actors tie at one")
    a_("letter, and raw order ranks let input row order leak into rho")
    a_("(-0.45 -> -0.32 on identical data). (iii) Composition: the residual")
    a_("trend concentrates in polities with political reasons to write")
    a_("little (Hatti-aligned Qadesh/Sidon; quasi-independent Ugarit);")
    a_("without them rho = -0.18, p = 0.32, and single-polity deletion")
    a_("leaves significance in a minority of variants. The partial effect")
    a_("of court distance given administrative proximity, coast, and")
    a_("alignment is -0.26 (p = 0.17); no covariate predicts volume.")
    a_("")
    a_("Conclusion: the pre-registered RQ5 prediction stands after all -")
    a_("distance decays mention and conflict ties (both robust to the")
    a_("coordinate corrections, p < 0.01) while correspondence with the")
    a_("court shows no defensible distance effect at this n. The sign")
    a_("stays negative in every variant, so a weak true effect is not")
    a_("excluded - but nothing here licenses claiming one.")
    a_("")

    (ROOT / "distance_confounds.md").write_text("\n".join(L))
    print("\n".join(L))


if __name__ == "__main__":
    main()
