# Phase 4 inferential models (RQ2/RQ3): ERGM on the correspondence
# network, latent-cluster model (ergmm) on the mention network.
# Writes phase4_ergm.md. Run from repo root: Rscript scripts/phase4_models.R

suppressMessages({
  library(network)
  library(ergm)
  library(latentnet)
})
set.seed(4711)

nodes <- read.csv("data/derived/nodes.csv", stringsAsFactors = FALSE)
edges <- read.csv("data/derived/edges_corr.csv", stringsAsFactors = FALSE)

## ---- Correspondence ERGM (directed) ----
actors <- nodes$actor_id
net <- network.initialize(length(actors), directed = TRUE)
network.vertex.names(net) <- actors
tier <- nodes$tier[match(actors, nodes$actor_id)]
net %v% "tier" <- tier
for (i in seq_len(nrow(edges))) {
  s <- match(edges$src[i], actors); d <- match(edges$dst[i], actors)
  if (!is.na(s) && !is.na(d) && s != d) net[s, d] <- 1
}

lines <- c("## ERGM — correspondence network (directed, binarized dyads)", "")
fit <- tryCatch(
  ergm(net ~ edges + mutual + nodeifactor("tier") + nodeofactor("tier")
       + nodematch("tier"),
       control = control.ergm(seed = 4711)),
  error = function(e) e)
if (inherits(fit, "error")) {
  lines <- c(lines, paste("ERGM failed:", conditionMessage(fit)),
             "Falling back per pre-registered plan (QAP + latent space).")
} else {
  s <- summary(fit)
  co <- coef(s)
  lines <- c(lines, "| term | est | se | p |", "|---|---|---|---|")
  for (r in rownames(co)) {
    lines <- c(lines, sprintf("| %s | %.3f | %.3f | %.4f |",
                              r, co[r, 1], co[r, 2], co[r, ncol(co)]))
  }
  lines <- c(lines, "",
    sprintf("AIC: %.1f. Interpretation guide: `mutual` tests RQ3", AIC(fit)),
    "reciprocity; `nodematch.tier` tests RQ2 tier homophily (expected",
    "strongly NEGATIVE here: correspondence crosses tiers by design -",
    "everyone writes to Egypt, no one writes within-tier).", "")
}

## ---- Latent cluster model on the mention network ----
ma <- read.csv("data/derived/mention_actors.csv", stringsAsFactors = FALSE)
me <- read.csv("data/derived/edges_mention.csv", stringsAsFactors = FALSE)
# largest-component actors with a known tier from nodes.csv
tier_of <- setNames(nodes$tier, nodes$actor_id)
keep <- ma$actor_id[ma$n_letters >= 2]   # trim singletons for tractability
keep <- keep[1:min(length(keep), 120)]   # cap for runtime
mnet <- network.initialize(length(keep), directed = FALSE)
network.vertex.names(mnet) <- keep
for (i in seq_len(nrow(me))) {
  s <- match(me$actor_i[i], keep); d <- match(me$actor_j[i], keep)
  if (!is.na(s) && !is.na(d) && s != d) mnet[s, d] <- 1
}
lines <- c(lines, "## Latent-space cluster model (ergmm) — mention network", "")
mfit <- tryCatch(
  ergmm(mnet ~ euclidean(d = 2, G = 3),
        control = ergmm.control(sample.size = 2000, burnin = 10000)),
  error = function(e) e)
if (inherits(mfit, "error")) {
  lines <- c(lines, paste("ergmm failed:", conditionMessage(mfit)))
} else {
  cl <- mfit$mkl$Z.K
  tiers_known <- tier_of[keep]
  tab <- table(cluster = cl, tier = ifelse(is.na(tiers_known) | tiers_known == "",
                                           "unknown", tiers_known))
  lines <- c(lines, sprintf("Actors modeled: %d (appearing in >=2 letters, capped at 120).",
                            length(keep)),
             "", "Cluster x tier cross-tab (correspondent tiers where known):", "",
             "```", capture.output(print(tab)), "```", "",
             sprintf("BIC (overall): %.1f", summary(mfit)$bic$overall), "")
}

writeLines(lines, "phase4_ergm.md")
cat("wrote phase4_ergm.md\n")
