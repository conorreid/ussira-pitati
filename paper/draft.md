# The Small World of the Amarna Letters, Revisited: A Reproducible, Bias-Aware Network Analysis

*Working draft v0.1 — target venue: Journal of Historical Network Research.
All numbers regenerate from `run_all.sh` at the repository root; seeds fixed.*

## Abstract

The Amarna letters (c. 1360–1330 BC) are the oldest well-preserved archive
of interstate diplomacy, and the network analysis of Cline & Cline (2015) —
a hand-coded "small world" with clustering ~49× a random graph, brokered
above all by Rib-Hadda of Byblos — has become the canonical quantitative
reading of the corpus. We rebuild the Amarna networks from the Oracc
lemmatized edition with fully reproducible code, hand-coding only what the
digital corpus lacks, and subject every headline claim to appropriate null
models and survival-bias corrections. Three results follow. (1) The
correspondence network contains *zero* triangles: the celebrated small
world lives entirely in the mention layer. Reconstructed at full scale (244
persons; Cline & Cline counted 246), that layer's clustering (0.409 ≈
their 0.391) exceeds a fair bipartite configuration null by a factor of
~1.6 — genuine structure, but far from the "48.75×" figure produced by an
Erdős–Rényi comparison. (2) Rib-Hadda's famous brokerage replicates
exactly under Cline & Cline's construction and dissolves under bias
correction: it depends on splitting the pharaoh's identity across nodes
and on his 60+-letter dossier; volume-equalized, he falls to median rank
15 with zero bootstrap probability of a top-three position, while Aziru of
Amurru and the Egyptian commissioner Yanḥamu emerge as the stable
brokers. (3) Inferential models formalize the tier structure (ERGM:
reciprocity +3.78, tier anti-homophily −2.21, both p < 0.001), and
geography behaves exactly as pre-registered: distance decays mention
and conflict ties but not correspondence with the court — a result we
report with confidence only because an apparent counter-finding
(ρ = −0.50 for correspondence) dissolved under our own audit into
gazetteer mismatches, a tie-handling artifact, and political
composition, an object lesson in the paper's central argument applied
to ourselves. We release the actor
registry, edge lists, provenance joins (including a machine-readable
transcription of Goren, Finkelstein & Na'aman's petrographic
determinations), and all code.

## 1. Introduction

The 382 tablets found at Tell el-Amarna record the diplomatic
correspondence of the Egyptian court under Amenhotep III and Akhenaten
with two tiers of partners: the "Great Powers" (Babylonia, Assyria,
Mittani, Hatti, Arzawa, Alashiya) and the vassal rulers of the Levant.
Cline & Cline (2015) introduced network analysis to this corpus,
hand-coding actors and ties in NodeXL, and reported three memorable
findings: a clustering coefficient of 0.391, "nearly fifty times higher"
than a comparable random network; the minor king Rib-Hadda of Byblos
out-scoring both pharaohs in betweenness centrality; and pharaohs
dominating only two of ten network clusters. E. Cline's *Love, War, and
Diplomacy* (2025) brought this picture — 246 named people, 464
connections — to a broad audience.

These studies are exploratory: no null models, no uncertainty, no
correction for the archive's structure, and hand-coded data that cannot be
audited. The present study asks which of their findings survive
reproducible construction and appropriate inference — and finds that the
answer is a precise decomposition rather than a verdict: each headline
claim is true under one specific set of constructional choices and false
under defensible alternatives. Identifying *which* choice drives *which*
result is, we argue, the useful contribution.

A second contribution is methodological framing. The archive is an
ego-network of Egypt, excavated in Egypt: every correspondence tie
touches the court by construction, and every mention survives because
some letter to Egypt carried it. Centrality measured on such an archive is
*salience to Egypt*, not historical importance. Rather than treating this
as a caveat, we build it into the analysis: the correspondence layer is
analyzed as what it is (a star), the substantive questions are pushed to
the mention and conflict layers, and every centrality claim carries
bootstrap rank intervals and dossier-volume corrections.

## 2. Data

**Corpus.** The Oracc `aemw/amarna` edition (Lauinger & Yoder; catalogue
timestamp 2024-07-05) contains 379 catalogued tablets, of which 347 are
letters and 305 carry lemmatized transliteration (34,346 word tokens,
94.0% lemmatized). The Great Powers letters EA 1–44 and ~30 fragments
have catalogue metadata but no digital text.

**A correction to the record.** Contrary to the assumption (reproduced in
our own project plan from the Oracc pager configuration) that the
catalogue lacks structured sender/addressee fields, the raw
`catalogue.json` carries `ancient_author` for 349 and `recipient` for 348
of 379 entries — including 42/44 of the unlemmatized Great Powers
letters. We therefore used the catalogue fields as the primary source and
demoted formula parsing to a validation instrument.

**Validation.** A parser extracting sender and addressee from the
stereotyped address formulae (both orders: *ana* ADDRESSEE *qibīma umma*
SENDER, and the Byblos-type SENDER *qabû ana* ADDRESSEE) agrees with the
catalogue on 96.1% (sender) and 96.5% (addressee) of comparable letters.
All 18 disagreements were adjudicated against both English editions —
Moran (1992) and Rainey (2015). Both editions confirm two catalogue
errors (EA 62 is addressed to the commissioner Paḫanate, not pharaoh;
EA 301 is from Šubandu, not Yapaḫu), as well as EA 7's recipient
("Babylon" corrected to the pharaoh Rainey restores as [Napḫu]rureia).
Twelve cases resolve for the catalogue with both editions agreeing;
three remain edition-contested and are graded `disputed`: EA 169
(Moran: an unnamed high official; Rainey: "the king(?)"), EA 294 (Moran:
Adda-danu; Rainey's collation: Zimredda(!), agreeing with the Oracc
lemma against Moran), and EA 135 (lost tablet). Rainey also vindicates
two of the parser's minority readings (EA 206 Naṣība; EA 294) and reads
the contested ᵈIM-DI.KUD name a third way (Baʿlu-dāni), reinforcing the
identity-merge over any one reading. Every verdict, with supporting
quotations from both editions, ships in the repository
(`registry/adjudication_queue.csv`).

**Entity resolution.** Actors are keyed on alias-canonicalized folded
names; the hand-curated registry (17 entries) records Sumerographic
readings (IR₃-Ḫebat = ʿAbdi-Ḫeba), orthographic systems (Oracc ʿAḏiri =
conventional Aziru), contested sign readings (ᵈIM-DI.KUD = Adda-danu =
Baʿlu-šipṭi), and pharaonic throne names (Napḫurureya = Akhenaten), each
with a justification; figure preparation surfaced one residual split
identity (Labʾayu keyed as both labaya and labayu across lemma and
catalogue spellings, similarly Milki-ilu), merged before the final
run. All named pharaohs collapse to a single PHARAOH
node in the base analysis; the per-letter identification is retained for
sensitivity splits.

**Hand-coded supplements.** EA 1–44's mentioned persons were coded from
Moran's translations (44 letters; gods excluded, throne names resolved to
PHARAOH). A signed conflict layer (accusation/alliance) was coded via a
corpus-wide hostile-language sweep of Moran's translations (40 letters,
63 edges: 59 accusations, 4 alliances), each edge carrying its Moran
quotation; letters whose hostile language has only unnamed antecedents
yield no edges by rule. The full set was then independently recoded from
Rainey's (2015) translations: cross-edition agreement is 93.5% with
Cohen's κ = 0.86 (56 edges shared; 5 divergences per edition, all
traceable to textual differences between the editions — e.g., Miya as
perpetrator in Moran but victim in Rainey at EA 75 — rather than to the
coding rules). This establishes edition-robustness; since both passes
share an annotator, an independent human recoding remains the remaining
reliability step.

**Geography and provenance.** Polities were georeferenced against
Pleiades (31/55 automated with hand-review flags; regions without ancient
fixed points — Amurru, Mittani, "Syria" — remain unlocated by design).
Four automated matches proved to be classical homonyms at wildly wrong
locations (Tyre, Pihilu, Irqata, and the "Syria" region point) and were
corrected against the Pleiades bulk dump; §5.5 reports what the audit
did to a headline number. The petrographic provenance
determinations of Goren, Finkelstein & Na'aman (2004) were transcribed to
a machine-readable table (292 tablets). Where both sources speak, the
petrographic determination agrees with the Oracc catalogue's provenience
87% of the time (151/174); the disagreements reproduce Goren et al.'s own
discoveries (EA 144, sent for Zimreddi of Sidon but written at Beirut;
the Biryawaza dossier EA 194–197 written at Damascus), and 11 tablets the
catalogue lists as "unknown location" acquire a petrographic origin.

## 3. Network construction

Three layers, all built by code from the tables above:

1. **Correspondence** (directed, weighted): sender → addressee per
   letter; 111 actors, 302 letters, 117 distinct dyads. Every endpoint
   carries a confidence grade (certain 451, probable 76, restored 59,
   adjudicated 16, disputed 2 of 604); sensitivity runs drop the weaker
   grades.
2. **Mention co-occurrence** (undirected, weighted): the persons
   appearing in each letter (sender + every PN/RN lemma; PHARAOH only
   when actually named) form a clique; 244 persons, 734 dyads. The
   Great-Power letters enter via the Moran hand-coding.
3. **Conflict** (signed, directed; provisional): 63 accusation (−) and
   alliance (+) edges across 40 letters, with quotation-level provenance.

We additionally rebuild a **Cline-style graph** — correspondence edges
plus sender→mentioned stars — because replication requires the original's
construction, not just its corpus.

## 4. Methods

Descriptives are never compared to an Erdős–Rényi baseline alone. The
correspondence and Cline-style graphs are tested against degree-preserving
rewiring; the clique-projected mention layer against a *bipartite*
configuration null (shuffling person-to-letter incidences while preserving
letter sizes and person frequencies), since clique projection manufactures
triangles that edge-rewiring nulls do not discount. Centrality claims
carry (a) bootstrap-over-letters 95% rank intervals and (b) a
dossier-equalization design in which every sender contributes at most the
median dossier size (2 letters) per replicate. Inference: an ERGM on the
binarized correspondence network (edges, mutual, tier activity, tier
homophily; MCMLE converged; GOF adequate on all model statistics, MC
p ≥ 0.94), a two-dimensional three-cluster latent-space model (`ergmm`) on
the mention layer, and QAP/permutation tests (2,000 permutations) for the
geography contrasts. All analyses are seeded; `run_all.sh` regenerates
every number in this paper.

## 5. Results

### 5.1 The correspondence network has no small world to find

Global and local clustering in the correspondence layer are exactly zero
in all three edge sets (all letters; high-confidence only; without the
Byblos dossier) — below even the configuration null (95% band
0.0015–0.0051). The layer is a star on Egypt: vassals and kings wrote to
the court, not to each other (two vassal–vassal dyads exist in 302
letters). Whatever the "small world of the Amarna letters" is, it is not a
property of who wrote to whom.

### 5.2 The small world is real, mention-borne, and ~1.6× — not 49×

Rebuilt at full scale, the person-to-person mention network has 244
persons (Cline & Cline: 246 people) and clustering 0.409 (theirs: 0.391)
— we take this convergence as evidence that we have reconstructed their
object. An Erdős–Rényi comparison of the kind behind the "48.75×" claim
yields 16.5× here. But against the bipartite configuration null the
observed 0.408 stands over a null median of 0.253 (95% band 0.235–0.271):
significant — the observed value lies outside the null band in every
variant, including without the Byblos dossier (0.452 vs. 0.315) — but a
factor of ~1.6. The small world of the Amarna letters exists; the
astronomical multiplier was an artifact of the weakest available null.
The Cline-style star construction, by contrast, clusters at 0.034, at or
below its null — confirming that triadic structure comes from mentions
connecting *third parties*, not from anyone's correspondence.

### 5.3 Rib-Hadda's brokerage, decomposed

Cline & Cline's flagship finding — Rib-Hadda of Byblos out-brokering the
pharaohs — replicates *exactly* under their choices: in the Cline-style
graph with pharaohs split by identification (Amenhotep III, Amenhotep IV,
and a residual "the king"), Rib-Hadda's betweenness (5,382) exceeds
Amenhotep III's (2,836) and Amenhotep IV's. But the residual unidentified
pharaoh — most letters address only "the king" — holds 25,797, five times
Rib-Hadda's score. The finding is an artifact of dividing one actor's
identity across three nodes under uncertainty. From there the correction
proceeds stepwise: collapse the pharaohs and Rib-Hadda is second;
move to the person-to-person layer and he is ~7th (bootstrap median 7,
95% interval 4–12); equalize dossier volume and he is 15th with
P(top 3) = 0.00. His 63-letter dossier buys eigenvector attachment to the
hub, and nothing else.

The stable brokers, in every construction and correction, are **Aziru of
Amurru** (rank 1 with P(top 3) = 0.95–0.98 across designs) — the defector
who bridged Egypt's orbit and Hatti's, and simultaneously the
most-accused actor in the conflict layer — and, once volume is corrected,
**Yanḥamu**, the Egyptian commissioner (P(top 3) = 0.67), vindicating the
hypothesis that pharaoh's officials, not the loudest vassal, carried the
network. In the provisional conflict layer, Aziru again tops betweenness:
he is the figure accused from Byblos, Tyre, and Damascus at once.

### 5.4 The diplomatic system as coefficients

The ERGM formalizes the two-tier reading: reciprocity is strong and
significant (mutual = +3.78 ± 0.80), concentrated at the Great-Power tier
(17% of Egypt↔Great-Power dyads reciprocated vs. 4% of Egypt↔vassal,
the latter being Egyptian file copies), and tier homophily is strongly
*negative* (nodematch = −2.21 ± 0.64): Amarna correspondence is
cross-tier by construction — the brotherhood of kings and the servitude
of vassals both materialize as letters to Egypt, not within-tier
correspondence. The latent-space model finds three clusters that do not
recover the tiers: mention-layer communities (modularity ≈ 0.56) are
political theatres — the Amurru crisis, the Damascus–Qadesh axis, the
Shechem–Jerusalem conflict, the Tyre–Sidon feud — not diplomatic ranks.

### 5.5 Geography: the pre-registered contrast, recovered by audit

Distance decays ties in the mention layer (point-biserial r = −0.147, QAP
p < 0.001): neighbors name neighbors. The conflict layer agrees
(r = −0.298, QAP p = 0.001, n = 14 located actors). We had predicted *no*
distance effect in the correspondence layer — all vassals write to
distant Egypt regardless — and an earlier draft reported that prediction
overturned (ρ = −0.50, p = 0.002). Auditing that finding dissolved it,
in three layers that are worth recounting because they enact the paper's
thesis. First, six of 39 data points were gazetteer phantoms: four
actors coded to a "Syria" *region* whose Pleiades match lies in the
Ionian Sea, Pihilu matched to Macedonian Pella, Irqata to an Anatolian
Arca — all far-with-few-letters, exactly the shape that manufactures
decay (Tyre was likewise mislocated to a homonymous Hellenistic estate
in Jordan). Second, with 14 of 35 vassals tied at one letter, Spearman
without tie-averaged ranks let input row order leak into the statistic;
correcting both leaves ρ = −0.32 (p = 0.07). Third, the residual trend
is compositional: it concentrates in polities with political reasons to
write little — Hatti-aligned Qadesh and Sidon (EA 174–176, 148–149) and
quasi-independent Ugarit — without which ρ = −0.18 (p = 0.32); a
leave-one-polity-out jackknife retains nominal significance in only
7 of 24 deletions. A partialled design against hand-coded covariates
(distance to the nearest Egyptian administrative center — Gaza, Joppa,
Beth-Shean, Kumidi, Ṣumur; coastal access; Hatti alignment) finds no
predictor of epistolary volume, court distance included (partial
r = −0.26, p = 0.17). The sign stays negative in every variant, so a
weak true decay is not excluded; but the defensible statement is the
pre-registered one: geography structures whom the letters *talk about*,
not who talks to Egypt.

## 6. Discussion

The revision this study proposes is not that Cline & Cline were wrong but
that each of their results is the output of an unstated constructional
switch. Split the pharaoh's identity and Rib-Hadda out-brokers kings;
collapse it and he does not. Compare against an Erdős–Rényi graph and the
archive is a 49× marvel; compare against a null that knows letters come
in groups and it is a 1.6× society. Count a man's own dossier and he is
central; ask what remains when every voice speaks at equal volume and the
brokers are the defector Amurru dynast and pharaoh's own commissioner.
None of these switches is illegitimate — but they must be visible, and
their consequences measured, before centrality in a survival-biased
ego-archive is read as ancient history.

What survives every correction is historically satisfying: a two-tier
system statistically legible in one coefficient (+ reciprocity above, −
homophily across), inter-vassal politics organized in regional conflict
theatres invisible to the correspondence graph, brokerage lodged in
exactly the two figures — Aziru, Yanḥamu — whose careers the letters
narrate as boundary-crossing, and a mention society whose modest but real
small-world excess reflects genuine third-party political entanglement.
The archive measures salience to Egypt; measured carefully, that salience
still has structure worth explaining.

## 7. Limitations

The conflict layer is corpus-wide and edition-robust (cross-edition
κ = 0.86) but single-annotator; an independent human recoding (PLAN §7)
remains desirable. EA 1–44 mentions were hand-coded from translation
rather than lemmata (a documented source seam that will close when Oracc
releases the Great Powers letters). The Oracc catalogue snapshot dates to
2024; Rainey's (2015) collations were consulted for all adjudicated
header cases, though not systematically for the mention and conflict
coding, which rests on Moran's translations. Entity resolution is registry-v1 and single-passed;
petrographic transcription is automated-plus-review (key 2 pending).
Senders whose polity the catalogue string does not state default to the
vassal tier (14 minor correspondents of 1-3 letters each, after the
EA 12 correction); Ugarit's rulers are likewise coded vassal though the
kingdom's standing was closer to client-of-both-courts. At these
actors' letter volumes neither choice can move the tier coefficients,
but both are choices, not facts.
Chronology is coarse by design: a two-phase sensitivity split (reign
identifications plus the Amurru-succession anchor; 71% of letters
honestly unassigned) reproduces the small-world excess within each phase
(early CC 0.454 vs. null 0.297; late 0.480 vs. 0.395, marginal) and
keeps brokerage with the Amurru dynasty in both eras — ʿAbdi-Aširta
early, Aziru late — though the anchor guarantees their presence (not
their rank) by construction. Finer temporal claims remain out of
scope. Geographic coverage reaches 64% of letters at both endpoints;
region-states without fixed points (Amurru, Mittani, "Syria") are
excluded from distance tests rather than imputed — which costs the
correspondence distance test four actors and Amurru entirely, so the
compositional analysis of §5.5 cannot see the system's most consequential
defector. The administrative-center covariate is coded from five
garrison/commissioner seats attested in the letters themselves; a finer
gradient (commissioner itineraries, road networks) is future work.

## 8. Data and code availability

All code (MIT), derived tables (CC-BY), and this draft:
https://git.sr.ht/~calgacus/ussira-pitati. Oracc corpus text is CC-BY-SA
(Lauinger & Yoder / Izre'el) and is not redistributed; Moran (1992) and
Goren et al. (2004) are quoted within scholarly fair use. A Zenodo
deposit with DOI accompanies submission.

## References (selected, to be completed)

- Cline, D. H. & Cline, E. H. 2015. "Text Messages, Tablets, and Social
  Networks: The 'Small World' of the Amarna Letters." In Mynářová et al.
  (eds.), *There and Back Again — the Crossroads II*, 17–44.
- Cline, E. H. 2025. *Love, War, and Diplomacy*. Princeton UP.
- Moran, W. L. 1992. *The Amarna Letters*. Johns Hopkins UP.
- Rainey, A. F. 2015. *The El-Amarna Correspondence*. Brill.
- Goren, Y., Finkelstein, I. & Na'aman, N. 2004. *Inscribed in Clay*.
  Tel Aviv University.
- Lauinger, J. & Yoder, T. (eds.). Oracc AEMW/Amarna.
- Brughmans, T. & Peeples, M. 2023. *Network Science in Archaeology*.
  Cambridge UP.
- Hunter, D. & Handcock, M. — ERGM geometrically weighted terms; statnet.
- Krivitsky, P. & Handcock, M. — latentnet.
