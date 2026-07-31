"""Parse sender/addressee from the opening address formula of each letter and
validate against the catalogue's structured ancient_author/recipient fields.

Two formula orders occur:
    A (vassal-standard):  ana ADDRESSEE qibīma | umma SENDER ...
    B (Byblos etc.):      SENDER qabû ana ADDRESSEE ...
and either half may be lost to breakage. Slots are delimited by the first
occurrences of `ana`, `umma`, and `qabû`, whichever order they appear in.

Writes data/derived/headers.csv and prints an agreement summary. Catalogue
fields are the reference; residual disagreements are for hand-adjudication
against Moran/Rainey and may include catalogue errors (e.g. EA 62).
"""

import csv
import difflib
import re

from oracc_lib import DERIVED, ROOT, corpus_files, fold, load_catalogue, words

PHARAOH_MARKERS = ("pharaoh", "amenhotep", "akhenaten", "tutankhamun",
                   "neferneferuaten", "smenkhkare")
# Throne names ("Naphuriya" = Nefer-kheperu-re = Akhenaten, etc.) as they
# surface in Oracc citation forms, folded.
PHARAOH_THRONE_NAMES = {"naphuriya", "naphururiya", "naphurureya", "naphuriya",
                        "nimmuriya", "mimmuriya", "nibmuriya", "nibmuareya",
                        "nimmureya", "mimmureya", "huriya"}
EGYPT_GNS = {"misri", "misru", "egypt", "mizri"}

ALIASES = {}
with (ROOT / "registry" / "canonical_registry.csv").open() as fh:
    for row in csv.DictReader(fh):
        ALIASES[row["folded_variant"]] = row["folded_canonical"]


def canon(folded: str) -> str:
    return ALIASES.get(folded, folded)


def cf(w):
    return w.get("f", {}).get("cf", "")


def pos(w):
    return w.get("f", {}).get("pos", "")


def expand_or(label: str):
    """Oracc encodes lemma ambiguity inline: 'HadduORTeššub-nerari'.
    Return plausible full-name alternatives."""
    if "OR" not in label:
        return [label]
    parts = label.split("OR")
    first, last = parts[0], parts[-1]
    alts = {first, last}
    if "-" in last:
        alts.add(first + last[last.index("-"):])
    if "-" in first:
        alts.add(first[: first.rindex("-") + 1] + last)
    return list(alts)


def describe_slot(slot):
    """Actor label for an address slot.
    kind: 'name' | 'pharaoh' | 'king-of-GN' | 'collective' | 'none'."""
    names = [cf(w) for w in slot if pos(w) in ("PN", "RN")]
    gns = [cf(w) for w in slot if pos(w) in ("GN", "SN")]
    has_king = any(cf(w) == "šarru" for w in slot)
    if names:
        if fold(names[0]) in PHARAOH_THRONE_NAMES:
            return names[0], "pharaoh"
        return names[0], "name"
    if has_king and gns and fold(gns[0]) not in EGYPT_GNS:
        return f"king of {gns[0]}", "king-of-GN"
    if has_king:
        return "PHARAOH", "pharaoh"
    if gns:
        return gns[0], "collective"
    return "", "none"


def parse_header(word_nodes, scan_limit=40):
    """Extract (sender, addressee) slots from the opening formula."""
    head = word_nodes[:scan_limit]

    def first(pred):
        return next((i for i, w in enumerate(head) if pred(w)), None)

    i_ana = first(lambda w: cf(w) == "ana")
    i_umma = first(lambda w: cf(w) == "umma")
    i_qibi = first(lambda w: cf(w) == "qabû")
    marks = sorted(i for i in (i_ana, i_umma, i_qibi) if i is not None)

    def slot_after(i, span=8):
        """Relevant words after position i, stopping at the next formula
        marker, the first verb, or span words — whichever comes first."""
        stop = min([m for m in marks if m > i] + [i + 1 + span, len(head)])
        out = []
        for w in head[i + 1: stop]:
            if pos(w) == "V":
                break
            if pos(w) in ("PN", "RN", "GN", "SN") or cf(w) == "šarru":
                out.append(w)
        return out

    # Positional gates: a real address formula sits at the tablet's head.
    # Late markers mean the opening is lost and we'd be grabbing body text
    # (continuation tablets like EA 245, broken openings like EA 101/131).
    addressee = (describe_slot(slot_after(i_ana))
                 if i_ana is not None and i_ana <= 5 else ("", "none"))

    if i_umma is not None and i_umma <= 30:
        sender = describe_slot(slot_after(i_umma, span=6))
    else:
        # Formula B ("SENDER qabû ana ..."): the sender PN opens the tablet,
        # with qabû immediately after it.
        lead = [(i, w) for i, w in enumerate(head[:3]) if pos(w) in ("PN", "RN")]
        if lead and i_qibi is not None and i_qibi <= lead[0][0] + 4:
            sender = describe_slot([w for _, w in lead])
        else:
            sender = ("", "none")
    return sender, addressee


def catalogue_name(raw):
    """First name-chunk of a catalogue value: 'Milki-ilu, mayor of Gazru' ->
    'Milki-ilu'. Strips editorial brackets and regnal numerals."""
    s = (raw or "").strip().strip("[]")
    for sep in (",", " of ", " the "):
        if sep in s:
            s = s.split(sep)[0]
    return re.sub(r"\s+[IVX]+$", "", s.strip())


def is_pharaoh(raw):
    r = (raw or "").lower()
    return any(m in r for m in PHARAOH_MARKERS)


def agree(parsed_label, parsed_kind, raw_catalogue):
    """True/False agreement, or None when not comparable (broken name,
    missing field, unparsed slot)."""
    raw = (raw_catalogue or "").strip()
    if not raw or raw.strip("[]").strip() in ("missing", "") or "..." in raw:
        return None
    if parsed_kind == "none" or "x" in fold(parsed_label)[:1] or "-x" in parsed_label.lower():
        return None
    if parsed_kind == "pharaoh":
        return is_pharaoh(raw)
    if parsed_kind in ("king-of-GN", "collective"):
        gn = canon(fold(parsed_label.removeprefix("king of ")))
        return bool(gn) and gn in fold(raw)
    target = canon(fold(catalogue_name(raw)))
    if not target:
        return None
    for alt in expand_or(parsed_label):
        a = canon(fold(alt))
        if a and (a == target or difflib.SequenceMatcher(None, a, target).ratio() >= 0.75):
            return True
    return False


def main():
    cat = load_catalogue()["members"]
    pfiles = corpus_files()
    DERIVED.mkdir(parents=True, exist_ok=True)

    rows = []
    for pid, v in sorted(cat.items(), key=lambda kv: kv[1]["designation"]):
        if v.get("genre") != "letter" or pid not in pfiles:
            continue
        (s_label, s_kind), (a_label, a_kind) = parse_header(words(pid))
        rows.append({
            "id_text": pid,
            "designation": v["designation"],
            "parsed_sender": s_label,
            "parsed_sender_kind": s_kind,
            "parsed_addressee": a_label,
            "parsed_addressee_kind": a_kind,
            "cat_sender": v.get("ancient_author", ""),
            "cat_recipient": v.get("recipient", ""),
            "sender_agree": agree(s_label, s_kind, v.get("ancient_author")),
            "addressee_agree": agree(a_label, a_kind, v.get("recipient")),
        })

    out = DERIVED / "headers.csv"
    with out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)

    def summarize(key):
        vals = [r[f"{key}_agree"] for r in rows]
        n_cmp = sum(1 for x in vals if x is not None)
        n_ok = sum(1 for x in vals if x is True)
        n_na = sum(1 for x in vals if x is None)
        print(f"{key:10s}: {n_ok}/{n_cmp} agree ({100*n_ok/n_cmp:.1f}%), "
              f"{n_na} not comparable (broken header or missing field)")

    print(f"parsed {len(rows)} letters -> {out}")
    summarize("sender")
    summarize("addressee")

    print("\nDisagreements (for hand-adjudication vs Moran/Rainey):")
    for r in rows:
        for key, cat_key in (("sender", "cat_sender"), ("addressee", "cat_recipient")):
            if r[f"{key}_agree"] is False:
                print(f"  {r['designation']:8s} {key}: "
                      f"parsed={r[f'parsed_{key}']!r} vs catalogue={r[cat_key]!r}")


if __name__ == "__main__":
    main()
