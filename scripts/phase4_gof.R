# Goodness-of-fit diagnostics for the Phase 4 correspondence ERGM.
# Appends a GOF section to phase4_ergm.md. Run after phase4_models.R.

suppressMessages({
  library(network)
  library(ergm)
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
fit <- ergm(net ~ edges + mutual + nodeifactor("tier") + nodeofactor("tier")
            + nodematch("tier"), control = control.ergm(seed = 4711))
g <- gof(fit)
sink("phase4_gof.txt")
print(g)
sink()

# Compact markdown summary: p-values for observed stats under the fitted model
lines <- c("", "## ERGM goodness-of-fit (gof) summary", "",
  "Full tables in `phase4_gof.txt`. Model-statistic GOF p-values",
  "(observed vs simulated; large p = well captured):", "", "```")
ms <- g$summary.model
lines <- c(lines, capture.output(print(round(ms, 3))), "```", "")
frag <- readLines("phase4_ergm.md")
writeLines(c(frag, lines), "phase4_ergm.md")
cat("GOF appended to phase4_ergm.md\n")
