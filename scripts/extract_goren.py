"""Extract the per-tablet petrographic catalogue from the OCR'd Goren,
Finkelstein & Na'aman 2004 (data/raw/goren2004/page*.txt, not committed).

Writes registry/goren2004_provenance.csv: one row per tablet with the
book's chapter/section (the provenance determination), the raw geological
interpretation text, and the cross-reference line. This automated pass is
transcription key 1; a human spot-check is key 2 (PLAN.md §2.3).

OCR quirks handled: roman numerals rendered with lowercase L ('Ill.'),
chapter headers as bare 'CHAPTER n' lines with the title following.
"""

import csv
import re
from pathlib import Path

from oracc_lib import ROOT

RAW = ROOT / "data" / "raw" / "goren2004"
OUT = ROOT / "registry" / "goren2004_provenance.csv"


def main():
    pages = sorted(RAW.glob("page*.txt"))
    full = "\n".join(f"\n@@PAGE {p.stem}@@\n" + p.read_text() for p in pages)

    chap_pat = re.compile(r"^CHAPTER (\d+)\n+([A-Z][^\n]{3,70})?", re.M)
    # OCR renders I/l/1 interchangeably in roman numerals ('Ill. BABYLONIA').
    sec_pat = re.compile(r"^([IVXl1]{1,5}\. [A-Z][^\n]{2,55})$", re.M)
    ea_pat = re.compile(r"^EA (\d{1,3}[a-z]?) \(([^)]{2,40})\)[,.]? *(.*)$", re.M)

    marks = [(m.start(), "chap", f"Ch.{m.group(1)} {(m.group(2) or '').strip()}")
             for m in chap_pat.finditer(full)]
    marks += [(m.start(), "sec", m.group(1).strip()) for m in sec_pat.finditer(full)]
    marks += [(m.start(), "ea", m) for m in ea_pat.finditer(full)]
    marks.sort(key=lambda t: t[0])

    rows, cur_chapter, cur_section = [], "", ""
    for i, (pos, kind, val) in enumerate(marks):
        if kind == "chap":
            cur_chapter, cur_section = val, ""
            continue
        if kind == "sec":
            cur_section = re.sub(r"^[IVXl1]+\.", lambda m: m.group(0).upper().replace("L", "I"), val)
            continue
        m = val
        nxt = next((marks[j][0] for j in range(i + 1, len(marks)) if marks[j][1] == "ea"),
                   m.end() + 4500)
        seg = full[m.end():min(nxt, m.end() + 4500)]
        if not re.search(r"Sampling method|Matrix:|Geological interpretation"
                         r"|Interpretation and conclusion", seg[:2800]):
            continue  # table-of-contents line, not a catalogue entry
        geo = re.search(r"(?:Geological interpretation|Interpretation and conclusions?):?\s*"
                        r"(.{0,400}?)(?=\n\n|Reference:|@@PAGE|Petrograph)", seg, re.S)
        ref = re.search(r"Reference:?\s*(.{0,120}?)(?:\n|$)", seg)
        suffix = m.group(1)[-1] if m.group(1)[-1].isalpha() else ""
        rows.append({
            "ea": f"EA {int(re.sub('[a-z]', '', m.group(1))):03d}{suffix}",
            "museum_no": m.group(2).strip(),
            "header_rest": m.group(3).strip()[:80],
            "chapter": cur_chapter, "section": cur_section,
            "interpretation_raw": (geo.group(1).replace("\n", " ").strip() if geo else ""),
            "reference": (ref.group(1).strip() if ref else ""),
        })

    seen, out = set(), []
    for r in rows:
        if r["ea"] not in seen:
            seen.add(r["ea"])
            out.append(r)
    out.sort(key=lambda r: r["ea"])
    with OUT.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(out)
    print(f"{len(out)} tablets -> {OUT}")


if __name__ == "__main__":
    main()
