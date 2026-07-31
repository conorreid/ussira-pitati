# Bayesian ERGM (Bergm) on the correspondence network - posterior
# uncertainty for the Phase 4 point estimates. Writes phase4_bergm.md.

suppressMessages({
  library(network)
  library(ergm)
  library(Bergm)
})
set.seed(4711)

nodes <- read.csv("data/derived/nodes.csv", stringsAsFactors = FALSE)
edges <- read.csv("data/derived/edges_corr.csv", stringsAsFactors = FALSE)
actors <- nodes$actor_id
net <- network.initialize(length(actors), directed = TRUE)
network.vertex.names(net) <- actors
net %v% "tier" <- nodes$tier[match(actors, nodes$actor_id)]
for (i in seq_len(nrow(edges))) {
  s <- match(edges$src[i], actors); d <- match(edges$dst[i], actors)
  if (!is.na(s) && !is.na(d) && s != d) net[s, d] <- 1
}

fit <- bergm(net ~ edges + mutual + nodeifactor("tier") + nodeofactor("tier")
             + nodematch("tier"),
             burn.in = 2000, main.iters = 30000, aux.iters = 3000)

s <- summary(fit)
post <- fit$Theta
qs <- t(apply(post, 2, quantile, probs = c(0.025, 0.5, 0.975)))
terms <- c("edges", "mutual", "nodeifactor.great_power", "nodeifactor.vassal",
           "nodeofactor.great_power", "nodeofactor.vassal", "nodematch.tier")

lines <- c("## Bayesian ERGM (Bergm) - posterior quantiles", "",
  "Same specification as the MCMLE fit; 30k main iterations, seed 4711.", "",
  "| term | 2.5% | median | 97.5% |", "|---|---|---|---|")
for (i in seq_len(nrow(qs))) {
  lines <- c(lines, sprintf("| %s | %.3f | %.3f | %.3f |",
                            terms[min(i, length(terms))],
                            qs[i, 1], qs[i, 2], qs[i, 3]))
}
lines <- c(lines, "",
  "Read: RQ3 (mutual) and RQ2 (nodematch.tier) hold if their 95% credible",
  "intervals exclude zero.", "")
writeLines(lines, "phase4_bergm.md")
cat("wrote phase4_bergm.md\n")
