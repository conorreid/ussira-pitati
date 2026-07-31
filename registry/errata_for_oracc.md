# Draft errata report for the Oracc aemw/amarna editors

*Prepared but NOT sent. Contact decision pending project completion per
project policy. Recipients would be the Amarna sub-project editors:
Jacob Lauinger (Johns Hopkins) and Tyler Yoder; AEMW umbrella directed
by Lauinger and Matthew Rutz (Brown).*

Catalogue snapshot examined: `aemw-amarna.zip`, UTC-timestamp 2024-07-05.

## Certain errors (both Moran 1992 and Rainey 2015 agree)

1. **EA 62 (P271123), `recipient`.** Catalogue: "[An Egyptian pharaoh]".
   The letter is addressed to the commissioner Paḫanate: Moran p. 133
   "[To P]ahanate, [my l]or[d: Message of ʿAbd]i-Aširti"; Rainey p. 437
   "[To] Paḥa(m)nate, my lord". The tablet's own lemmatized formula in
   the corpus file also carries the PN.

2. **EA 301 (P271008), `ancient_author`.** Catalogue: "Yapahu, mayor of
   Gazru". The letter is from Šubandu: Moran "Message of Suban[d]u, your
   servant" (with his note grouping EA 301–306 as Šubandu's); Rainey
   p. 1169 "the message of Shubandu, your servant". The corpus file's
   own address formula reads Šubandu.

3. **EA 007 (catalogue entry), `recipient`.** Catalogue: "Babylon". The
   letter is from Burna-Buriaš to the Egyptian king: Rainey p. 97
   restores "[Speak to Napḫu]rureia, the great king, the king of the
   land of Eg[ypt]".

## Contested attributions the catalogue may wish to flag

4. **EA 169 (P271104), `recipient`.** Catalogue: "Tutu, an Egyptian
   official". Moran (n.1) argues the addressee "must be another high
   Egyptian official" (Tutu being addressed only in the body); Rainey
   restores "[To the king(?)]". Neither edition supports Tutu as
   addressee.

5. **EA 294 (P270956), `ancient_author`.** Catalogue: "Adda-danu(?),
   mayor of Gazru". Rainey's collation reads "Zimredda(!)" — agreeing
   with the corpus file's own lemmatization (Zimri-Haddu) against
   Moran's Adda-danu.

## Method note

Found by cross-validating the catalogue's structured sender/recipient
fields against the address formulae in the project's own lemmatized
corpus files (96% agreement; every disagreement adjudicated against both
print editions). Full machine-readable evidence:
`registry/adjudication_queue.csv` in this repository.
