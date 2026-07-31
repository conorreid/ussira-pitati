# ussira-pitati

> *uššira piṭāti* — "send the archers!" — Rib-Hadda of Byblos, passim.

A rigorous, reproducible social network analysis of the Amarna letters,
built on the Oracc `aemw/amarna` lemmatized corpus. The project replicates
and decomposes the descriptive network studies of Cline & Cline
(2015)/Cline (2025) with explicit null models, inferential network models
(ERGM / latent-space / QAP), and survival-bias modeling: the corpus is an
ego-network of Egypt, excavated in Egypt, and centrality within it
measures salience-to-Egypt rather than historical importance.

**Headline results** (details in [paper/draft.md](paper/draft.md)):

- The correspondence network contains **zero triangles** — the famous
  "small world" lives entirely in the mention layer.
- Rebuilt at full scale the mention network matches Cline & Cline's object
  (245 vs 246 persons; CC 0.408 vs 0.391) but exceeds a fair bipartite
  null by **~1.6×, not "48.75×"**.
- Rib-Hadda's celebrated brokerage **replicates under their construction
  and dissolves under correction** (pharaoh-node splitting + dossier
  volume); the stable brokers are **Aziru of Amurru** and the Egyptian
  commissioner **Yanḥamu**.
- ERGM: reciprocity +3.77, tier anti-homophily −2.27 (both p < 0.001,
  GOF clean). Distance decays mention ties (QAP p = 0.002) — and,
  contrary to our own prediction, correspondence volume too
  (ρ = −0.50, p = 0.002, vassals only, robust to dropping Rib-Hadda).
- Two Oracc catalogue errors found and adjudicated against Moran (EA 62,
  EA 301), plus EA 7's recipient; 87% petrography-catalogue provenance
  agreement with Goren et al.'s discoveries reproduced machine-readably.

## Reproduce

```sh
# 1. fetch raw data (not committed):
curl -sLo data/raw/aemw-amarna.zip http://oracc.museum.upenn.edu/json/aemw-amarna.zip
unzip -d data/raw data/raw/aemw-amarna.zip
curl -sLo data/raw/pleiades-places-latest.csv.gz https://atlantides.org/downloads/pleiades/dumps/pleiades-places-latest.csv.gz
curl -sLo data/raw/pleiades-names-latest.csv.gz https://atlantides.org/downloads/pleiades/dumps/pleiades-names-latest.csv.gz
gunzip -k data/raw/pleiades-*.gz
# OCR'd Moran (1992) and Goren et al. (2004) page texts belong in
# data/raw/moran1992/ and data/raw/goren2004/ (copyrighted; not
# distributable - see scripts/extract_goren.py headers for expectations).

# 2. environment: uv sync;  R with install.packages(c("network","sna","ergm","latentnet"))

# 3. everything:
./run_all.sh
```

All stages are seeded; reports regenerate byte-identically.

## Layout

- `scripts/` — the pipeline (audit → headers → network → geography →
  mentions → analyses → inference); each file's docstring states its role
- `registry/` — hand-curated, evidence-quoted data: entity aliases,
  Moran adjudications, EA 1–44 mention coding, signed conflict edges +
  codebook, polity coordinates, Goren petrography transcription
- `data/derived/` — machine-built tables (nodes, edge lists, provenance)
- `coverage_report.md`, `phase2_report.md`, `phase3_report.md`,
  `conflict_report.md`, `phase4_report.md` — generated reports
- `paper/` — article draft + data-paper outline
- `PLAN.md` — the original project plan (kept verbatim; §2.1's premise is
  corrected in coverage_report.md)

## Licensing

Code MIT; derived tables CC-BY 4.0 (see LICENSE). Oracc corpus text is
CC-BY-SA (Lauinger & Yoder / Izre'el) and never redistributed here;
Moran/Goren quotations are page-referenced fair use.

## Remaining before submission

- Conflict tranche 2 (remaining dossier letters) + independent second
  coding with Cohen's κ; second-key spot-checks of the adjudication,
  registry, and Goren transcription
- Bergm posterior + early/middle/late phase-split sensitivity
- Rainey (2015) collation pass on the adjudicated cases
- Zenodo deposit + DOI
