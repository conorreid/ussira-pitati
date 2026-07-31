## ERGM — correspondence network (directed, binarized dyads)

| term | est | se | p |
|---|---|---|---|
| edges | -2.576 | 0.683 | 0.0002 |
| mutual | 3.783 | 0.801 | 0.0000 |
| nodeifactor.tier.great_power | -4.204 | 0.770 | 0.0000 |
| nodeifactor.tier.vassal | -4.074 | 0.532 | 0.0000 |
| nodeofactor.tier.great_power | 0.124 | 0.726 | 0.8640 |
| nodeofactor.tier.vassal | 0.111 | 0.681 | 0.8700 |
| nodematch.tier | -2.207 | 0.641 | 0.0006 |

AIC: 884.2. Interpretation guide: `mutual` tests RQ3
reciprocity; `nodematch.tier` tests RQ2 tier homophily (expected
strongly NEGATIVE here: correspondence crosses tiers by design -
everyone writes to Egypt, no one writes within-tier).

## Latent-space cluster model (ergmm) — mention network

Actors modeled: 117 (appearing in >=2 letters, capped at 120).

Cluster x tier cross-tab (correspondent tiers where known):

```
       tier
cluster egypt great_power unknown vassal
      1     2           0      17     20
      2     0           0      11      5
      3     4           3      33     22
```

BIC (overall): 2553.9


## ERGM goodness-of-fit (gof) summary

Full tables in `phase4_gof.txt`. Model-statistic GOF p-values
(observed vs simulated; large p = well captured):

```
                             obs min   mean max MC p-value
edges                        117  87 115.93 145       0.98
mutual                         6   1   5.71  12       1.00
nodeifactor.tier.great_power   2   0   1.73   5       1.00
nodeifactor.tier.vassal        9   2   9.03  17       0.98
nodeofactor.tier.great_power  13   5  13.59  22       0.98
nodeofactor.tier.vassal       95  74  93.68 123       0.92
nodematch.tier                 3   0   2.84   9       1.00
```

