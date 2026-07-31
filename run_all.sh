#!/bin/sh
# Full pipeline, raw data -> reports. Requires: uv (Python), Rscript with
# ergm/latentnet installed, and the corpus zips fetched per README (data/raw/
# is not committed). Every stage is seeded; output should be identical
# across runs.
set -e
cd "$(dirname "$0")"

echo "== audit =="       && uv run python scripts/audit_coverage.py
echo "== headers =="     && uv run python scripts/parse_headers.py > /dev/null && echo ok
echo "== network =="     && uv run python scripts/build_network.py
echo "== pleiades =="    && uv run python scripts/join_pleiades.py
echo "== goren =="       && uv run python scripts/extract_goren.py && uv run python scripts/join_goren.py
echo "== mentions =="    && uv run python scripts/build_mentions.py
echo "== phase2 =="      && uv run python scripts/phase2_analysis.py
echo "== phase3 =="      && uv run python scripts/phase3_analysis.py
echo "== conflict =="    && uv run python scripts/conflict_analysis.py
echo "== reliability ==" && uv run python scripts/coding_reliability.py
echo "== phase4 R =="    && Rscript scripts/phase4_models.R
echo "== phase4 GOF ==" && Rscript scripts/phase4_gof.R
echo "== phase4 Bergm ==" && Rscript scripts/phase4_bergm.R
echo "== phase split ==" && uv run python scripts/phase_split.py
echo "== phase4 QAP =="  && uv run python scripts/qap_distance.py
echo "== distance confounds ==" && uv run python scripts/distance_confounds.py > /dev/null && echo ok
echo "== done =="
