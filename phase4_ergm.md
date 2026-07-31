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

