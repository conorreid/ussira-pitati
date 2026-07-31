## QAP / permutation tests — the RQ5 geography contrast

Located actors: 51 (via registry/polity_coords.csv). Seed 4711, 2000 permutations.

| layer | n actors | statistic | observed | p |
|---|---|---|---|---|
| mention co-occurrence | 41 | point-biserial r(tie, km) | -0.123 | 0.001 (P(r_null <= obs)) |
| conflict (tranches 1-2, provisional) | 12 | point-biserial r(tie, km) | -0.265 | 0.006 (P(r_null <= obs)) |
| correspondence: letters to pharaoh vs km to Akhetaten (vassals) | 35 | Spearman rho | -0.319 | 0.061 (two-sided) |
| ... same, without Rib-Hadda | 34 | Spearman rho | -0.387 | 0.028 (two-sided) |

Prediction: negative and significant in mention/conflict; null in
correspondence. A negative r with small P(r_null <= obs) supports
distance decay.
