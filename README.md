# ussira-pitati

> *uššira piṭāti* — "send the archers!" — Rib-Hadda of Byblos, passim.

A rigorous, reproducible social network analysis of the Amarna letters, built on
the Oracc `aemw/amarna` lemmatized corpus. The aim is to upgrade the descriptive
network studies of Cline & Cline (2015) with explicit null models, inferential
network models (ERGM / latent-space / SBM / QAP), and — centrally — modeling of
the archive-survival bias: the corpus is an ego-network of Egypt, excavated in
Egypt, and centrality within it measures salience-to-Egypt rather than raw
historical importance.

See [PLAN.md](PLAN.md) for the full project plan: research questions, data
sources, network-construction decisions, statistical methodology, work plan,
and publication strategy.

## Status

Phase 0 complete — see [coverage_report.md](coverage_report.md), which includes
two significant corrections to PLAN.md §2.1: the raw `catalogue.json` *does*
carry structured `ancient_author` (sender) and `recipient` fields, and 42/44
Great Powers letters (EA 1–44) already have both — so the header parser and
the Moran/Rainey hand-coding both shrink to validation tasks.

Environment: Python via `uv` (`uv sync`; networkx, igraph, pandas). Deferred
until Phase 4: R (`statnet`/`ergm`/`latentnet`/`Bergm` — no R installed on this
machine yet) and `graph-tool` (conda-forge only). Corpus lives in `data/raw/`
(gitignored): `curl -sLo data/raw/aemw-amarna.zip
http://oracc.museum.upenn.edu/json/aemw-amarna.zip && unzip -d data/raw
data/raw/aemw-amarna.zip`.

## Data

- Primary corpus: [Oracc Amarna Letters](http://oracc.museum.upenn.edu/aemw/amarna/)
  (Lauinger & Yoder, CC-BY-SA) via the `aemw-amarna.zip` bulk JSON download.
- Derived network tables produced here will be licensed and released separately,
  with the CC-BY-SA corpus text never redistributed wholesale.
