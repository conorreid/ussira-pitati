# Project 1A — "The Amarna Network, Done Right"
## A Project Plan for a Rigorous, Reproducible Social Network Analysis of the Amarna Letters

*Prepared for a history/economics graduate with strong software and statistics skills, reading knowledge of Ancient Greek and Italian, and no prior background in Assyriology or digital humanities. Current as of 31 July 2026.*

---

## TL;DR
- **The project is feasible and can start now.** The Oracc "Amarna Letters" corpus (project path `aemw/amarna`, the sub-project directed by Jacob Lauinger and Tyler Yoder within the AEMW umbrella directed by Jacob Lauinger and Matthew Rutz) now contains **305 lemmatized texts** — the full Levantine vassal correspondence including the Phoenician letters — downloadable as `aemw-amarna.zip` under CC-BY-SA. Only the ~50 "Great Powers" letters (EA 1–44) and the inventories remain unreleased, so a rigorous, reproducible upgrade of Cline & Cline (2015) can begin immediately on the vassal network, hand-coding the Great-Power tier from Moran (1992) and Rainey (2015).
- **The intellectual value-add is statistical inference and bias-correction, not prettier graphs.** Cline & Cline's hand-coded NodeXL study (clustering coefficient 0.391, reported as ~48.75× higher than a comparable random network; Rib-Hadda of Byblos with the highest betweenness centrality) and Eric Cline's 2025 trade book (246 named people, 464 connections) are descriptive. The contribution here is (a) explicit modeling of the archive-survival bias — the whole archive is an ego-network centered on Egypt and was excavated in Egypt — and (b) inferential models (ERGMs / latent-space models / SBMs / QAP) testing tier homophily, reciprocity, and distance-decay against null models.
- **The single biggest data-engineering task is entity resolution, not ingestion.** The Oracc catalogue exposes `place/provenience`, `subgenre` ("client letter"), `period`, and `designation` (EA number) — but **no structured `sender`/`addressee` fields**; the personal names of senders/addressees must be parsed from each letter's stereotyped opening address formula and normalized across variant spellings (Rib-Hadda/Rib-Addi; "the king" = pharaoh). Budget the plan around that.

---

## Key Findings (Resource Verification Status)

| Resource | Status | Detail |
|---|---|---|
| **Oracc Amarna corpus** (`oracc.museum.upenn.edu/aemw/amarna/`) | **Verified live** | Now **305 texts** (`tmax=305`), up from an initial set of 218 released 2 April 2021. All Levantine vassal + Phoenician letters lemmatized. Great Powers (EA 1–44) + inventories still pending ("final update," undated). CC-BY-SA, 2014–. |
| **JSON download** (`oracc.museum.upenn.edu/json/`) | **Verified** | `aemw-amarna.zip` listed. Standard Oracc structure: `corpusjson/P######.json` per text (CDL tree with transliteration + lemmatization) + `catalogue.json` + glossary files (`gloss-akk.json` etc.) + `metadata.json`. |
| **Catalogue fields** | **Verified via pager config** | `cat_fields=designation,primary_publication,subgenre\|genre,period,place\|provenience`. **No `sender`/`addressee`/`ancient_author` fields** — sender is encoded as place-of-origin + `subgenre`; personal names must be parsed from letter headers. |
| **CDLI** (`cdli.earth` / `cdli.ox.ac.uk`) | **Verified** | Amarna tablets have P-numbers (e.g. EA 254 = P271197; VAT numbers from the Vorderasiatisches Museum Berlin). Izre'el's transliterations were uploaded to CDLI/Oracc in C-ATF; tablet images (esp. Berlin) available. |
| **Izre'el transliterations** | **Verified** | Definitive version of 378 tablets, contributed to Oracc; underlies the Lauinger–Yoder edition. |
| **Moran, *The Amarna Letters* (1992, JHU Press)** | **Verified in print** | Standard English translation; EA numbering. |
| **Rainey, *The El-Amarna Correspondence* (2015, Brill, HdO 110, 2 vols)** | **Verified** | New collation-based edition/translation, ed. Schniedewind & Cochavi-Rainey. |
| **Goren, Finkelstein & Na'aman, *Inscribed in Clay* (2004, Tel Aviv)** | **Verified** | Petrographic provenance of 300+ tablets; also BASOR 329 (2003) on Amurru. Book-table data, not a downloadable dataset. |
| **Pleiades** (`pleiades.stoa.org`) | **Verified** | 36,000+ places, expanding into ANE; CC-BY; bulk dumps (CSV/KML/RDF) at atlantides.org. Levantine ANE coverage partial — verify each toponym. |
| **R: ergm/statnet, latentnet, Bergm** | **Verified on CRAN** | `statnet` suite maintained; `latentnet::ergmm()` (docs updated Sept 2025); `Bergm` for Bayesian ERGMs. |
| **Python: networkx, igraph, graph-tool** | **Verified** | All maintained; `graph-tool` includes degree-corrected SBM inference. |
| **Cline & Cline 2015** | **Verified** | In *There and Back Again — the Crossroads II*, ed. Mynářová, Onderka, Pavúk, pp. 17–44, Charles University Prague. |

---

## 1. Project Definition and Research Questions

### 1.1 Background and motivation
The Amarna letters are the archive found at Tell el-Amarna (ancient Akhetaten), Akhenaten's capital, dating mostly to Amenhotep III (c. 1390–1353 BC) and Akhenaten (c. 1353–1336 BC) — a window of roughly 30 years. In the words of the Oracc project itself, "the corpus of cuneiform texts known as 'the Amarna letters' comprises 346 letters (one actually found at Tell el-Hesi) and four administrative lists (28 scholarly and literary texts were found with these archival texts and probably used in the training of the scribes)," ~382 tablets in all. They fall into two tiers: correspondence with the **Great Powers** ("brotherhood of kings": Babylonia, Assyria, Mitanni, Hatti, Arzawa, Alashiya) and with **Levantine vassals** (Byblos/Gubla, Tyre, Sidon, Amurru, Shechem, Jerusalem/Urusalim, Megiddo, Gezer, Ashkelon, Lachish, Hazor, etc.).

Cline & Cline (2015) hand-coded a network in NodeXL and reported "small-world" structure: "the clustering coefficient of the Amarna letters network is 0.391 (as calculated by the NodeXL program), which is nearly fifty times higher (48.75, to be precise) than it would be if it were simply a random network." They found that "Rib-Hadda, the mayor of Byblos, scores even higher than Amenhotep III and Akhenaten in Betweenness Centrality, because in his 60 letters he mentions people who otherwise would not be in our database, and thus in the social network," and — strikingly — that "the pharaohs dominate only two of the ten clusters in the network." Eric Cline's *Love, War, and Diplomacy* (Princeton UP, 2025) extends this to the **246 people named in the letters** and the **464 connections between them**. These works are valuable but exploratory: no null models, no inferential tests, no bias correction, and hand-coded (hence hard to reproduce). The observation that Rib-Hadda's high betweenness comes from the *mentions* inside his own large dossier is itself the seed of this project's central methodological worry.

### 1.2 Research questions
**RQ1 (Brokerage under bias).** Which actors are structurally central/brokers in the correspondence and mention networks, and do those rankings survive once the Egypt-centric archive-survival bias is modeled? *Hypothesis:* Rib-Hadda's dominant betweenness is partly an artifact of his large Byblos dossier (60 letters per Cline & Cline; other tallies run to ~64–70) and of the fact that mentions are drawn disproportionately from it; Egyptian officials (commissioners such as Yanhamu, Pawura, Pihuri) may emerge as the true structural brokers once mentions are properly weighted.

**RQ2 (Tier homophily).** Is the network consistent with tier homophily — Great Powers corresponding among themselves and with Egypt as peers, vassals corresponding only with Egypt (and its officials)? *Hypothesis:* strong block structure; near-zero direct vassal↔Great-Power correspondence ties; vassal↔vassal ties appear almost exclusively as hostile *mentions*, not correspondence.

**RQ3 (Reciprocity by tier).** Does reciprocity of correspondence (and of mentions) differ by tier? *Hypothesis:* Great-Power ties are reciprocated (letters both directions survive, e.g. Akhenaten↔Burna-Buriash II of Babylonia); vassal ties are structurally non-reciprocal (vassal→pharaoh dominates; the few pharaoh→vassal letters, e.g. EA 99, 162, 367, 369, 370, are rare survivals of Egyptian file copies).

**RQ4 (Mention/conflict network vs. correspondence network).** What does the mention/co-occurrence network reveal that the correspondence network cannot — specifically the inter-vassal *conflict* network (signed edges: accusations, alliances)? Sub-dossiers to encode: Rib-Hadda vs. Abdi-Ashirta then his son Aziru of Amurru (Abdi-Ashirta's death noted in EA 101; Aziru later captures/exiles Rib-Hadda and defects to Hatti); Labaya of Shechem (and "the sons of Labaya") vs. Biridiya of Megiddo and Abdi-Heba of Jerusalem; Abdi-Heba vs. Milkilu of Gezer and Shuwardata of Gath/Hebron — who nonetheless *ally* with Abdi-Heba against the ʿApiru in EA 366. *Hypothesis:* the conflict network has its own high-betweenness brokers (Amurru, Gezer) invisible in the correspondence graph.

**RQ5 (Geography and provenance as predictors).** Do geographic distance (via Pleiades coordinates) and petrographic provenance (Goren, Finkelstein & Na'aman 2004) predict tie presence/strength and community membership? *Hypothesis:* distance-decay in the conflict/mention network (neighbors accuse neighbors) but *not* in the correspondence network (all vassals write to distant Egypt regardless of distance) — a testable structural contrast, and a use of petrography that goes beyond its usual philological application.

---

## 2. Data Sources and Access

### 2.1 Primary corpus — Oracc `aemw/amarna`
- **Web:** `http://oracc.museum.upenn.edu/aemw/amarna/` (hub, pager/browse, glossaries, bibliography). **305 texts** currently, CC-BY-SA, 2014–.
- **Bulk data:** `http://oracc.museum.upenn.edu/json/aemw-amarna.zip`. Inside: a `corpusjson/` directory with one `P######.json` per text (the CDL tree carrying transliteration + lemmatization), a `catalogue.json` (metadata manifest), glossary JSON files, and `metadata.json`. Parse with Python `zipfile` + `json`. The canonical template is Niek Veldhuis's "Computational Assyriology (Compass)"/`sumnet` `parse_ORACC_json()` routine; Ellie Bennett's `ORACC-download` GitHub repo is a lighter, filterable remix. **Do not scrape the website** (robots-blocked) — use the zip.
- **Critical caveat (verified directly):** the catalogue's field configuration is `designation, primary_publication, subgenre|genre, period, place|provenience`, plus the standard Oracc `id_text` and a modern-editor `author` field. There are **no structured `sender`/`addressee`/`ancient_author` fields.** Direction of correspondence is encoded as *place of origin* (the sender's polity: Byblos, Tyre, Amurru, Jerusalem, Nuhašše, …) + `subgenre` ("client letter" = client king → Egypt). The *personal name* of the sender (Rib-Hadda, Aziru, Abdi-Heba) and the addressee ("the king"/pharaoh) must be extracted by parsing the opening address formula from the lemmatized text. The stereotyped formula — "To the king, my lord … message of NN, your servant" / *umma NN* — makes this highly tractable (see §3.2).

### 2.2 Secondary / corroborating text sources
- **CDLI** (`cdli.earth`): P-numbers, catalogue, C-ATF transliterations, tablet images (esp. Berlin VAT tablets). Use to cross-check the P-number↔EA↔museum-number mapping and to backfill provenance metadata.
- **Moran, *The Amarna Letters* (1992)** and **Rainey, *El-Amarna Correspondence* (2015)**: the two English editions. Essential for (a) hand-coding the unreleased Great-Power letters EA 1–44, and (b) validating parsed sender/addressee/mention data against expert translation.
- **Izre'el's transliterations** (378 tablets, in Oracc/CDLI): the philological substrate.
- **Liverani, *Le lettere di el-Amarna* (2 vols, 1998/1999, Paideia)** — the Italian edition (leverage the reader's Italian) whose "Piccoli Re" / "Grandi Re" split operationalizes the tier distinction directly.

### 2.3 Geographic and provenance layers
- **Pleiades**: fetch each toponym's place record (JSON/CSV) and store the canonical Pleiades URI + representative point coordinates. ANE Levantine coverage is only partial; for any toponym absent from Pleiades, fall back to the **World Historical Gazetteer / Wikidata / Goren et al.'s located provenances** and flag as lower-confidence.
- **Goren, Finkelstein & Na'aman, *Inscribed in Clay* (2004)** + **BASOR 329 (2003)**: petrographic provenance for 300+ tablets, keyed by EA number. This is book-table data — hand-transcribe the relevant tables into a CSV keyed by EA number (a Phase-1 deliverable, double-keyed to catch transcription errors). It resolves several sender locations (e.g. Biryawaza; Hiziru↔Zuhra on the Gilead plateau) and constrains Alashiya, Tunip, and the territorial expansion of Amurru.

### 2.4 Data pipeline (concrete)
```
aemw-amarna.zip
   ├─ corpusjson/P######.json  ─▶  [ingest.py: parse_oracc_json]
   └─ catalogue.json           ─▶  text-level table (EA#, P#, place, subgenre, period)
                                          │
   [header_parser.py] ─▶ raw sender/addressee strings (from the address formula)
                                          │
   [entity_resolution.py + canonical_registry.csv] ─▶ resolved actor IDs
                                          │
   ├─ nodes.csv           (actor_id, canonical_name, tier, polity, Pleiades_URI, lat, lon)
   ├─ edges_corr.csv      (src_actor, dst_actor, EA#, weight)
   ├─ edges_mention.csv   (actor_i, actor_j, EA#, cooccur)
   └─ edges_conflict.csv  (src, dst, EA#, sign{+/–}, type{accuse,ally})
```
All tables key on the **EA number** as the stable join across Oracc, CDLI, Moran/Rainey, Pleiades, and Goren et al.

---

## 3. Network Construction Decisions

### 3.1 Three networks (with trade-offs)
1. **Correspondence network** — directed sender→addressee, weighted by letter count. *Pro:* cleanest signal, closest to Cline & Cline for replication. *Con:* dominated by the Egypt hub and Rib-Hadda's volume; structurally an ego-network of Egypt.
2. **Mention/co-occurrence network** — undirected (or directed for "X says Y did Z"): an edge when two named entities co-occur in a letter. *Pro:* recovers the vassal↔vassal and official↔ruler structure invisible in correspondence — where the real politics live. *Con:* sensitive to entity-resolution error and to the definition of a "mention."
3. **Accusation/conflict network** — signed, directed edges (accusation = negative; stated alliance = positive). *Pro:* directly answers RQ4; historically the richest layer. *Con:* requires interpretive hand-coding → inter-annotator reliability needed (§7); cannot be fully automated.

### 3.2 Node-definition problems
- **Variant spellings / same person:** Rib-Hadda = Rib-Addi = Rib-Addu; Abdi-Heba = Abdi-Ḫeba (= older "Er-Heba"); Labaya = Lab'ayu. Resolve via the **Oracc glossary / proper-noun lemmatization** (each attested name form links to a lemma ID) plus a hand-curated `canonical_registry.csv` mapping lemma IDs → canonical actors. Keep Oracc lemma IDs as the backbone so the mapping is reproducible and auditable.
- **"The king" = pharaoh:** the addressee is almost always the reigning pharaoh, given by title not name. Decision: collapse to a single `PHARAOH` node for the base analysis, with a sensitivity variant splitting Amenhotep III vs. Akhenaten where dossier chronology allows (§3.4).
- **Unnamed / title-only actors:** commissioners and officials (Yanhamu, Pawura, Pihuri, Amanappa, Maya) are sometimes named, sometimes only titled (*rābiṣu*, "commissioner"). Decision: create a node only when a personal name is attested; record title-only references as attributes, not nodes, to avoid inflating brokerage artificially. (Mynářová's work on the officials layer, §5, is the guide here.)
- **Collective actors:** "sons of Abdi-Ashirta," "sons of Labaya," the ʿApiru/Habiru, "the people of city X." Decision: model as distinct collective nodes flagged `is_collective=TRUE`, analyzed both included and excluded (sensitivity).

### 3.3 Uncertain sender/addressee
Many letters are fragmentary. Decision: assign a `confidence` field (certain / probable / restored-by-editor / unknown) sourced from Moran/Rainey/Izre'el. Base analysis uses certain+probable; robustness reruns exclude "probable" (§7).

### 3.4 The Great-Power letters (EA 1–44) and temporal ordering
- **Not yet in Oracc.** Hand-code sender/addressee/mentions for EA 1–44 from Moran (1992) and Rainey (2015). These ~50 letters are metadata-light but have unambiguous royal senders (Kadashman-Enlil and Burna-Buriash II of Babylonia, Tushratta of Mitanni, Suppiluliuma I of Hatti, Ashur-uballit I of Assyria, the kings of Alashiya and Arzawa), so hand-coding is low-risk and fast. Re-fold the Oracc data when the final release appears.
- **Temporal ordering** is only *relative*, via internal cross-references and prosopography. Anchors include the Amurru succession (Abdi-Ashirta's death in EA 101 → Aziru); Aziru's letters EA 157 and 164–167, reordered by scholars across a ~5-year "One-Year War"; and Rib-Hadda's dossier as a chronological spine (references to Amanappa's arrival, to Abdi-Ashirta then Aziru, and to his brother Ili-Rapih's succession in EA 139–140). Use the dossier orderings of Moran, Na'aman, and Mynářová. Decision: treat time as **ordinal phases** (early / middle / late Amarna), not absolute dates; run the network both as a single static aggregate and split by phase (sensitivity), acknowledging that fine-grained temporal SNA is not defensible given the uncertainty.

---

## 4. Statistical Methodology

### 4.1 Descriptive SNA with null models
Compute degree (in/out), betweenness, eigenvector, and closeness centrality; global and local clustering; component structure; and community detection (Louvain **and** Leiden — report both; Leiden avoids Louvain's badly-connected-community artifacts). **Every descriptive statistic must be compared to a null model,** not reported raw:
- **Degree-preserving configuration model** (rewire holding the degree sequence) — tests whether observed clustering/centralization exceeds chance given the skewed degree distribution (the Egypt and Rib-Hadda hubs). This directly interrogates the Cline & Cline "48.75× random" claim by making the null explicit and reproducible.
- **Permutation tests** for group-level contrasts (e.g. mean betweenness of officials vs. rulers).
- Report centrality as **rank with uncertainty**, not point estimates, following the archaeological-network guidance of Brughmans & Peeples, *Network Science in Archaeology* (Cambridge, 2023), and Peeples' Monte Carlo resampling tutorials (archnetworks.net).

### 4.2 Inferential models
**(a) ERGMs** (`ergm`/`statnet` in R). For a network of ~100–400 nodes this is feasible but degeneracy-prone. Relevant terms:
- `edges` (baseline density), `mutual` (RQ3 reciprocity), `nodematch("tier")` (RQ2 homophily), `nodefactor("tier")` (differential activity), `edgecov(distance)` and `edgecov(same_provenance)` (RQ5), `nodecov` for dossier size.
- **Avoid raw `triangle`/`kstar` terms** (the classic degenerate specification — statnet's own tutorials show the edges+triangle model heading "somewhere very bad"). Use geometrically-weighted terms (`gwesp`, `gwdegree`) per Hunter & Handcock; check `mcmc.diagnostics()` and GOF.
- Known risk: small dense networks → MCMLE may fail to converge. Mitigations below.

**(b) Latent-space / latent-cluster models** (`latentnet::ergmm()`): embed actors in a latent social space; naturally captures block/tier structure and yields interpretable clustering without triangle-term degeneracy. It is dyad-independent but robust — the recommended primary alternative if ERGMs misbehave.

**(c) Stochastic block models** (Python `graph-tool` degree-corrected SBM; or `latentnet` clustering): directly test the tier-block hypothesis (RQ2) and detect data-driven blocks to compare against the a priori Great-Power/vassal/Egypt partition. Degree-correction is essential given the Rib-Hadda/Egypt hubs.

**(d) Bayesian ERGMs** (`Bergm`): quantify parameter uncertainty on the small network; more stable than point MCMLE for sparse/small data.

**(e) QAP / MRQAP regression** (`sna::netlm`/`netlogit`, or a Python equivalent): regress the tie matrix on distance and same-provenance matrices with permutation-based inference. This is the **safe fallback** for RQ5 if ERGMs fail — dyad-level, no degeneracy, directly interpretable.

### 4.3 Archive/survival-bias handling (the methodological core)
The archive is (i) **egocentric** — centered on Egypt, which is by construction a node of every correspondence tie; (ii) **survival-biased** — we see letters *received* by Egypt plus file-copies Egypt kept, not the vassals' own archives; (iii) **spatially biased** — everything was excavated in one place.
- Frame the correspondence network explicitly as an **ego-network of Egypt**, and locate the substantive inferential work in the **mention/conflict networks**, which are less directly an artifact of who-filed-what.
- Apply the **missing-data / sampling-sensitivity toolkit** from archaeological network science (Brughmans, Peeples, Collar — the "Oxford school"; Collar, Coward, Brughmans & Mills, "Networks in Archaeology," *J. Archaeol. Method Theory* 22, 2015): bootstrap over letters; simulate node/edge removal; test whether centrality rankings survive plausible missingness (cf. "Filling the Gaps — Computational Approaches to Incomplete Archaeological Networks," *J. Archaeol. Method Theory*, 2024).
- State plainly (in text and caveats) that **centrality in a survival-biased egocentric archive measures salience-to-Egypt, not raw historical importance.** This reframing is itself a contribution.

### 4.4 Validation
- **Replication target:** reproduce Cline & Cline's clustering coefficient (0.391) and Rib-Hadda's top betweenness on a comparable network definition, then show how the results change under (i) inferential modeling and (ii) bias correction — documenting every definitional choice that moves the number.
- **Convergent validity:** compare automated parsed sender/addressee/mentions against Moran/Rainey hand-coding on a sample.
- **GOF** for ERGM/latent models; posterior predictive checks for Bayesian/SBM.

---

## 5. Prior Literature to Engage

**Network study of Amarna specifically**
- Cline, D. H. & Cline, E. H. (2015), "Text Messages, Tablets, and Social Networks: The 'Small World' of the Amarna Letters," in *Crossroads II*, ed. Mynářová et al., pp. 17–44 (the direct predecessor; NodeXL; CC 0.391 ≈ 48.75× random; Rib-Hadda top betweenness from his 60 letters; pharaohs dominate only 2 of 10 clusters).
- Cline, E. H. (2025), *Love, War, and Diplomacy* (Princeton UP) — the 246 named people and 464 connections; Akhenaten–Burna-Buriash shared contacts.
- Siat, K. M. (Manchester PhD; ICE XIII Leiden 2023 pilot), SNA of *women / female agents* in the Amarna letters (sampled EA 1–6, 8–13, 17; note EA 26, the Mitanni king Tushratta → an Egyptian queen). Engage as complementary (gender-focused) and as a caution on small-sample SNA.
- Chollier, V. (2020), "Social Network Analysis in Egyptology," *JEA* — methods and limits.

**Amarna history, diplomacy, philology (to pose the questions well)**
- Moran (1992) and Rainey (2015) — the editions. Liverani (1998/1999, Italian) — the tiered edition. Izre'el — the transliterations.
- Liverani, *Prestige and Interest* / *International Relations in the Ancient Near East 1600–1100 BC* (2001) — the "prestige vs. interest" and Great-Power-club framing.
- Cohen & Westbrook (eds.), *Amarna Diplomacy: The Beginnings of International Relations* (JHU Press, 2000).
- Podany, *Brotherhood of Kings* (OUP, 2010) — the brotherhood/reciprocity concepts underpinning RQ3.
- Mynářová, *Language of Amarna – Language of Diplomacy* (2007), "The Representatives of Power in the Amarna Letters" (2012), and *Egyptian State Correspondence of the New Kingdom* (2018) — address formulae and the officials/commissioners layer, directly operationalizable for header parsing and node definition.
- Na'aman — chronological and political studies (dossier ordering).
- Goren, Finkelstein & Na'aman (2004), *Inscribed in Clay* — provenance.

**Historical / archaeological network methods**
- Brughmans & Peeples, *Network Science in Archaeology* (Cambridge, 2023) + Online Companion (book.archnetworks.net) — the primary methods handbook; R code for null models, sensitivity analysis, spatial networks.
- Collar, Coward, Brughmans & Mills (2015), "Networks in Archaeology," *JAMT* 22:1–32.
- Brughmans & Peeples (eds.), *The Oxford Handbook of Archaeological Network Research* (2023).
- *Journal of Historical Network Research* Vol. 4 (2020), "The Ties That Bind: Ancient Politics and Network Research."
- Latent-space model review (arXiv 2012.02307); statnet ERGM tutorials.

**Computational Akkadian / NLP (for scaling and future NER)**
- Gordin et al. (2020), "Reading Akkadian cuneiform using natural language processing," *PLOS ONE* — Akkademia (HMM/MEMM/BiLSTM transliteration; ~96.7% BiLSTM accuracy).
- Gutherz, Gordin, Sáenz, Levy & Berant (2023), "Translating Akkadian to English with neural machine translation," *PNAS Nexus* 2(5):pgad096.
- Fetaya et al. (2020, *PNAS*) and Lazar et al. (2021, EMNLP) — text restoration / masked-LM for broken Akkadian (relevant to fragmentary letters).
- MTAAC (Machine Translation and Automated Analysis of Cuneiform) — Sumerian-focused, but methodologically relevant for name/place NER.

---

## 6. Work Plan (Phases, Deliverables, Durations, Risks)

Assumes **~8–10 hrs/week part-time**. Durations in part-time weeks.

**Phase 0 — Environment & data audit (2 wk).**
Deliverables: reproducible environment (Python: `networkx`, `igraph`, `graph-tool`, `pandas`; R: `statnet`/`ergm`, `latentnet`, `Bergm`, `sna`; managed with `renv` + `conda`/`uv`; Git repo). Download `aemw-amarna.zip`; audit lemmatization coverage against the 305 texts; confirm which EA numbers are present/absent (Great Powers absent). *Deliverable:* `coverage_report.md`.
Risk: Oracc robots-block on scraping → use the bulk zip, not page scraping (mitigated).

**Phase 1 — Ingestion & entity normalization (4 wk).**
Deliverables: `ingest.py` (JSON→tables); `header_parser.py` extracting sender/addressee from address formulae; `canonical_registry.csv` (lemma ID→actor, with tier/polity); Pleiades URI + coordinate join; Goren et al. provenance CSV (hand-keyed, double-checked); Great-Power letters EA 1–44 hand-coded from Moran/Rainey. *Deliverable:* versioned `nodes.csv` + edge lists.
Risk: no structured sender/addressee fields → header parsing required (anticipated; formulae are stereotyped). Fallback: hand-code from Moran/Rainey where parsing fails. Risk: Pleiades gaps → WHG/Wikidata fallback with confidence flags.

**Phase 2 — Correspondence network + descriptives + null models (3 wk).**
Deliverables: directed weighted correspondence graph; centrality tables with configuration-model/permutation nulls; Louvain + Leiden communities; **replication of Cline & Cline's 0.391 / Rib-Hadda betweenness**; `phase2_report`.

**Phase 3 — Mention & conflict networks (3 wk).**
Deliverables: co-occurrence mention graph (semi-automated from lemmatized proper nouns); hand-coded signed conflict graph for the key dossiers (Amurru, Shechem, Jerusalem, Gezer, Megiddo); inter-annotator reliability check (§7).

**Phase 4 — Inferential modeling (4 wk).**
Deliverables: ERGM (homophily / reciprocity / distance), with latent-space (`ergmm`) and SBM (`graph-tool`) as parallel models; QAP for distance/provenance; Bayesian ERGM for uncertainty; GOF + convergence diagnostics.
Risk: ERGM non-convergence/degeneracy → drop to gw-terms; if still failing, report latent-space + SBM + QAP as primary (pre-registered fallback).

**Phase 5 — Write-up & release (4 wk).**
Deliverables: article draft + data paper; Zenodo deposit (DOI) of code + derived data; GitHub repo; independent reproducibility check.

Total ≈ 20 part-time weeks (~5 months) to a first submittable draft.

### First-90-days timeline (~8–10 hrs/wk)
- **Weeks 1–2 (Phase 0):** environment + repo + corpus download + coverage audit. *Milestone: `coverage_report.md`.*
- **Weeks 3–4:** header-parser prototype on 20 letters; validate against Moran. *Milestone: parser ≥90% agreement on the sample.*
- **Weeks 5–7:** full ingestion; `canonical_registry.csv` v1; Pleiades + Goren joins. *Milestone: `nodes.csv` + `edges_corr.csv` v1.*
- **Weeks 8–9:** hand-code Great-Power EA 1–44; build the correspondence graph + descriptive stats. *Milestone: Cline & Cline replication attempt.*
- **Weeks 10–11:** configuration-model + permutation nulls; Louvain/Leiden. *Milestone: bias-aware centrality ranking.*
- **Week 12:** mention-network prototype + conflict-coding schema + first inter-annotator pilot. *Milestone: go/no-go review; decide the primary inferential model for Phase 4.*

---

## 7. Validation and Robustness
- **Inter-annotator checks** on hand-coded conflict/alliance edges: two coders (you + an Assyriologist collaborator, or a second pass after a cooling-off interval) on a shared subset; report Cohen's κ; adjudicate disagreements; only edges above an agreement threshold enter the base network.
- **Sensitivity to uncertain attributions:** rerun all analyses excluding "probable"/"restored" senders and mentions.
- **Bootstrap over letters:** resample letters with replacement; report centrality-rank stability intervals.
- **With / without the Rib-Hadda dossier:** the Byblos letters dominate the corpus (Cline & Cline count 60; Mynářová notes Rib-Hadda supplied roughly half of her letters-to-officials sample; other tallies run to ~64–70). Rerun with the dossier down-weighted and fully removed to test how much the "small-world" structure — and his own betweenness — depends on sheer volume.
- **With / without collective nodes** ("sons of …", ʿApiru).
- **Replication target:** Cline & Cline CC = 0.391 (≈48.75× random) and Rib-Hadda top betweenness as explicit benchmarks; document every definitional difference that moves the numbers.

---

## 8. Publication and Community Strategy
- **Data paper:** *Journal of Open Humanities Data* (JOHD) — publish the derived actor registry + edge lists + code (the reusable asset). Precedent: eBL/CDLI data papers in JOHD.
- **Methods/results article:** *Journal of Historical Network Research* (JHNR) — fully open access, **no APC**, DOAJ-listed, explicitly welcoming Bronze-Age-to-contemporary network work (Vol. 4, 2020 was on ancient politics). Best primary target for fit and openness.
- **Field-facing venue:** *Journal of Ancient Near Eastern History* (JANEH, De Gruyter; double-blind, methodologically minded) or *Digital Scholarship in the Humanities* (DSH, OUP) for a DH-forward framing.
- **Conferences:** the Historical Network Research conference; CAA (Computer Applications and Quantitative Methods in Archaeology); the Rencontre Assyriologique Internationale (RAI) for field credibility; and a DH conference (ADHO) for methods.
- **Preprint norms:** post to a preprint/repository (Humanities Commons / SocArXiv / arXiv cs.SI) — standard in DH/network science, tolerated (if less established) in Assyriology.
- **Assyriologist co-author:** approach **Jacob Lauinger** and/or **Tyler Yoder** (the Oracc Amarna editors — their data is CC-BY-SA and their print edition, *The Amarna Letters: The Syro-Levantine Correspondence*, appeared with Lockwood Press in 2025; they explicitly aim to serve scholars and reusers). They are the natural collaborators and the people who most benefit from a rigorous reuse of their corpus; note the wider AEMW umbrella is directed by Lauinger and Matthew Rutz (Brown). Also relevant: **Jana Mynářová** (Amarna diplomatics/formulae; co-editor of the very volume Cline & Cline published in) and the **Na'aman/Rainey school**. A co-author supplies philological authority for the hand-coding and smooths reception.
- **Data/code release:** GitHub (code, MIT/BSD) + Zenodo (archival DOI; CC-BY for derived data). Respect Oracc's **CC-BY-SA** on any redistributed corpus text — keep the derived network tables separate and clearly licensed, and cite Oracc / Izre'el / Lauinger–Yoder explicitly.

---

## 9. Risks and Limitations
- **Archive bias (structural — modelable, not removable):** the correspondence graph is an ego-network of Egypt, found in Egypt; centrality there measures salience-to-Egypt. Over-reading Rib-Hadda's (or anyone's) betweenness as raw historical importance is the single biggest interpretive trap — and Cline & Cline's own note that his score derives from mentions inside his 60-letter dossier is the warning sign. Mitigation: §4.3, and lead with the mention/conflict networks.
- **Small-n inference:** ~100–400 nodes; ERGMs may be unstable; all estimates carry wide uncertainty. Mitigation: multiple model families (ERGM / latent / SBM / QAP), Bayesian uncertainty, and honest interval reporting.
- **Chronological uncertainty:** dating is only relative; treat time as ordinal phases and never over-claim temporal dynamics.
- **Entity ambiguity:** variant spellings, title-only officials, collective actors, "the king." Mitigation: Oracc lemma-ID backbone + a transparent `canonical_registry.csv` + sensitivity runs.
- **Great-Power letters not yet lemmatized:** hand-coding EA 1–44 introduces a small heterogeneous-source seam; document it and re-fold the Oracc data when the final release drops.
- **Provenance data is book-bound:** the Goren et al. tables must be hand-transcribed; double-key and spot-check.
- **Scholarly-reception risk for an outsider:** entering Assyriology from software/statistics invites skepticism about philological competence. Mitigation: (a) an Assyriologist co-author, (b) validate everything against Moran/Rainey, (c) foreground methodological humility and the bias-modeling contribution rather than "correcting" domain experts, and (d) release fully reproducible code+data so every claim is checkable.

---

*Prepared 31 July 2026. Resource statuses were verified against live sources on that date; the corpus size (305 texts) and the absence of structured sender/addressee catalogue fields were confirmed directly. The Great-Power release date is not announced ("final update," undated) — re-check the Oracc project page before Phase 4. Where secondary counts conflict (e.g. Rib-Hadda's dossier at 60 vs. ~64–70 letters), the plan carries both and treats the discrepancy as a robustness parameter rather than silently choosing one.*