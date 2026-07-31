## Bayesian ERGM (Bergm) - posterior quantiles

Same specification as the MCMLE fit; 30k main iterations, seed 4711.

| term | 2.5% | median | 97.5% |
|---|---|---|---|
| edges | -4.191 | -2.555 | -1.122 |
| mutual | 2.337 | 4.048 | 6.237 |
| nodeifactor.great_power | -6.688 | -4.588 | -3.199 |
| nodeifactor.vassal | -5.609 | -4.298 | -3.224 |
| nodeofactor.great_power | -1.464 | 0.083 | 1.852 |
| nodeofactor.vassal | -1.336 | 0.105 | 1.736 |
| nodematch.tier | -3.988 | -2.259 | -0.826 |

Read: RQ3 (mutual) and RQ2 (nodematch.tier) hold if their 95% credible
intervals exclude zero.

