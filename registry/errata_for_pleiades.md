# Draft erratum for Pleiades

*Prepared but NOT sent. Same contact policy as `errata_for_oracc.md`.*

Checked against `pleiades-places-latest.csv` (atlantides.org bulk dump)
as downloaded for this project (see README for fetch commands).

## The erratum

**Place 991392 "Cyprus" (province): representative point is not on
Cyprus.** The dump's `reprLat`/`reprLong` are 37.5, 32.5 — inland
Anatolia near Konya, ~250 km NNW of the island. The island spans
roughly 34.5–35.7 N, 32.2–34.6 E; even under the record's stated
`rough` precision, the representative point should fall on or near it.
Found because this project used the point to locate Alašiya and the
resulting distance entered a permutation test (`distance_confounds.md`
documents the audit).

## Not errata (name collisions our own join mis-resolved)

For the record, five other bad locations in this project's early
geocoding were legitimate Pleiades records matched to the wrong
homonym, i.e. our fault, not theirs: Tyrus 697757 (Transjordanian
Tyros/ʿIraq al-Amir, not Phoenician Tyre 678437); Pella 491688
(Macedonia, not Pella/Berenice 678326); Arca 628929 (Anatolia, not
Arca/Caesarea ad Libanum 668198); Hatti 56567731 (the Iron-Age
Syro-Hittite region, not Hattusa 283602441); and "Leukosyria" 844869
(Black Sea region carrying "Assyria" as a name variant). A cautionary
list for anyone geocoding Bronze Age toponyms against classical
gazetteers.
