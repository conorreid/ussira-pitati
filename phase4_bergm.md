## Bayesian ERGM (Bergm) - posterior quantiles

Same specification as the MCMLE fit; 30k main iterations, seed 4711.

| term | 2.5% | median | 97.5% |
|---|---|---|---|
| edges | -4.236 | -2.599 | -1.156 |
| mutual | 2.364 | 4.066 | 6.253 |
| nodeifactor.great_power | -6.581 | -4.534 | -3.127 |
| nodeifactor.vassal | -5.613 | -4.278 | -3.190 |
| nodeofactor.great_power | -1.461 | 0.149 | 1.918 |
| nodeofactor.vassal | -1.311 | 0.145 | 1.797 |
| nodematch.tier | -3.944 | -2.234 | -0.825 |

Read: RQ3 (mutual) and RQ2 (nodematch.tier) hold if their 95% credible
intervals exclude zero.

