"""Phase 3: the mention/co-occurrence network - where Cline & Cline's
'small world' must live if it lives anywhere. Writes phase3_report.md.

Analyses:
- Global descriptives and clustering-vs-nulls for the mention graph
  (all letters / without the Byblos dossier).
- The replication targets: CC = 0.391 and '48.75x random' (ER-style ratio),
  now against the fair configuration-model null as well.
- RQ1: betweenness with bootstrap rank intervals, plus a dossier-equalized
  variant (every sender capped at the median dossier size) to test whether
  Rib-Hadda's brokerage survives volume correction.
- Communities (Louvain/Leiden) and pharaoh-domination check.

Caveat carried in the report: EA 1-44 (Great Powers) have no lemmatized text
yet, so this mention layer covers the vassal correspondence; Cline & Cline's
graph included the royal letters.
"""

import csv
import random
from collections import Counter, defaultdict

import igraph as ig

from oracc_lib import DERIVED, ROOT
from phase2_analysis import (N_BOOT, SEED, fmt_dict, fmt_table, global_stats,
                             null_clustering, undirected)

REPORT = ROOT / "phase3_report.md"


def load_letter_persons():
    with (DERIVED / "letter_persons.csv").open() as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        r["group"] = [p for p in r["persons"].split(";") if p]
    return rows


def build_mention(rows):
    """Undirected weighted co-occurrence graph from letter person-groups."""
    import itertools
    w = Counter()
    actors = set()
    for r in rows:
        actors.update(r["group"])
        for a, b in itertools.combinations(sorted(r["group"]), 2):
            w[(a, b)] += 1
    actors = sorted(actors)
    idx = {a: i for i, a in enumerate(actors)}
    g = ig.Graph(directed=False)
    g.add_vertices(actors)
    g.add_edges([(idx[a], idx[b]) for a, b in w])
    g.es["weight"] = list(w.values())
    return g


def build_star(rows, include_corr=True):
    """Cline-style construction: per letter, edges sender<->each mentioned
    person (who-mentions-whom), optionally plus the correspondence edges.
    Undirected, weight = letter count."""
    w = Counter()
    actors = set()
    for r in rows:
        s = r["sender"]
        if not s:
            continue
        actors.add(s)
        for p in r["group"]:
            if p != s:
                actors.add(p)
                w[tuple(sorted((s, p)))] += 1
    if include_corr:
        with (DERIVED / "edges_corr.csv").open() as fh:
            for e in csv.DictReader(fh):
                if e["src"] != e["dst"]:
                    actors.update((e["src"], e["dst"]))
                    w[tuple(sorted((e["src"], e["dst"])))] += 1
    actors = sorted(actors)
    idx = {a: i for i, a in enumerate(actors)}
    g = ig.Graph(directed=False)
    g.add_vertices(actors)
    g.add_edges([(idx[a], idx[b]) for a, b in w])
    g.es["weight"] = list(w.values())
    return g


def build_star_from(rows, named_ph):
    """build_star over pre-transformed rows (e.g. pharaoh split), applying
    the same per-letter pharaoh tag to the correspondence edges."""
    def tag_for(pid):
        np_ = named_ph.get(pid, "")
        return ("pharaoh-" + np_.split(" of ")[0].replace(" ", "-").lower()
                if np_ else "pharaoh-unidentified")
    w = Counter()
    actors = set()
    for r in rows:
        s = r["sender"]
        if not s:
            continue
        actors.add(s)
        for p in r["group"]:
            if p != s:
                actors.add(p)
                w[tuple(sorted((s, p)))] += 1
    with (DERIVED / "edges_corr.csv").open() as fh:
        for e in csv.DictReader(fh):
            src, dst = e["src"], e["dst"]
            if src == "pharaoh":
                src = tag_for(e["id_text"])
            if dst == "pharaoh":
                dst = tag_for(e["id_text"])
            if src != dst:
                actors.update((src, dst))
                w[tuple(sorted((src, dst)))] += 1
    actors = sorted(actors)
    idx = {a: i for i, a in enumerate(actors)}
    g = ig.Graph(directed=False)
    g.add_vertices(actors)
    g.add_edges([(idx[a], idx[b]) for a, b in w])
    g.es["weight"] = list(w.values())
    return g


def bipartite_null_clustering(rows, rng, n_samples=200):
    """The fair null for a clique-projected graph: shuffle which persons
    appear in which letters, preserving each letter's group size and each
    person's total appearances (bipartite configuration via stub shuffle),
    then project and measure CC. Plain edge-rewiring overstates
    significance because cliques manufacture triangles mechanically."""
    stubs = [p for r in rows for p in r["group"]]
    sizes = [len(r["group"]) for r in rows]
    ccs = []
    for _ in range(n_samples):
        rng.shuffle(stubs)
        it = iter(stubs)
        fake = []
        for k in sizes:
            group = {next(it) for _ in range(k)}  # dedupe within letter
            fake.append({"group": sorted(group)})
        ccs.append(build_mention(fake).transitivity_undirected(mode="zero"))
    ccs.sort()
    return {
        "bipartite-null CC (median)": round(ccs[len(ccs) // 2], 4),
        "bipartite-null CC (2.5%-97.5%)":
            f"{ccs[int(0.025*len(ccs))]:.4f}-{ccs[int(0.975*len(ccs))]:.4f}",
    }


def betweenness_rows(g, top=12):
    bet = g.betweenness(directed=False)
    deg = g.degree()
    rows = []
    for v in g.vs:
        rows.append({"actor": v["name"], "degree": deg[v.index],
                     "betweenness": round(bet[v.index], 1)})
    rows.sort(key=lambda r: -r["betweenness"])
    return rows[:top]


def bootstrap_ranks(rows, focus, rng, dossier_cap=None, n_boot=N_BOOT):
    """Bootstrap betweenness ranks over letters. With dossier_cap, each
    sender contributes at most that many letters per replicate (sampled
    without replacement) - the RQ1 volume correction."""
    by_sender = defaultdict(list)
    for r in rows:
        by_sender[r["sender"] or f"_unk_{r['id_text']}"].append(r)
    ranks = defaultdict(list)
    for _ in range(n_boot):
        if dossier_cap is None:
            sample = rng.choices(rows, k=len(rows))
        else:
            sample = []
            for letters in by_sender.values():
                take = min(dossier_cap, len(letters))
                sample.extend(rng.sample(letters, take))
        g = build_mention(sample)
        bet = g.betweenness(directed=False)
        order = sorted(range(g.vcount()), key=lambda i: -bet[i])
        rank_of = {g.vs[i]["name"]: rk + 1 for rk, i in enumerate(order)}
        for a in focus:
            ranks[a].append(rank_of.get(a, g.vcount() + 1))
    out = []
    for a in focus:
        rs = sorted(ranks[a])
        out.append({"actor": a, "median rank": rs[n_boot // 2],
                    "95% rank interval": f"{rs[int(0.025*n_boot)]}-{rs[int(0.975*n_boot)]}",
                    "P(top 3)": round(sum(1 for r in rs if r <= 3) / n_boot, 2)})
    return out


def communities(g):
    u = undirected(g) if g.is_directed() else g
    louvain = u.community_multilevel(weights="weight")
    leiden = u.community_leiden(objective_function="modularity",
                                weights="weight", n_iterations=20)
    out = {}
    for name, part in (("louvain", louvain), ("leiden", leiden)):
        tops = []
        for c in sorted(range(len(part)), key=lambda c: -len(part[c]))[:8]:
            members = sorted(part[c], key=lambda i: -u.degree(i))[:4]
            tops.append(f"n={len(part[c])}: " + ", ".join(u.vs[i]["name"] for i in members))
        out[name] = {"k": len(part), "modularity": round(part.modularity, 3),
                     "largest": tops}
    return out


def main():
    rng = random.Random(SEED)
    ig.set_random_number_generator(random.Random(SEED))
    rows = load_letter_persons()
    no_byblos = [r for r in rows if r["sender"] != "ribhadda"]

    # Median dossier size among senders (the volume-equalization cap).
    by_sender = Counter(r["sender"] for r in rows if r["sender"])
    sizes = sorted(by_sender.values())
    cap = sizes[len(sizes) // 2]

    variants = {"all letters": rows, "without Byblos dossier": no_byblos}

    L = []
    a = L.append
    a("# Phase 3 Report — The Mention Network: Where the Small World Lives")
    a("")
    a(f"Generated by `scripts/phase3_analysis.py` (seed {SEED}). Input: "
      f"`data/derived/letter_persons.csv` (from `build_mentions.py`).")
    a("")
    a("**Scope caveat:** EA 1-44 (Great Powers) are not yet lemmatized in")
    a("Oracc, so this layer covers the vassal correspondence + the released")
    a("royal letters. Cline & Cline's 246-person graph included EA 1-44.")
    a("")
    a("## 1. Global descriptives")
    for name, rs in variants.items():
        a(f"\n### {name}")
        a(fmt_dict(global_stats(build_mention(rs))))
    a("")
    a("## 2. Clustering vs nulls — the replication target (CC 0.391, '48.75x')")
    for name, rs in variants.items():
        a(f"\n### {name}")
        a(fmt_dict(null_clustering(build_mention(rs), rng)))
        a(fmt_dict(bipartite_null_clustering(rs, rng)))
    a("")
    a("## 2b. Cline-style construction (sender-star mentions + correspondence)")
    a("")
    star = build_star(rows)
    a(fmt_dict(global_stats(star)))
    a(fmt_dict(null_clustering(star, rng)))
    a("")
    a("Top betweenness under the Cline-style construction:")
    a("")
    a(fmt_table(betweenness_rows(star, top=8)))
    a("")
    a("## 2c. Sensitivity: splitting the pharaohs (Cline & Cline's node definition)")
    a("")
    a("Their headline — Rib-Hadda's betweenness beats Amenhotep III and")
    a("Akhenaten — used *individual* pharaoh nodes. Rebuilding the")
    a("Cline-style graph with the PHARAOH node split per letter by the")
    a("catalogue's named-pharaoh identification (unidentified letters keep a")
    a("generic node):")
    a("")
    named_ph = {}
    with (DERIVED / "edges_corr.csv").open() as fh:
        for e in csv.DictReader(fh):
            named_ph[e["id_text"]] = e["named_pharaoh"]

    def split_pharaoh(rows_in):
        out = []
        for r in rows_in:
            np_ = named_ph.get(r["id_text"], "")
            tag = ("pharaoh-" + np_.split(" of ")[0].replace(" ", "-").lower()
                   if np_ else "pharaoh-unidentified")
            out.append({**r,
                        "sender": tag if r["sender"] == "pharaoh" else r["sender"],
                        "group": [tag if p == "pharaoh" else p for p in r["group"]]})
        return out

    split_rows = split_pharaoh(rows)
    star_split = build_star_from(split_rows, named_ph)
    a(fmt_table(betweenness_rows(star_split, top=8)))
    a("")
    a("## 3. Betweenness (mention layer, all letters)")
    a("")
    g = build_mention(rows)
    bet_rows = betweenness_rows(g)
    a(fmt_table(bet_rows))
    a("")
    focus = [r["actor"] for r in bet_rows[:6]]
    a("## 4. RQ1 — rank stability and the dossier correction")
    a("")
    a("### 4a. Plain bootstrap (resample letters with replacement)")
    a("")
    a(fmt_table(bootstrap_ranks(rows, focus, rng)))
    a("")
    a(f"### 4b. Dossier-equalized (every sender capped at {cap} letters = "
      "median dossier)")
    a("")
    a(fmt_table(bootstrap_ranks(rows, focus, rng, dossier_cap=cap)))
    a("")
    a("## 5. Communities")
    a("")
    for algo, d in communities(g).items():
        a(f"### {algo}")
        a(f"- k = {d['k']}, modularity = {d['modularity']}")
        for line in d["largest"]:
            a(f"- {line}")
        a("")

    a("## 6. Interpretation")
    a("")
    a("**The 'small world' is real but construction-dependent and far more")
    a("modest than claimed.** Person-to-person co-occurrence clustering is")
    a("0.42 — same ballpark as Cline & Cline's 0.391 — and their ER-style")
    a("comparison would let us proclaim '14x random'. But cliques manufacture")
    a("triangles mechanically: against the bipartite configuration null")
    a("(letter sizes and person frequencies preserved), the observed CC of")
    a("0.42 stands against a null median of 0.26. The honest sentence is:")
    a("*clustering exceeds the fair null by ~1.6x, not 49x* — genuine social")
    a("structure, mostly explained by who-appears-in-letters-together.")
    a("")
    a("**Cline & Cline's Rib-Hadda finding replicates under their")
    a("construction and dissolves under bias correction.** In the")
    a("sender-star + correspondence graph (closest to their hand-coded")
    a("object), Rib-Hadda is #2 in betweenness behind only the collapsed")
    a("PHARAOH node — and since they *split* the pharaohs (Amenhotep III vs")
    a("Akhenaten vs 'the king'), each individual pharaoh falls below him —")
    a("section 2c CONFIRMS this: split the pharaohs and Rib-Hadda (4625)")
    a("beats Amenhotep IV (3304) and Amenhotep III (1084), exactly their")
    a("headline, but only because the residual 'unidentified pharaoh' node")
    a("(18208) absorbs most royal traffic. Their most famous finding is an")
    a("artifact of splitting one actor's identity across three nodes under")
    a("uncertainty. In the person-to-person layer Rib-Hadda is only")
    a("#6, and with dossiers equalized at the median (2 letters/sender) he")
    a("falls to median rank 13 with P(top-3) = 0.0.")
    a("")
    a("**The structural brokers of the vassal network are Aziru and")
    a("Yanhamu.** Aziru of Amurru holds top betweenness in every variant")
    a("(P(top-3) = 0.99 even dossier-equalized) — the defector who bridged")
    a("Egypt's orbit and Hatti's. Yanhamu, the Egyptian commissioner, rises")
    a("to #2 (P(top-3) = 0.86) once volume is corrected — precisely RQ1's")
    a("hypothesis that officials, not the loudest vassal, carried the")
    a("network. Rib-Hadda's fame is a fact about his archive, not his")
    a("position.")
    a("")
    a("**Community structure is real in this layer** (modularity ~0.56, k~35")
    a("with ~8 substantive blocks) and the big communities read as political")
    a("theatres: the Amurru crisis (Aziru/ʿAbdi-Aširta/Rib-Hadda/Yanhamu),")
    a("the Damascus-Qadesh axis (Biryawaza/Etakkama), the Shechem-Jerusalem")
    a("conflict (Labaya/ʿAbdi-Heba), the Tyre-Sidon feud (Zimreddi/")
    a("Abi-Milku). Phase 4 SBMs will test these against the tier partition.")
    a("")
    a("**Caveats:** EA 1-44 mentions are absent (not yet lemmatized) — the")
    a("Great-Power brotherhood is invisible here, which depresses clustering")
    a("relative to Cline & Cline's corpus; entity resolution is registry-v1")
    a("(one pass, unadjudicated); the bipartite null dedupes within-letter")
    a("repeats, slightly shrinking group sizes (conservative direction).")
    a("")
    REPORT.write_text("\n".join(L))
    print(f"wrote {REPORT}")
    print(f"(dossier cap = {cap}; senders = {len(by_sender)})")


if __name__ == "__main__":
    main()
