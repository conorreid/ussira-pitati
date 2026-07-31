## ERGM — correspondence network (directed, binarized dyads)

| term | est | se | p |
|---|---|---|---|
| edges | -2.538 | 0.697 | 0.0003 |
| mutual | 3.768 | 0.833 | 0.0000 |
| nodeifactor.tier.great_power | -4.138 | 0.772 | 0.0000 |
| nodeifactor.tier.vassal | -4.077 | 0.503 | 0.0000 |
| nodeofactor.tier.great_power | 0.069 | 0.756 | 0.9272 |
| nodeofactor.tier.vassal | 0.059 | 0.696 | 0.9329 |
| nodematch.tier | -2.267 | 0.637 | 0.0004 |

AIC: 883.5. Interpretation guide: `mutual` tests RQ3
reciprocity; `nodematch.tier` tests RQ2 tier homophily (expected
strongly NEGATIVE here: correspondence crosses tiers by design -
everyone writes to Egypt, no one writes within-tier).

## Latent-space cluster model (ergmm) — mention network

Actors modeled: 117 (appearing in >=2 letters, capped at 120).

Cluster x tier cross-tab (correspondent tiers where known):

```
       tier
cluster egypt great_power unknown vassal
      1     0           1      14     12
      2     4           0      26     21
      3     2           2      21     14
```

BIC (overall): 2742.4


## ERGM goodness-of-fit (gof) summary

Full tables in `phase4_gof.txt`. Model-statistic GOF p-values
(observed vs simulated; large p = well captured):

```
                             obs min   mean max MC p-value
edges                        117  91 117.41 148       0.94
mutual                         6   0   6.09  13       1.00
nodeifactor.tier.great_power   2   0   2.16   7       1.00
nodeifactor.tier.vassal        9   4   9.13  17       1.00
nodeofactor.tier.great_power  12   5  12.10  22       1.00
nodeofactor.tier.vassal       96  77  96.51 119       1.00
nodematch.tier                 3   0   2.72   9       1.00
```

