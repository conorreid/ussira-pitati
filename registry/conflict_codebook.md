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
- `tranche` 1 covers the five classic theatres; tranche 2 completes a
  keyword-driven sweep of the full Moran corpus (hostile-language filter,
  every flagged letter read): the remaining Rib-Hadda run, Jerusalem
  EA 286/290, the Hasi dossier (EA 185-186), Bayadi (EA 238), the Hatti
  front report (EA 170), and the Mitanni regicide (EA 17). Letters whose
  hostile language has only unnamed antecedents (e.g. EA 102, 119, 161,
  252, 281) yield no edges by rule, not by omission; EA 179's sender is
  unresolvable. Coverage is now corpus-wide at the level of the keyword
  filter; a second independent coding pass remains required.
