# Conflict/Alliance Coding Schema (RQ4)

Signed, directed person-to-person edges hand-coded from Moran (1992)
translations. One row per (letter, src, dst, type) in
`registry/conflict_edges.csv`.

## Edge types

| type | sign | rule |
|---|---|---|
| `accuse` | − | src, in a letter src sent, charges dst with hostile action (seizure, killing, incitement, treason, obstruction, slander). Includes reported proxy acts ("his men took…"). |
| `ally` | + | src states dst fought alongside/aided src, or src acts jointly with dst. Mutual aid coded as two directed rows. |

## Exclusions

- Self-defense/loyalty protestations (no target) are not edges.
- Accusations against collectives code against the collective node
  (`sons-of-labaya`, `sons-of-abdiasirta`, `apiru`) — analyzed with and
  without collectives per PLAN.md §3.2.
- Gods, unnamed "enemies", and generic "traitors" are not coded.
- The pharaoh as mere recipient of the complaint is not an edge.

## Provenance and reliability

- `evidence_quote` carries the Moran wording (OCR; brackets simplified).
- `coder` = annotator id; this file starts as a single-coder pass
  (claude/moran-pass1). PLAN.md §7 requires a second independent pass and
  Cohen's κ before the signed network enters the base analysis; until
  then results are labeled provisional.
- `tranche` 1 covers the five classic theatres: Amurru (Rib-Hadda,
  Ili-rapih vs ʿAbdi-Aširta/Aziru + sons), Shechem-south (Biridiya/
  ʿAbdi-Heba/Šuwardata vs Labaya, Milkilu, Tagi + sons), the EA 366
  rescue coalition, Tyre-Sidon (Abi-Milku vs Zimreddi), and the
  Damascus-Qadesh axis (Biryawaza vs Etakkama et al.). Remaining
  dossiers (Rib-Hadda's full run EA 68-138, Jerusalem EA 285-290
  complete, Gezer EA 268-271, minor northern letters) are tranche 2.
