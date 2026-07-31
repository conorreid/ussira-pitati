"""Build the correspondence network tables (Weeks 5-7 deliverable).

Joins the catalogue's structured sender/recipient fields with the parsed
header validation (data/derived/headers.csv) to produce:

    data/derived/nodes.csv       one row per resolved actor
    data/derived/edges_corr.csv  one row per letter: sender -> addressee

Resolution policy (PLAN.md §3.2-3.3):
- Catalogue fields are the primary source; the parsed formula corroborates.
- confidence: certain  = catalogue and parsed formula agree
              probable = one source only, or a hedged '(?)' catalogue value
              restored = catalogue value is entirely an editorial [bracket]
              disputed = catalogue and parsed formula disagree
- All named pharaohs collapse to a single PHARAOH node (base analysis);
  the named identification is kept in named_pharaoh for the sensitivity split.
- Unnamed-but-locatable senders ('the citizens of Tunip', '[the queen of
  Ugarit]') become nodes flagged is_named=False rather than being dropped:
  they are letter endpoints, and edges need endpoints.
"""

import csv
import re

from oracc_lib import DERIVED, ROOT, corpus_files, fold, load_catalogue, parse_ea

ALIASES = {}
with (ROOT / "registry" / "canonical_registry.csv").open() as fh:
    for row in csv.DictReader(fh):
        ALIASES[row["folded_variant"]] = row["folded_canonical"]

GREAT_POWERS = {"babylon", "babylonia", "assyria", "mittani", "mitanni",
                "hatti", "arzawa", "alashiya", "alasiya"}
PHARAOH_MARKERS = ("pharaoh", "amenhotep", "akhenaten", "tutankhamun",
                   "neferneferuaten", "smenkhkare")


def slug(s):
    import unicodedata
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.replace("ʾ", "").replace("ʿ", "")
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower().strip())).strip("-")


def is_pharaoh(raw):
    r = raw.lower()
    return any(m in r for m in PHARAOH_MARKERS) and "official" not in r


def parse_catalogue_actor(raw):
    """Resolve one catalogue actor string to a dict:
    {actor_id, display, polity, tier, is_named, named_pharaoh, hedged, restored}
    Returns None if the value is empty/missing."""
    if not raw:
        return None
    s = raw.strip()
    restored = s.startswith("[") and s.endswith("]")
    s = s.strip("[]").strip()
    hedged = "(?)" in s
    s = s.replace("(?)", "").strip()
    if not s or s.lower() in ("missing", "unknown"):
        return None

    if is_pharaoh(s):
        named = s if not s.lower().startswith(("an egyptian", "the egyptian")) else ""
        return dict(actor_id="pharaoh", display="PHARAOH", polity="Egypt",
                    tier="egypt", is_named=bool(named), named_pharaoh=named,
                    hedged=hedged, restored=restored)

    # 'NN, mayor/ruler/king of PLACE' | 'NN of PLACE' | 'the king/city/citizens of PLACE'
    polity = ""
    m = re.search(r"(?:of|in) ([A-ZŠṢṬʿʾ][\w'ʾʿšṣṭḫāēīū-]*)$", s)
    if m:
        polity = m.group(1)
    name = s.split(",")[0].strip()
    unnamed = bool(re.match(r"(the|a|an) ", name, re.I))
    if unnamed:
        name = s  # keep the whole description for display

    egyptian = "egyptian" in s.lower() or polity.lower() == "egypt"
    if egyptian:
        tier = "egypt"
    elif fold(polity) in GREAT_POWERS:
        tier = "great_power"
    else:
        tier = "vassal"

    if not unnamed and polity:
        name = re.sub(rf"\s+of\s+{re.escape(polity)}$", "", name)
    display = name if not unnamed else s
    # Named actors key on the alias-canonical folded name so catalogue
    # spelling variants (Šub-Andu / Šubandu) merge; unnamed ones on the
    # full description.
    folded = fold(name)
    actor_id = ALIASES.get(folded, folded) if not unnamed and folded else slug(display)
    return dict(actor_id=actor_id, display=display, polity=polity,
                tier=tier, is_named=not unnamed, named_pharaoh="",
                hedged=hedged, restored=restored)


def confidence(actor, agree_flag):
    if actor is None:
        return None
    if agree_flag == "True":
        return "certain"
    if agree_flag == "False":
        return "disputed"
    if actor["restored"]:
        return "restored"
    return "probable"


def main():
    cat = load_catalogue()["members"]
    pfiles = corpus_files()

    parsed = {}
    with (DERIVED / "headers.csv").open() as fh:
        for row in csv.DictReader(fh):
            parsed[row["id_text"]] = row

    nodes = {}   # actor_id -> node dict (+ counters)
    edges = []

    def register(actor):
        n = nodes.setdefault(actor["actor_id"], {
            "actor_id": actor["actor_id"], "display": actor["display"],
            "polity": actor["polity"], "tier": actor["tier"],
            "is_named": actor["is_named"], "n_sent": 0, "n_received": 0,
        })
        if actor["polity"] and not n["polity"]:
            n["polity"] = actor["polity"]
        return n

    n_letters = n_no_sender = n_no_addressee = 0
    for pid, v in sorted(cat.items(), key=lambda kv: kv[1]["designation"]):
        if v.get("genre") != "letter":
            continue
        n_letters += 1
        p = parsed.get(pid, {})
        sender = parse_catalogue_actor(v.get("ancient_author", ""))
        addressee = parse_catalogue_actor(v.get("recipient", ""))
        s_conf = confidence(sender, p.get("sender_agree", ""))
        a_conf = confidence(addressee, p.get("addressee_agree", ""))

        if sender is None:
            n_no_sender += 1
        if addressee is None:
            n_no_addressee += 1
        if sender is None or addressee is None:
            continue

        register(sender)["n_sent"] += 1
        register(addressee)["n_received"] += 1
        ea = parse_ea(v["designation"])
        edges.append({
            "ea": v["designation"], "ea_num": ea[0] if ea else "",
            "id_text": pid,
            "src": sender["actor_id"], "dst": addressee["actor_id"],
            "src_tier": sender["tier"], "dst_tier": addressee["tier"],
            "named_pharaoh": (sender["named_pharaoh"] or addressee["named_pharaoh"]),
            "src_confidence": s_conf, "dst_confidence": a_conf,
            "has_text": pid in pfiles,
            "provenience": v.get("provenience", ""),
        })

    DERIVED.mkdir(parents=True, exist_ok=True)
    with (DERIVED / "nodes.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(next(iter(nodes.values())).keys()),
                           lineterminator="\n")
        w.writeheader()
        w.writerows(sorted(nodes.values(), key=lambda n: -(n["n_sent"] + n["n_received"])))
    with (DERIVED / "edges_corr.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(edges[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(edges)

    # Summary
    from collections import Counter
    tiers = Counter(n["tier"] for n in nodes.values())
    confs = Counter((e["src_confidence"], e["dst_confidence"]) for e in edges)
    both_certain = sum(c for (a, b), c in confs.items() if a == b == "certain")
    print(f"letters (genre=letter): {n_letters}")
    print(f"edges written: {len(edges)}  "
          f"(dropped: {n_no_sender} no-sender, {n_no_addressee} no-addressee, overlapping)")
    print(f"nodes: {len(nodes)}  by tier: {dict(tiers)}")
    print(f"edges with both endpoints 'certain': {both_certain}")
    conf_flat = Counter(c for e in edges for c in (e["src_confidence"], e["dst_confidence"]))
    print(f"endpoint confidence counts: {dict(conf_flat)}")
    print("\ntop 10 actors by letters sent:")
    for n in sorted(nodes.values(), key=lambda n: -n["n_sent"])[:10]:
        print(f"  {n['n_sent']:3d}  {n['display']}  ({n['tier']}, {n['polity'] or '?'})")


if __name__ == "__main__":
    main()
