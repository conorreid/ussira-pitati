"""Publication figures for paper/draft.md -> paper/figures/.

Reads derived tables + generated reports (phase2/phase3), so regenerate
those first (run_all.sh order). Numeric annotations are parsed from the
report markdown rather than recomputed, keeping figures in lockstep with
the pipeline of record. Seed 4711 for all layouts.

Palette: dataviz-validated 4-slot categorical (blue/green/magenta/yellow)
on white; identity never rides color alone (direct labels + marker shape).

Figures:
  1. correspondence star vs mention small world (two-panel networks)
  2. observed clustering vs three nulls (the 49x -> 1.6x decomposition)
  3. Rib-Hadda's betweenness rank across constructions (bump chart)
  4. map: located vassals, letter volume, Egyptian admin centers
  5. map: the gazetteer audit (phantom -> corrected points)
  6. signed conflict network (accusation / alliance)
  7. map: the conflict network in space (paper Figure 6; fig5 is a
     repo/talk asset, not included in the paper)

Basemap: Natural Earth land/rivers/coastline geojson in data/raw/
(fetch commands in README).
"""

import csv
import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

import igraph as ig
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D

from oracc_lib import DERIVED, ROOT

SEED = 4711
FIGDIR = ROOT / "paper" / "figures"
FIGDIR.mkdir(parents=True, exist_ok=True)

# --- palette (dataviz reference, light mode, validated) ---
BLUE, GREEN, MAGENTA, YELLOW = "#2a78d6", "#008300", "#e87ba4", "#eda100"
RED = "#d03b3b"          # status-critical: audit errors only
INK, SEC, MUTED = "#0b0b0b", "#52514e", "#898781"
GRID, BASE = "#e1e0d9", "#c3c2b7"
SURFACE = "#ffffff"
TIER_COLOR = {"egypt": BLUE, "great_power": GREEN, "vassal": MAGENTA,
              "unknown": MUTED, "": MUTED}
TIER_LABEL = {"egypt": "Egypt (court & officials)",
              "great_power": "Great Powers", "vassal": "Vassals",
              "unknown": "unknown"}

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica Neue", "Arial", "DejaVu Sans"],
    "font.size": 8.5, "axes.linewidth": 0.6,
    "axes.edgecolor": BASE, "text.color": INK,
    "axes.labelcolor": SEC, "xtick.color": MUTED, "ytick.color": MUTED,
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "svg.fonttype": "none", "pdf.fonttype": 42,
})


def save(fig, name):
    for ext in ("pdf", "png"):
        fig.savefig(FIGDIR / f"{name}.{ext}", dpi=300,
                    bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)
    print(f"  {name}")


def load_nodes():
    with (DERIVED / "nodes.csv").open() as fh:
        return {r["actor_id"]: r for r in csv.DictReader(fh)}


def corr_dyads():
    w = Counter()
    with (DERIVED / "edges_corr.csv").open() as fh:
        for r in csv.DictReader(fh):
            w[(r["src"], r["dst"])] += 1
    return w


def mention_dyads():
    w = Counter()
    with (DERIVED / "edges_mention.csv").open() as fh:
        for r in csv.DictReader(fh):
            w[(r["actor_i"], r["actor_j"])] += 1
    return w


def fr_layout(g):
    ig.set_random_number_generator(random.Random(SEED))
    return g.layout_fruchterman_reingold(niter=800)


def draw_graph(ax, g, layout, nodes, size_by, label_ids, label_size=6.5,
               edge_w=None, edge_color=None, curved=False):
    xy = {v.index: layout[v.index] for v in g.vs}
    segs, ws, cols = [], [], []
    for e in g.es:
        a, b = list(xy[e.source]), list(xy[e.target])
        sh = e["shift"] if "shift" in e.attributes() else None
        if sh:
            a = [a[0] + sh[0], a[1] + sh[1]]
            b = [b[0] + sh[0], b[1] + sh[1]]
        segs.append([a, b])
        ws.append(edge_w(e) if edge_w else 0.4)
        cols.append(edge_color(e) if edge_color else "#00000022")
    ax.add_collection(LineCollection(segs, linewidths=ws, colors=cols,
                                     zorder=1, capstyle="round"))
    for v in g.vs:
        n = nodes.get(v["name"], {})
        c = TIER_COLOR.get(n.get("tier", ""), MUTED)
        s = size_by(v)
        ax.scatter(*xy[v.index], s=s, color=c, zorder=3,
                   edgecolors=SURFACE, linewidths=0.8)
    for v in g.vs:
        if v["name"] in label_ids:
            n = nodes.get(v["name"], {})
            spec = label_ids[v["name"]]
            if isinstance(spec, tuple):
                disp, dx, dy = spec
            else:
                disp, dx, dy = spec, 0, 4.5
            disp = disp or n.get("display", v["name"])
            ax.annotate(disp, xy[v.index], xytext=(dx, dy),
                        textcoords="offset points",
                        ha="center" if dx == 0 else ("left" if dx > 0
                                                     else "right"),
                        fontsize=label_size, color=INK, zorder=4,
                        path_effects=halo(2.0))
    ax.set_aspect("equal")
    ax.axis("off")


LABELS_MAIN = {
    "pharaoh": "Pharaoh", "ribhadda": "Rib-Hadda", "aziru": "Aziru",
    "yanhamu": "Yanḫamu", "abdiasirta": "ʿAbdi-Aširta",
    "labayu": "Labʾayu", "abdiheba": "ʿAbdi-Ḫeba", "zimreddi": "Zimreddi",
    "biryawaza": "Biryawaza", "etakkama": "Etakkama",
    "tusratta": "Tušratta", "burnaburiasii": "Burna-Buriaš II",
    "abimilku": "Abi-Milku", "akizzi": "Akizzi",
}


def fig1():
    nodes = load_nodes()
    # (a) correspondence
    cw = corr_dyads()
    actors = sorted({a for e in cw for a in e})
    g = ig.Graph(directed=False)
    g.add_vertices(actors)
    idx = {a: i for i, a in enumerate(actors)}
    g.add_edges([(idx[s], idx[d]) for s, d in cw])
    g.es["w"] = [cw[e] for e in cw]
    lay_a = fr_layout(g)
    deg_letters = Counter()
    for (s, d), n in cw.items():
        deg_letters[s] += n
        deg_letters[d] += n

    # (b) mention, largest component
    mw = mention_dyads()
    m_actors = sorted({a for e in mw for a in e})
    gm = ig.Graph()
    gm.add_vertices(m_actors)
    midx = {a: i for i, a in enumerate(m_actors)}
    gm.add_edges([(midx[i], midx[j]) for i, j in mw])
    comp = gm.components()
    gm = comp.giant()
    lay_b = fr_layout(gm)
    mdeg = {v["name"]: gm.degree(v.index) for v in gm.vs}

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 3.7))
    corr_labels = {k: v for k, v in LABELS_MAIN.items()
                   if k in idx and k in ("pharaoh", "ribhadda", "aziru",
                                         "tusratta", "burnaburiasii")}
    draw_graph(ax1, g, lay_a, nodes,
               lambda v: 6 + 3.2 * math.sqrt(deg_letters[v["name"]]),
               corr_labels,
               edge_w=lambda e: 0.3 + 0.25 * math.sqrt(e["w"]))
    ax1.set_title("(a) Correspondence: who wrote to whom",
                  fontsize=9, color=INK, pad=8)
    ax1.text(0.5, -0.04, "111 actors · 302 letters · clustering = 0",
             transform=ax1.transAxes, ha="center", fontsize=7.5, color=SEC)

    keep = {"pharaoh": ("Pharaoh", -8, 5), "tusratta": ("Tušratta", -9, -9),
            "aziru": ("Aziru", 9, -8), "yanhamu": ("Yanḫamu", 11, 6),
            "labayu": ("Labʾayu", 2, 10), "etakkama": ("Etakkama", 2, -12),
            "ribhadda": ("Rib-Hadda", -13, 4)}
    ment_labels = {k: v for k, v in keep.items() if k in set(gm.vs["name"])}
    draw_graph(ax2, gm, lay_b, nodes,
               lambda v: 4 + 1.9 * math.sqrt(mdeg[v["name"]]),
               ment_labels)
    ax2.set_title("(b) Mention: who is named together",
                  fontsize=9, color=INK, pad=8)
    ax2.text(0.5, -0.04,
             "largest component · 244 persons overall · clustering = 0.41",
             transform=ax2.transAxes, ha="center", fontsize=7.5, color=SEC)

    handles = [Line2D([], [], marker="o", ls="", color=TIER_COLOR[t],
                      markersize=6, label=TIER_LABEL[t])
               for t in ("egypt", "great_power", "vassal", "unknown")]
    fig.legend(handles=handles, loc="lower center", ncol=4, frameon=False,
               fontsize=7.5, bbox_to_anchor=(0.5, -0.04))
    save(fig, "fig1_two_layers")


def parse_phase3_nulls():
    txt = (ROOT / "phase3_report.md").read_text()
    sec2 = re.search(r"## 2\. Clustering.*?(?=## 2b)", txt, re.S).group(0)
    out = {}
    for variant in ("all letters", "without Byblos dossier"):
        m = re.search(rf"### {re.escape(variant)}\n" + r"(.*?)(?=###|\Z)",
                      sec2, re.S)
        blk = m.group(1)
        g = lambda k: float(re.search(rf"\*\*{k}\*\*: ([\d.]+)", blk).group(1))
        band = re.search(r"bipartite-null CC \(2\.5%-97\.5%\)\*\*: "
                         r"([\d.]+)-([\d.]+)", blk)
        cfg = re.search(r"config-model CC \(2\.5%-97\.5%\)\*\*: "
                        r"([\d.]+)-([\d.]+)", blk)
        out[variant] = dict(
            obs=g("observed CC"), er=g("ER-expected CC"),
            cfg_med=g(r"config-model CC \(median\)"),
            cfg_lo=float(cfg.group(1)), cfg_hi=float(cfg.group(2)),
            bip_med=g(r"bipartite-null CC \(median\)"),
            bip_lo=float(band.group(1)), bip_hi=float(band.group(2)))
    return out


def fig2():
    n3 = parse_phase3_nulls()
    # correspondence row from phase2: CC exactly 0, config band
    p2 = (ROOT / "phase2_report.md").read_text()
    m = re.search(r"### all letters\n- \*\*observed CC\*\*: ([\d.]+)\n.*?"
                  r"config-model CC \(2\.5%-97\.5%\)\*\*: ([\d.]+)-([\d.]+)",
                  p2, re.S)
    corr = dict(obs=float(m.group(1)), lo=float(m.group(2)),
                hi=float(m.group(3)))

    rows = [
        ("Correspondence\n(all letters)", corr["obs"], None,
         (corr["lo"], corr["hi"]), None, None),
        ("Mention\n(all letters)", n3["all letters"]["obs"],
         n3["all letters"]["er"],
         (n3["all letters"]["cfg_lo"], n3["all letters"]["cfg_hi"]),
         (n3["all letters"]["bip_lo"], n3["all letters"]["bip_hi"]),
         n3["all letters"]),
        ("Mention\n(without Byblos)", n3["without Byblos dossier"]["obs"],
         n3["without Byblos dossier"]["er"],
         (n3["without Byblos dossier"]["cfg_lo"],
          n3["without Byblos dossier"]["cfg_hi"]),
         (n3["without Byblos dossier"]["bip_lo"],
          n3["without Byblos dossier"]["bip_hi"]),
         n3["without Byblos dossier"]),
    ]

    fig, ax = plt.subplots(figsize=(6.6, 2.9))
    ys = [2, 1, 0]
    for y, (name, obs, er, cfg, bip, d) in zip(ys, rows):
        if er is not None:
            ax.plot(er, y, "o", mfc="none", mec=MUTED, ms=6, mew=1.2)
        ax.plot(cfg, [y, y], "-", color="#86b6ef", lw=5, solid_capstyle="round")
        if bip:
            ax.plot(bip, [y, y], "-", color="#1c5cab", lw=5,
                    solid_capstyle="round")
        ax.plot(obs, y, "D", color=INK, ms=7, zorder=5)
    # direct labels, once, on the top mention row
    y = 1
    d = rows[1]
    ax.annotate("ER random\n(the '49×' baseline)", (d[2], y),
                xytext=(d[2], y + 0.42), ha="center", fontsize=7, color=SEC)
    ax.annotate("configuration\nnull", (sum(d[3]) / 2, y),
                xytext=(sum(d[3]) / 2, y + 0.42), ha="center", fontsize=7,
                color=SEC)
    ax.annotate("bipartite\nnull", (sum(d[4]) / 2, y),
                xytext=(sum(d[4]) / 2, y + 0.42), ha="center", fontsize=7,
                color=SEC)
    ax.annotate("observed", (d[1], y), xytext=(d[1], y + 0.42), ha="center",
                fontsize=7, color=INK, fontweight="bold")
    ax.annotate("×16.5 vs ER — but ×1.6 vs the fair null",
                (d[1], y), xytext=(d[1] + 0.005, y - 0.38), fontsize=7,
                color=SEC, ha="center")
    ax.annotate("observed = 0: below its own null band",
                (0.006, 2), xytext=(0.05, 2.0), fontsize=7, color=SEC,
                va="center",
                arrowprops=dict(arrowstyle="-", color=BASE, lw=0.6))
    ax.set_yticks(ys)
    ax.set_yticklabels([r[0] for r in rows], fontsize=8, color=INK)
    ax.set_xlabel("global clustering coefficient", fontsize=8)
    ax.set_xlim(-0.015, 0.56)
    ax.set_ylim(-0.55, 2.75)
    ax.spines[["left", "top", "right"]].set_visible(False)
    ax.tick_params(left=False)
    ax.xaxis.grid(True, color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    save(fig, "fig2_nulls")


def fig3():
    txt = (ROOT / "phase3_report.md").read_text()

    def table_ranks(section_re):
        m = re.search(section_re + r".*?\n\|---[^\n]*\n((?:\|[^\n]*\n)+)", txt, re.S)
        ranks = {}
        i = 0
        for line in m.group(1).strip().split("\n"):
            parts = line.split("|")
            if len(parts) < 3:
                continue
            i += 1
            ranks[parts[1].strip()] = i
        return ranks

    def boot_ranks(section_re):
        m = re.search(section_re + r".*?\n\|---[^\n]*\n((?:\|[^\n]*\n)+)", txt, re.S)
        out = {}
        for line in m.group(1).strip().split("\n"):
            p = [c.strip() for c in line.split("|")[1:-1]]
            if len(p) < 3:
                continue
            lo, hi = p[2].split("-")
            out[p[0]] = (int(p[1]), int(lo), int(hi))
        return out

    split = table_ranks(r"## 2c\.")          # Cline-style, pharaohs split
    coll = table_ranks(r"## 2b\..*?Top betweenness")  # collapsed
    p2p = boot_ranks(r"### 4a\.")
    eq = boot_ranks(r"### 4b\.")

    stages = ["Cline-style,\npharaohs split", "Cline-style,\npharaoh collapsed",
              "person-to-person\nmentions", "dossier-equalized\n(2 letters/sender)"]
    actors = [("ribhadda", "Rib-Hadda", MAGENTA),
              ("aziru", "Aziru", GREEN),
              ("yanhamu", "Yanḫamu", BLUE)]

    fig, ax = plt.subplots(figsize=(6.2, 3.4))
    xs = range(4)
    for aid, name, color in actors:
        series, bands = [], []
        for i, src in enumerate((split, coll, p2p, eq)):
            if aid in src:
                v = src[aid]
                if isinstance(v, tuple):
                    series.append(v[0]); bands.append((v[1], v[2]))
                else:
                    series.append(v); bands.append(None)
            else:
                series.append(None); bands.append(None)
        pts = [(x, r) for x, r in zip(xs, series) if r]
        ax.plot([p[0] for p in pts], [p[1] for p in pts], "-o", color=color,
                lw=2, ms=6, mec=SURFACE, mew=1.2, solid_capstyle="round")
        for x, b in zip(xs, bands):
            if b:
                ax.plot([x, x], list(b), "-", color=color, lw=1.1, alpha=0.45,
                        solid_capstyle="round", zorder=1)
        lx, ly = pts[-1]
        ax.annotate(f"{name}  ({ly})", (lx, ly), xytext=(8, 0),
                    textcoords="offset points", va="center", fontsize=8,
                    color=INK)
        if series[0] is None:
            ax.annotate("not in either star construction", (0, 16.8),
                        fontsize=6.8, color=SEC, ha="left") if aid == "yanhamu" else None
    ax.invert_yaxis()
    ax.set_yticks([1, 3, 5, 7, 9, 11, 13, 15, 20, 25])
    ax.set_ylim(26.5, 0.3)
    ax.set_xticks(list(xs))
    ax.set_xticklabels(stages, fontsize=7.5)
    ax.set_ylabel("betweenness rank (1 = top broker)", fontsize=8)
    ax.set_xlim(-0.3, 3.95)
    ax.spines[["top", "right"]].set_visible(False)
    ax.yaxis.grid(True, color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.set_title("Rib-Hadda's brokerage across constructions",
                 fontsize=9.5, color=INK, pad=8)
    fig.text(0.13, -0.02, "Whiskers on the two mention-layer designs are "
             "bootstrap 95% rank intervals (phase3_report §4).",
             fontsize=7, color=SEC)
    save(fig, "fig3_ribhadda")


LAND, SEA, RIVER = "#f4f1ea", "#e8eff5", "#c3d6e6"


def _rings(geom):
    if geom["type"] == "LineString":
        return [geom["coordinates"]]
    if geom["type"] == "MultiLineString":
        return geom["coordinates"]
    if geom["type"] == "Polygon":
        return geom["coordinates"]
    if geom["type"] == "MultiPolygon":
        return [ring for poly in geom["coordinates"] for ring in poly]
    return []


def _in_bbox(line, lonlim, latlim):
    xs = [p[0] for p in line]
    ys = [p[1] for p in line]
    return not (max(xs) < lonlim[0] or min(xs) > lonlim[1]
                or max(ys) < latlim[0] or min(ys) > latlim[1])


def basemap(ax, lonlim, latlim, detail="10m"):
    """Filled land, rivers, coastline from Natural Earth (data/raw/,
    fetch commands in README). Marks and labels go on top (zorder>=2)."""
    raw = ROOT / "data" / "raw"
    ax.set_facecolor(SEA)
    land = json.loads((raw / "ne_10m_land.geojson").read_text())
    from matplotlib.patches import Polygon as MplPolygon
    for feat in land["features"]:
        for ring in _rings(feat["geometry"]):
            if _in_bbox(ring, lonlim, latlim):
                ax.add_patch(MplPolygon(ring, closed=True, facecolor=LAND,
                                        edgecolor="none", zorder=0.5))
    rivers = json.loads(
        (raw / "ne_10m_rivers_lake_centerlines.geojson").read_text())
    for feat in rivers["features"]:
        for line in _rings(feat["geometry"]):
            if _in_bbox(line, lonlim, latlim):
                ax.plot([p[0] for p in line], [p[1] for p in line], "-",
                        color=RIVER, lw=0.6, zorder=0.8,
                        solid_capstyle="round")
    coast = json.loads((raw / f"ne_{detail}_coastline.geojson").read_text())
    for feat in coast["features"]:
        for line in _rings(feat["geometry"]):
            if _in_bbox(line, lonlim, latlim):
                ax.plot([p[0] for p in line], [p[1] for p in line], "-",
                        color=BASE, lw=0.6, zorder=1)
    ax.set_xlim(lonlim)
    ax.set_ylim(latlim)
    ax.set_aspect(1 / math.cos(math.radians(sum(latlim) / 2)))
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(True); s.set_color(GRID)


def halo(size=2.2):
    import matplotlib.patheffects as pe
    return [pe.withStroke(linewidth=size, foreground=SURFACE)]


# back-compat: fig5 (audit map) still calls coastline() with wide extent
def coastline(ax, lonlim, latlim):
    basemap(ax, lonlim, latlim, detail="50m")


def load_coords():
    with (ROOT / "registry" / "polity_coords.csv").open() as fh:
        return {r["polity"]: (float(r["lon"]), float(r["lat"]))
                for r in csv.DictReader(fh) if r["lat"]}


def fig4():
    pol = load_coords()
    nodes = load_nodes()
    sent = Counter()
    with (DERIVED / "edges_corr.csv").open() as fh:
        for r in csv.DictReader(fh):
            if r["dst"] == "pharaoh":
                p = nodes.get(r["src"], {}).get("polity", "")
                if p in pol and p != "Egypt":
                    sent[p] += 1
    with (ROOT / "registry" / "egyptian_admin_centers.csv").open() as fh:
        centers = {r["center"]: (float(r["lon"]), float(r["lat"]))
                   for r in csv.DictReader(fh)}
    tier_of_pol = {}
    for n in nodes.values():
        if n["polity"]:
            tier_of_pol.setdefault(n["polity"], n["tier"])

    fig, ax = plt.subplots(figsize=(4.4, 5.4))
    basemap(ax, (28.6, 39.4), (26.8, 36.9))
    for p, n in sent.items():
        x, y = pol[p]
        c = TIER_COLOR.get(tier_of_pol.get(p, ""), MUTED)
        ax.scatter(x, y, s=14 + 5.5 * n, color=c, edgecolors=SURFACE,
                   linewidths=0.8, zorder=3, alpha=0.95)
    for name, (x, y) in centers.items():
        ax.scatter(x, y, marker="s", s=26, color=BLUE,
                   edgecolors=SURFACE, linewidths=0.9, zorder=4)
    ax.scatter(*pol["Egypt"], marker="*", s=170, color=BLUE,
               edgecolors=SURFACE, linewidths=0.9, zorder=5)
    ax.annotate("Akhetaten", pol["Egypt"], xytext=(7, -1),
                textcoords="offset points", fontsize=8, color=INK,
                path_effects=halo(), zorder=6)
    offsets = {"Byblos": (9, -4), "Tyre": (-7, -2), "Jerusalem": (7, -3),
               "Ugarit": (6, 2), "Qadesh": (6, -5), "Damascus": (6, 1),
               "Megiddo": (7, -1), "Ashkelon": (-7, 1), "Qatna": (6, 3),
               "Alašiya": (7, 2), "Gazru": (-7, 6)}
    for p, (dx, dy) in offsets.items():
        if p in pol:
            lbl = {"Gazru": "Gezer", "Alašiya": "Alašiya (Enkomi)"}.get(p, p)
            ax.annotate(lbl, pol[p], xytext=(dx, dy),
                        textcoords="offset points", fontsize=7, color=SEC,
                        ha="left" if dx > 0 else "right",
                        path_effects=halo(), zorder=6)
    coff = {"Gaza": (-6, -6), "Sumur": (-7, 0), "Kumidi": (-7, -3)}
    for name, (dx, dy) in coff.items():
        x, y = centers[name]
        ax.annotate({"Sumur": "Ṣumur"}.get(name, name), (x, y),
                    xytext=(dx, dy), textcoords="offset points",
                    fontsize=7, color=SEC, ha="right",
                    path_effects=halo(), zorder=6)
    handles = [
        Line2D([], [], marker="o", ls="", color=MAGENTA, markersize=7,
               label="vassal polity (area scales with letters)"),
        Line2D([], [], marker="o", ls="", color=GREEN, markersize=7,
               label="Great Power in frame"),
        Line2D([], [], marker="s", ls="", color=BLUE, markersize=6,
               label="Egyptian admin center"),
        Line2D([], [], marker="*", ls="", color=BLUE, markersize=11,
               label="Akhetaten (the archive)"),
    ]
    leg = ax.legend(handles=handles, loc="lower right", frameon=True,
                    fontsize=6.8, framealpha=0.9, edgecolor=GRID)
    leg.get_frame().set_facecolor(SURFACE)
    ax.set_title("The corrected geography of the corpus",
                 fontsize=9.5, color=INK, pad=8)
    save(fig, "fig4_map")


def fig5():
    pol = load_coords()
    # phantom -> corrected (old lon/lat from the pre-audit registry, see
    # distance_confounds.md 'Reading' and git history of polity_coords.csv)
    moves = [
        ("'Syria' ×4 actors", (20.679, 38.199), None),
        ("Pihilu (Macedonian Pella)", (22.75, 40.75), pol["Pihilu"]),
        ("Irqata (Anatolian Arca)", (37.971, 38.335), pol["Irqata"]),
        ("Tyre (Tyros in Jordan)", (35.754, 31.915), pol["Tyre"]),
        ("Alašiya (off-island point)", (32.5, 37.5), pol["Alašiya"]),
        ("Hatti (Iron-Age region)", (37.09, 37.03), pol["Hatti"]),
        ("Assyria ('Leukosyria')", (34.5, 41.5), pol["Assyria"]),
    ]
    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    coastline(ax, (19.0, 46.0), (26.5, 43.5))
    for label, old, new in moves:
        ax.scatter(*old, marker="x", s=42, color=RED, linewidths=1.6, zorder=4)
        if new:
            ax.annotate("", xy=new, xytext=old,
                        arrowprops=dict(arrowstyle="->", color=SEC, lw=0.9,
                                        shrinkA=4, shrinkB=4))
            ax.scatter(*new, s=26, color=BLUE, edgecolors=SURFACE,
                       linewidths=0.8, zorder=5)
        off = {"'Syria' ×4 actors": (4, 4), "Assyria ('Leukosyria')": (4, 4),
               "Tyre (Tyros in Jordan)": (5, -9)}.get(label, (4, 4))
        ax.annotate(label, old, xytext=off, textcoords="offset points",
                    fontsize=7, color=INK)
    ax.scatter(*pol["Egypt"], marker="*", s=150, color=BLUE,
               edgecolors=SURFACE, linewidths=0.9, zorder=5)
    ax.annotate("Akhetaten", pol["Egypt"], xytext=(6, -2),
                textcoords="offset points", fontsize=7.5, color=SEC)
    handles = [
        Line2D([], [], marker="x", ls="", color=RED, markersize=7,
               label="phantom location (pre-audit)"),
        Line2D([], [], marker="o", ls="", color=BLUE, markersize=6,
               label="verified location"),
    ]
    ax.legend(handles=handles, loc="lower left", frameon=False, fontsize=7.5)
    ax.set_title("The gazetteer audit: seven phantom coordinates",
                 fontsize=9.5, color=INK, pad=8)
    fig.text(0.13, 0.015, "The 'Syria' region point (four one-letter actors) "
             "has no corrected location: regions are excluded, not imputed.",
             fontsize=7, color=SEC)
    save(fig, "fig5_audit")


def fig6():
    nodes = load_nodes()
    edges = []
    with (ROOT / "registry" / "conflict_edges.csv").open() as fh:
        for r in csv.DictReader(fh):
            edges.append((r["src"], r["dst"], r["sign"]))
    actors = sorted({a for e in edges for a in e[:2]})
    g = ig.Graph(directed=True)
    g.add_vertices(actors)
    idx = {a: i for i, a in enumerate(actors)}
    seen = Counter()
    for s, d, sign in edges:
        seen[(s, d, sign)] += 1
    g.add_edges([(idx[s], idx[d]) for s, d, sign in seen])
    g.es["sign"] = [sign for (_, _, sign) in seen]
    g.es["n"] = [seen[k] for k in seen]
    lay = fr_layout(g)
    deg = {a: 0 for a in actors}
    for s, d, _ in edges:
        deg[s] += 1
        deg[d] += 1

    # nudge parallel opposite-sign edges apart so a dyad that both
    # accuses and allies (Suwardata <-> Abdi-Heba, EA 366) shows two
    # distinct lines instead of a muddy overlap
    both = {frozenset((s, d)) for s, d, sg in seen if sg == "-"} & \
           {frozenset((s, d)) for s, d, sg in seen if sg == "+"}

    fig, ax = plt.subplots(figsize=(6.4, 4.6))
    for e in g.es:
        if frozenset((g.vs[e.source]["name"], g.vs[e.target]["name"])) in both:
            a, b = lay[e.source], lay[e.target]
            dx, dy = b[0] - a[0], b[1] - a[1]
            norm = math.hypot(dx, dy) or 1
            off = 0.06 if e["sign"] == "-" else -0.06
            e["shift"] = (-dy / norm * off, dx / norm * off)
    labels6 = ({k: v for k, v in LABELS_MAIN.items() if k in idx} |
               {"milkiilu": ("Milki-ilu", -8, 3), "suwardata": ("Šuwardata", 9, -2),
                "ilirapih": "Ili-Rapiḫ",
                "sons-of-abdiasirta": ("sons of ʿA.-Aširta", 0, -11),
                "sons-of-labaya": ("sons of Labʾayu", 9, 2),
                "abdiheba": ("ʿAbdi-Ḫeba", -9, 3)})
    shift_lay = [list(p) for p in lay]
    draw_graph(ax, g, lay, nodes,
               lambda v: 8 + 4.5 * math.sqrt(deg[v["name"]]),
               labels6,
               edge_w=lambda e: 0.8 + 0.3 * e["n"],
               edge_color=lambda e: RED if e["sign"] == "-" else BLUE)
    handles = [
        Line2D([], [], color=RED, lw=2, label="accusation (59 edges)"),
        Line2D([], [], color=BLUE, lw=2, label="alliance (4 edges)"),
    ]
    ax.legend(handles=handles, loc="lower right", frameon=False, fontsize=7.5)
    ax.set_title("The signed conflict network (hand-coded, 40 letters)",
                 fontsize=9.5, color=INK, pad=8)
    save(fig, "fig6_conflict")


def fig7():
    """The conflict network drawn geographically: accusation/alliance
    edges between located polities. Neighbors accuse neighbors."""
    pol = load_coords()
    nodes = load_nodes()
    polity_of = {a: n["polity"] for a, n in nodes.items() if n["polity"]}
    agg = Counter()          # (polityA, polityB, sign) -> letters
    skipped_unlocated, intra = set(), 0
    with (ROOT / "registry" / "conflict_edges.csv").open() as fh:
        for r in csv.DictReader(fh):
            pa = polity_of.get(r["src"]); pb = polity_of.get(r["dst"])
            if not pa or not pb or pa not in pol or pb not in pol:
                for a, p in ((r["src"], pa), (r["dst"], pb)):
                    if not p or p not in pol:
                        skipped_unlocated.add(a)
                continue
            if pa == pb:
                intra += 1
                continue
            key = (min(pa, pb), max(pa, pb), r["sign"])
            agg[key] += 1

    fig, ax = plt.subplots(figsize=(5.2, 5.0))
    basemap(ax, (33.6, 37.6), (30.9, 36.2))
    involved = Counter()
    for (pa, pb, sign), n in agg.items():
        involved[pa] += n; involved[pb] += n
        (x1, y1), (x2, y2) = pol[pa], pol[pb]
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        dx, dy = x2 - x1, y2 - y1
        norm = math.hypot(dx, dy) or 1
        cx, cy = mx - dy / norm * 0.18, my + dx / norm * 0.18
        ts = [t / 24 for t in range(25)]
        xs = [(1 - t) ** 2 * x1 + 2 * (1 - t) * t * cx + t ** 2 * x2
              for t in ts]
        ys = [(1 - t) ** 2 * y1 + 2 * (1 - t) * t * cy + t ** 2 * y2
              for t in ts]
        color = RED if sign == "-" else BLUE
        ax.plot(xs, ys, "-", color=color, lw=0.9 + 0.55 * n,
                alpha=0.85, zorder=3, solid_capstyle="round")
    for p, n in involved.items():
        ax.scatter(*pol[p], s=26 + 12 * n, color=MAGENTA,
                   edgecolors=SURFACE, linewidths=0.9, zorder=4)
    lab = {"Byblos": (7, 2), "Tyre": (-8, -1), "Sidon": (-8, 1),
           "Beirut": (-8, 2), "Qadesh": (7, 2), "Damascus": (7, -2),
           "Qatna": (7, 2), "Jerusalem": (8, -4), "Gazru": (-8, -6),
           "Gimtu": (-9, -9), "Megiddo": (8, 0), "Akka": (-8, 2),
           "Šakmu": (8, -2), "Aštartu": (8, 2), "Pihilu": (8, -4),
           "Irqata": (-8, 3), "Ugarit": (7, 2), "Hazor": (8, 1),
           "Lakiša": (-8, -3), "Ashkelon": (-8, 1), "Tunip": (7, 1)}
    shown = {"Gazru": "Gezer", "Gimtu": "Gath", "Šakmu": "Shechem",
             "Lakiša": "Lachish"}
    for p, n in involved.items():
        dx, dy = lab.get(p, (7, 2))
        ax.annotate(shown.get(p, p), pol[p], xytext=(dx, dy),
                    textcoords="offset points", fontsize=7, color=INK,
                    ha="left" if dx > 0 else "right",
                    path_effects=halo(), zorder=6)
    n_acc = sum(n for (a, b, s), n in agg.items() if s == "-")
    n_all = sum(n for (a, b, s), n in agg.items() if s == "+")
    handles = [
        Line2D([], [], color=RED, lw=2,
               label=f"accusation ({n_acc} located letter-edges)"),
        Line2D([], [], color=BLUE, lw=2, label=f"alliance ({n_all})"),
    ]
    leg = ax.legend(handles=handles, loc="lower left", frameon=True,
                    fontsize=7, framealpha=0.9, edgecolor=GRID)
    leg.get_frame().set_facecolor(SURFACE)
    ax.set_title("The conflict network in space", fontsize=9.5,
                 color=INK, pad=8)
    dropped = (f" and {intra} intra-polity edges" if intra else "")
    fig.text(0.12, 0.02,
             f"Curved lines connect the polities of accuser and accused; "
             f"width scales with letters. Edges involving\n"
             f"unlocated actors (collectives, the ʿApiru, fragmentary "
             f"names){dropped} are not drawn.",
             fontsize=6.6, color=SEC)
    save(fig, "fig7_conflict_map")


def fig8():
    """Letters per sender, top 15: the dossier skew behind the
    Rib-Hadda story (site figure; not in the paper)."""
    nodes = load_nodes()
    sent = Counter()
    with (DERIVED / "edges_corr.csv").open() as fh:
        for r in csv.DictReader(fh):
            sent[r["src"]] += 1
    top = sent.most_common(15)
    fig, ax = plt.subplots(figsize=(6.0, 4.2))
    ys = range(len(top))[::-1]
    for y, (a, n) in zip(ys, top):
        c = TIER_COLOR.get(nodes.get(a, {}).get("tier", ""), MUTED)
        ax.barh(y, n, height=0.62, color=c, zorder=3)
        ax.annotate(str(n), (n, y), xytext=(4, 0),
                    textcoords="offset points", va="center", fontsize=7.5,
                    color=INK)
    ax.set_yticks(list(ys))
    labels = []
    for a, n in top:
        d = nodes.get(a, {}).get("display", a)
        p = nodes.get(a, {}).get("polity", "")
        labels.append(f"{d}" + (f"  ({p})" if p else ""))
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlabel("letters in the archive", fontsize=8)
    ax.set_xlim(0, max(n for _, n in top) * 1.09)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(left=False)
    ax.xaxis.grid(True, color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.set_title("One fifth of the archive is one man complaining",
                 fontsize=9.5, color=INK, pad=8)
    save(fig, "fig8_dossiers")


if __name__ == "__main__":
    print("figures ->", FIGDIR)
    fig1()
    fig2()
    fig3()
    fig4()
    fig5()
    fig6()
    fig7()
    fig8()
