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

Phase 0 — environment and data audit. Nothing to see yet.

## Data

- Primary corpus: [Oracc Amarna Letters](http://oracc.museum.upenn.edu/aemw/amarna/)
  (Lauinger & Yoder, CC-BY-SA) via the `aemw-amarna.zip` bulk JSON download.
- Derived network tables produced here will be licensed and released separately,
  with the CC-BY-SA corpus text never redistributed wholesale.
