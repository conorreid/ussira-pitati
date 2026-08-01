"""Generate the data-driven site pages (site/accusations.html,
site/people.html) from the registries and derived tables.

Hand-written pages (index, audit) are authored directly in site/;
these two regenerate from data so the site can never drift from the
registries. Deterministic; run after build_network/build_mentions.
"""

import csv
import html
import re
from collections import Counter

from oracc_lib import DERIVED, ROOT

SITE = ROOT / "site"

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — uššira piṭāti</title>
<meta name="description" content="{desc}">
<link rel="stylesheet" href="style.css">
</head>
<body>

<h1>{h1}</h1>
<p class="tagline">{tagline}</p>

<nav><ul>
<li><a href="index.html">Home</a></li>
<li><a href="letters.html">Letters index</a></li>
<li><a href="people.html">Dramatis personae</a></li>
<li><a href="accusations.html">The accusations</a></li>
<li><a href="audit.html">The gazetteer audit</a></li>
<li><a href="paper.pdf">Paper (PDF)</a></li>
</ul></nav>
"""

FOOT = """
<footer>
<p><a href="index.html">&larr; uššira piṭāti</a> &middot; Conor Reid
&middot; 2026 &middot; CC-BY 4.0 &middot; generated from the
repository&rsquo;s evidence-quoted registries by
<span class="num">scripts/build_site_pages.py</span></p>
</footer>

</body>
</html>
"""

# One-line roles for the principals, from Moran (1992) / standard
# literature. Hand-curated; actors without a note get stats only.
ROLES = {
    "pharaoh": "The court itself — Amenhotep III and Akhenaten, collapsed "
               "to one node; addressee of nearly every letter.",
    "ribhadda": "Mayor of Byblos and the archive's most prolific voice: "
                "63 letters, most of them demanding archers that never "
                "came. Eventually exiled by his own brother.",
    "abdiasirta": "Founder of Amurru's fortunes, accused from every side "
                  "of feeding towns to the ʿApiru; dead by EA 101.",
    "aziru": "ʿAbdi-Aširta's son. Played Egypt and Hatti against each "
             "other, captured Ṣumur, and finally defected to the "
             "Hittites — the corrected network's top broker.",
    "yanhamu": "Egyptian commissioner, probably the most powerful "
               "official in Canaan; vassals beg him for grain and fear "
               "his displeasure. Second broker once volume is corrected.",
    "abdiheba": "Ruler of Jerusalem, warning pharaoh that 'the lands of "
                "the king are lost' to the ʿApiru and his neighbors.",
    "labayu": "The 'lion' of Shechem, scourge of the Jezreel valley; "
              "killed by the men of Gina while being extradited.",
    "milkiilu": "Mayor of Gezer; ʿAbdi-Ḫeba's chief enemy in the south.",
    "suwardata": "Mayor of Gath; feuded with ʿAbdi-Ḫeba, then allied "
                 "with him against the ʿApiru (EA 366).",
    "zimreddi": "Mayor of Sidon; accused by Tyre of joining Aziru's side.",
    "abimilku": "Mayor of Tyre, cut off from water and mainland by "
                "Sidon; wrote elegant hymns to pharaoh while besieged.",
    "biryawaza": "Egypt's man in Damascus, holding the line in the "
                 "Beqaa against Qadesh.",
    "etakkama": "Ruler of Qadesh; went over to the Hittites and "
                "attacked his neighbors with Hittite troops.",
    "akizzi": "Ruler of Qatna, pleading loyalty as the Hittite storm "
              "broke over Syria.",
    "tusratta": "King of Mittani, 'brother' of pharaoh; sender of the "
                "longest letters in the archive, including one in "
                "Hurrian.",
    "burnaburiasii": "Kassite king of Babylon, connoisseur of gold and "
                     "diplomatic slights.",
    "pahanate": "Egyptian commissioner at Ṣumur — the addressee the "
                "catalogue mistook for pharaoh (EA 62).",
    "amanappa": "Egyptian official, Rib-Hadda's patron at court "
                "('father and lord').",
    "biridiya": "Mayor of Megiddo, Labʾayu's chief victim.",
    "ammunira": "Mayor of Beirut, Rib-Hadda's last refuge in exile.",
}


def esc(s):
    return html.escape(s, quote=False)


def load_nodes():
    with (DERIVED / "nodes.csv").open() as fh:
        return {r["actor_id"]: r for r in csv.DictReader(fh)}


def disp(nodes, a):
    n = nodes.get(a)
    if n:
        return n["display"]
    return a.replace("-", " ")


def people_page(nodes):
    sent, recv = Counter(), Counter()
    with (DERIVED / "edges_corr.csv").open() as fh:
        for r in csv.DictReader(fh):
            sent[r["src"]] += 1
            recv[r["dst"]] += 1
    mdeg = Counter()
    with (DERIVED / "edges_mention.csv").open() as fh:
        for r in csv.DictReader(fh):
            mdeg[r["actor_i"]] += 1
            mdeg[r["actor_j"]] += 1

    score = Counter()
    for a in set(sent) | set(recv) | set(mdeg):
        score[a] = sent[a] + recv[a] + mdeg[a]
    # principals first (all noted actors), then top of the rest
    order = [a for a in ROLES if a in score]
    order.sort(key=lambda a: -score[a])
    rest = [a for a, _ in score.most_common(40) if a not in ROLES][:12]

    L = [HEAD.format(
        title="Dramatis personae",
        desc="The cast of the Amarna letters: who wrote, who received, "
             "who was talked about.",
        h1="Dramatis personae",
        tagline="Who wrote, who received, who was talked about. Counts "
                "are computed from the derived tables; the one-line "
                "roles follow Moran (1992).")]
    a = L.append
    a("<figure>")
    a('<img src="figures/fig8_dossiers.png" alt="Bar chart of letters '
      'per sender; Rib-Hadda dwarfs everyone">')
    a("<figcaption><b>The dossier skew.</b> Letters per sender, top 15. "
      "Rib-Hadda's 63 letters are the reason volume corrections matter: "
      "count a man's own dossier and he looks central.</figcaption>")
    a("</figure>")
    a("<h2>The principals</h2>")
    a("<table>")
    a("<tr><th>who</th><th>polity</th><th>letters<br>sent</th>"
      "<th>letters<br>recv&rsquo;d</th><th>mention<br>degree</th>"
      "<th>role</th></tr>")
    for actor in order:
        n = nodes.get(actor, {})
        a(f"<tr><td><b>{esc(disp(nodes, actor))}</b></td>"
          f"<td>{esc(n.get('polity', '') or '&mdash;')}</td>"
          f"<td class='num'>{sent[actor]}</td>"
          f"<td class='num'>{recv[actor]}</td>"
          f"<td class='num'>{mdeg[actor]}</td>"
          f"<td>{esc(ROLES[actor])}</td></tr>")
    a("</table>")
    a("<h2>Also appearing</h2>")
    a("<table>")
    a("<tr><th>who</th><th>polity</th><th>letters sent</th>"
      "<th>mention degree</th></tr>")
    for actor in rest:
        n = nodes.get(actor, {})
        a(f"<tr><td>{esc(disp(nodes, actor))}</td>"
          f"<td>{esc(n.get('polity', '') or '&mdash;')}</td>"
          f"<td class='num'>{sent[actor]}</td>"
          f"<td class='num'>{mdeg[actor]}</td></tr>")
    a("</table>")
    a("<p>Plus some two hundred more: messengers, daughters sent to "
      "distant courts, commissioners, and men remembered only because "
      "someone accused them of something. The full actor table is "
      "<span class='num'>data/derived/nodes.csv</span> in "
      "<a href='https://git.sr.ht/~calgacus/ussira-pitati'>the "
      "repository</a>.</p>")
    a(FOOT)
    (SITE / "people.html").write_text("\n".join(L))
    print("  people.html")


def accusations_page(nodes):
    with (ROOT / "registry" / "conflict_edges.csv").open() as fh:
        rows = list(csv.DictReader(fh))
    rows.sort(key=lambda r: r["ea"])
    n_acc = sum(1 for r in rows if r["sign"] == "-")
    n_all = len(rows) - n_acc

    L = [HEAD.format(
        title="The accusations",
        desc="Every accusation and alliance hand-coded from the Amarna "
             "letters, with its source quotation.",
        h1="The accusations",
        tagline=f"{n_acc} accusations and {n_all} alliances, hand-coded "
                "from hostile and allied language across 40 letters — "
                "every row carries its quotation (Moran 1992, "
                "cross-checked against Rainey 2015; cross-edition "
                "&kappa; = 0.86).")]
    a = L.append
    a("<figure>")
    a('<img src="figures/fig6_conflict.png" alt="Signed conflict network '
      'diagram: accusation and alliance edges between actors">')
    a("<figcaption><b>The signed conflict network.</b> Red = accusation, "
      "blue = alliance. The three theatres — the Amurru crisis, the "
      "Damascus&ndash;Qadesh axis, the southern hill country — are "
      "invisible in the correspondence layer, where nearly every letter "
      "just goes to Egypt.</figcaption>")
    a("</figure>")
    a("<p>A reading note: these are <i>claims</i>, not facts. Rib-Hadda "
      "accusing Aziru tells us what Rib-Hadda wanted pharaoh to believe. "
      "The network of who-accuses-whom is real political structure "
      "either way — you denounce the neighbor who threatens you.</p>")
    a("<table>")
    a("<tr><th>EA</th><th>who</th><th></th><th>whom</th>"
      "<th>in their words</th></tr>")
    for r in rows:
        arrow = ("accuses" if r["sign"] == "-" else
                 "<b style='color:#0000aa'>allies with</b>")
        quote = esc(r["evidence_quote"]) or "<i>(see notes column in " \
            "the registry)</i>"
        ea = re.sub(r"EA 0+", "EA ", r["ea"])
        a(f"<tr><td class='num'>{esc(ea)}</td>"
          f"<td>{esc(disp(nodes, r['src']))}</td>"
          f"<td>{arrow}</td>"
          f"<td>{esc(disp(nodes, r['dst']))}</td>"
          f"<td>&ldquo;{quote}&rdquo;</td></tr>")
    a("</table>")
    a("<p>Machine-readable, with coder provenance and tranche flags: "
      "<span class='num'>registry/conflict_edges.csv</span>. The "
      "independent Rainey-based recode is "
      "<span class='num'>conflict_edges_rainey.csv</span>; divergences "
      "between the two editions are tabulated in "
      "<span class='num'>coding_reliability.md</span>. A second human "
      "coder is still wanted — the codebook is in the repository if "
      "you are an Assyriologist with an afternoon.</p>")
    a(FOOT)
    (SITE / "accusations.html").write_text("\n".join(L))
    print("  accusations.html")


def letters_page(nodes):
    import json
    cat = json.loads((ROOT / "data" / "raw" / "aemw" / "amarna" /
                      "catalogue.json").read_text())["members"]
    resolved = {}
    with (DERIVED / "edges_corr.csv").open() as fh:
        for r in csv.DictReader(fh):
            resolved[r["ea"]] = r

    def mark(name, conf):
        if conf in ("restored", "disputed", "unknown"):
            return f"{name}<sup>?</sup>"
        return name

    entries = []
    for m in cat.values():
        if m.get("genre") != "letter":
            continue
        des = m["designation"]
        num = re.match(r"EA (\d+)([a-z]?)", des)
        key = (int(num.group(1)), num.group(2)) if num else (9999, "")
        r = resolved.get(des)
        if r:
            frm = mark(esc(disp(nodes, r["src"])), r["src_confidence"])
            to = mark(esc(disp(nodes, r["dst"])), r["dst_confidence"])
            has_text = r["has_text"] == "True"
            prov = r["provenience"]
        else:
            frm = f"<span style='color:#777'>{esc(m.get('ancient_author') or '?')}</span>"
            to = f"<span style='color:#777'>{esc(m.get('recipient') or '?')}</span>"
            has_text = (ROOT / "data" / "raw" / "aemw" / "amarna" /
                        "corpusjson" / f"{m['id_text']}.json").exists()
            prov = m.get("provenience", "")
        link = (f"<a href='http://oracc.museum.upenn.edu/aemw/amarna/"
                f"{m['id_text']}'>text</a>" if has_text else "&mdash;")
        ea_short = re.sub(r"EA 0+", "EA ", des)
        entries.append((key, ea_short, frm, to, prov, link))
    entries.sort()

    n_resolved = sum(1 for e in entries if "color:#777" not in e[2])
    L = [HEAD.format(
        title="Letters index",
        desc="Every letter in the Amarna archive: sender, addressee, "
             "provenience, and a link to the Oracc edition.",
        h1="Letters index",
        tagline=f"All {len(entries)} letters, EA 1&ndash;382. Senders "
                f"and addressees are the pipeline's resolved actors for "
                f"{n_resolved} letters (catalogue strings, grayed, for "
                "the rest); <sup>?</sup> marks restored or disputed "
                "attributions. &ldquo;text&rdquo; links the lemmatized "
                "Oracc edition where one exists.")]
    a = L.append
    a("<table>")
    a("<tr><th>EA</th><th>from</th><th>to</th><th>provenience</th>"
      "<th>edition</th></tr>")
    for _, ea, frm, to, prov, link in entries:
        a(f"<tr><td class='num'>{esc(ea)}</td><td>{frm}</td>"
          f"<td>{to}</td><td>{esc(prov or '')}</td><td>{link}</td></tr>")
    a("</table>")
    a("<p>Not indexed here: the four administrative lists and the "
      "twenty-eight scholarly and literary tablets found with the "
      "archive (probably scribal training texts). Attribution "
      "corrections against Moran (1992) and Rainey (2015) &mdash; "
      "including three outright catalogue errors &mdash; are documented "
      "in <span class='num'>registry/adjudication_queue.csv</span> in "
      "<a href='https://git.sr.ht/~calgacus/ussira-pitati'>the "
      "repository</a>.</p>")
    a(FOOT)
    (SITE / "letters.html").write_text("\n".join(L))
    print("  letters.html")


def main():
    nodes = load_nodes()
    people_page(nodes)
    accusations_page(nodes)
    letters_page(nodes)


if __name__ == "__main__":
    main()
