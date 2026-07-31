"""Build the mention/co-occurrence network (Phase 3, PLAN.md §3.1 network 2).

For every letter with lemmatized text, collect the *persons* appearing in it:
the sender (from edges_corr.csv) plus every PN/RN lemma in the text body.
Pharaonic throne names (Naphuriya etc.) resolve to the PHARAOH node. Gods
(DN) and places (GN/SN) are excluded — this is a person-to-person layer.

Outputs:
    data/derived/letter_persons.csv  letter -> resolved person list (audit trail)
    data/derived/edges_mention.csv   co-occurrence pairs, weight = n letters
    data/derived/mention_actors.csv  person nodes with letter counts

Caveats recorded per row: OR-ambiguous lemmas take the first alternative and
set ambiguous=1; broken names (x-) are dropped.
"""

import csv
import itertools
from collections import Counter, defaultdict

from oracc_lib import DERIVED, ROOT, corpus_files, fold, load_catalogue, words

PHARAOH_THRONE_NAMES = {"naphuriya", "naphururiya", "naphurureya",
                        "nimmuriya", "mimmuriya", "nibmuriya", "nibmuareya",
                        "nimmureya", "mimmureya", "huriya"}

ALIASES = {}
with (ROOT / "registry" / "canonical_registry.csv").open() as fh:
    for row in csv.DictReader(fh):
        ALIASES[row["folded_variant"]] = row["folded_canonical"]


def resolve(cf_label):
    """PN/RN citation form -> (actor_id, ambiguous) or (None, _) if unusable."""
    ambiguous = "OR" in cf_label
    label = cf_label.split("OR")[0] if ambiguous else cf_label
    f = fold(label)
    if not f or f.startswith("x") or "-x" in label.lower():
        return None, ambiguous
    if f in PHARAOH_THRONE_NAMES:
        return "pharaoh", ambiguous
    return ALIASES.get(f, f), ambiguous


def main():
    cat = load_catalogue()["members"]
    pfiles = corpus_files()

    sender_of = {}
    with (DERIVED / "edges_corr.csv").open() as fh:
        for r in csv.DictReader(fh):
            sender_of[r["id_text"]] = r["src"]

    letter_rows = []
    cooccur = Counter()
    actor_letters = defaultdict(set)
    display_of = {}

    # Hand-coded person lists for the unlemmatized Great Powers letters
    # (registry/ea1_44_mentions.csv, coded from Moran 1992).
    handcoded = {}
    with (ROOT / "registry" / "ea1_44_mentions.csv").open() as fh:
        for r in csv.DictReader(fh):
            handcoded[r["designation"]] = [p for p in r["persons"].split(";") if p]

    for pid, v in sorted(cat.items(), key=lambda kv: kv[1]["designation"]):
        if v.get("genre") != "letter":
            continue
        if pid not in pfiles:
            group_hand = handcoded.get(v["designation"])
            if not group_hand:
                continue
            group = sorted({ALIASES.get(p, p) for p in group_hand})
            letter_rows.append({
                "id_text": pid, "designation": v["designation"],
                "sender": sender_of.get(pid, ""), "n_persons": len(group),
                "n_ambiguous_tokens": 0, "persons": ";".join(group),
                "source": "moran-handcoded",
            })
            for actor in group:
                actor_letters[actor].add(v["designation"])
                display_of.setdefault(actor, actor)
            for a, b in itertools.combinations(group, 2):
                cooccur[(a, b)] += 1
            continue
        persons = {}
        n_ambig = 0
        for w in words(pid):
            f = w.get("f", {})
            if f.get("pos") not in ("PN", "RN"):
                continue
            actor, ambiguous = resolve(f.get("cf", ""))
            if actor is None:
                continue
            n_ambig += ambiguous
            persons[actor] = persons.get(actor, 0) + 1
            display_of.setdefault(actor, f.get("cf", "").split("OR")[0])
        sender = sender_of.get(pid, "")
        if sender and sender != "pharaoh":
            persons.setdefault(sender, 0)
            display_of.setdefault(sender, sender)
        # PHARAOH participates only when actually named (throne name), else
        # the ever-present addressee-by-title would join every clique and
        # mechanically dominate the mention layer.
        group = sorted(persons)
        letter_rows.append({
            "id_text": pid, "designation": v["designation"],
            "sender": sender, "n_persons": len(group),
            "n_ambiguous_tokens": n_ambig,
            "persons": ";".join(group),
            "source": "oracc-lemmas",
        })
        for actor in group:
            actor_letters[actor].add(v["designation"])
        for a, b in itertools.combinations(group, 2):
            cooccur[(a, b)] += 1

    with (DERIVED / "letter_persons.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(letter_rows[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(letter_rows)

    with (DERIVED / "edges_mention.csv").open("w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["actor_i", "actor_j", "weight"])
        for (a, b), c in sorted(cooccur.items(), key=lambda kv: -kv[1]):
            w.writerow([a, b, c])

    with (DERIVED / "mention_actors.csv").open("w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["actor_id", "display", "n_letters"])
        for a, ls in sorted(actor_letters.items(), key=lambda kv: -len(kv[1])):
            w.writerow([a, display_of.get(a, a), len(ls)])

    print(f"letters processed: {len(letter_rows)}")
    print(f"distinct persons: {len(actor_letters)}")
    print(f"co-occurrence dyads: {len(cooccur)} "
          f"(total pair-observations: {sum(cooccur.values())})")
    print("\nmost-mentioned persons (letters appearing in):")
    for a, ls in sorted(actor_letters.items(), key=lambda kv: -len(kv[1]))[:12]:
        print(f"  {len(ls):3d}  {display_of.get(a, a)}")


if __name__ == "__main__":
    main()
