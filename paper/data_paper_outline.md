# Data paper outline — Journal of Open Humanities Data

**Title (working):** "The Amarna Letters as Data: Actor Registry, Network
Edge Lists, and Provenance Joins from the Oracc Lemmatized Corpus"

## Dataset summary

One versioned bundle (Zenodo DOI on release):

| file | rows | description |
|---|---|---|
| `data/derived/nodes.csv` | 111 | correspondence actors: id, display, polity, tier, letter counts |
| `data/derived/edges_corr.csv` | 302 | one row per letter: sender, addressee, per-endpoint confidence |
| `data/derived/edges_mention.csv` | 737 | person co-occurrence dyads, letter-count weights |
| `data/derived/letter_persons.csv` | 343 | per-letter resolved person lists + source (lemmas vs hand-coded) |
| `data/derived/letter_provenance.csv` | 292 | Goren 2004 petrographic determination x catalogue provenience |
| `registry/canonical_registry.csv` | 15 | hand-curated entity aliases with justifications |
| `registry/adjudication_queue.csv` | 18 | header disputes adjudicated vs Moran, with quotes |
| `registry/conflict_edges.csv` | 34 | signed conflict/alliance edges (tranche 1) with quotes |
| `registry/ea1_44_mentions.csv` | 44 | Great Powers letters person coding from Moran |
| `registry/polity_coords.csv` | 55 | polity -> Pleiades id + coordinates, match provenance |
| `registry/goren2004_provenance.csv` | 292 | per-tablet petrographic catalogue transcription |

## Reuse cases

- Any SNA/statistical reanalysis without re-doing entity resolution
- Prosopography: alias registry + adjudications as philological data
- Geography: letter-level provenance with coordinates
- Teaching: a compact, real, fully documented historical network

## Method summary (2-3 pp)

Pipeline diagram (`run_all.sh` stages); validation figures: 96% header
agreement, 87% petrography-catalogue agreement, adjudication outcomes;
known limitations (single-coder layers flagged in-data).

## Licensing

Code MIT; derived tables CC-BY 4.0; no Oracc corpus text redistributed
(CC-BY-SA respected by derivation, not reproduction); quotations from
Moran/Goren within fair use, page-referenced.
