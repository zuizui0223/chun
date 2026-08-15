# Direct Camellia thermal-niche screen v0.1

## Status

This is a **taxon-audited, species-level preliminary analysis** using public GBIF occurrences and CHELSA v2.1 (1981–2010) BIO1 and BIO6. It is independent of the literature-directional synthesis and was run specifically to test the simple macro hypothesis that anthocyanin-like red floral states occupy colder niches than yellow states.

Authoritative frozen outputs:

- `data/camellia_chelsa_thermal_species_v0_1.csv`
- `data/camellia_chelsa_thermal_tests_v0_1.csv`
- `data/camellia_japonica_rusticana_thermal_pair_v0_1.csv`
- workflow `Camellia GBIF CHELSA thermal niche`

## 1. Admission and taxonomic audit

Twelve pre-declared wild taxa were screened. GBIF occurrences were restricted to pre-declared native countries, explicit cultivated/non-native records and high-uncertainty coordinates were removed, points were thinned spatially, and a minimum of five climate-bearing points was required.

A requested species had to resolve at **species rank** in the GBIF species matcher. Synonym matches were allowed; higher-rank matches were rejected.

This gate caught a consequential error in the first run: `Camellia perpetua` resolved to genus `Camellia` rather than the species. Those genus-wide records were removed before the frozen analysis.

After the taxonomic and occurrence gates, four species were admissible:

- anthocyanin-like red (`A`): *C. japonica*, *C. rusticana*;
- yellow (`Y`): *C. nitidissima*, *C. petelotii*.

The remaining seeded species had too few defensible GBIF points or failed species-rank matching. No white species passed the five-point threshold, so the current direct analysis cannot test `W` as a climatic regime.

## 2. Direct A-versus-Y thermal result

### Mean annual temperature (BIO1 median by species)

- A species mean: **13.10 °C**
- Y species mean: **19.95 °C**
- A − Y: **−6.85 °C**
- exact two-sided species-label permutation: **P = 0.3333**
- one-sided test for A colder than Y: **P = 0.1667**

### Minimum temperature of the coldest month (BIO6 median)

- A species mean: **−2.675 °C**
- Y species mean: **6.25 °C**
- A − Y: **−8.925 °C**
- exact two-sided: **P = 0.3333**
- one-sided A-colder: **P = 0.1667**

### Cold-tail BIO6 (species 5th percentile)

- A species mean: **−8.6925 °C**
- Y species mean: **3.13 °C**
- A − Y: **−11.8225 °C**
- exact two-sided: **P = 0.3333**
- one-sided A-colder: **P = 0.1667**

### Thermal breadth

BIO1 IQR differs little between the groups (A − Y = **−0.425 °C**, exact `P=1.0`). The preliminary signal is therefore a difference in thermal position/cold limit, not evidence for a larger thermal breadth in red species.

## 3. Interpretation of the group contrast

The observed direction is consistent with red/anthocyanin-like taxa occupying colder environments than the admitted yellow taxa. It is **not a decisive state-dependent evolutionary result** because:

1. there are only two admitted species per colour state;
2. the exact permutation space has only six assignments, so the minimum possible one-sided P-value is 1/6;
3. the A taxa are Japanese and the Y taxa are southern Chinese, producing strong geography/clade confounding;
4. the warm red *C. amplexicaulis* could not enter the test because only one defensible GBIF point remained after cultivation filtering;
5. no white taxon passed the occurrence threshold;
6. no phylogenetic model is fitted at this sample size.

The correct result is therefore **directional but underpowered and confounded**, not evidence that anthocyanin caused cold colonisation.

## 4. Close-pair result: C. japonica versus C. rusticana

Both species are coded `A` / red, but their thermal niches differ strongly:

- BIO1 median: *C. rusticana* is **3.60 °C colder**;
- BIO6 median: *C. rusticana* is **4.55 °C colder**;
- BIO6 5th percentile: *C. rusticana* is **6.05 °C colder**.

Independent published trait data report that *C. rusticana* petals are slightly **lighter**, not darker/redder, than those of *C. japonica* while the colour spaces overlap strongly. Published ecological/phylogeographic work also supports long-term differentiation of *C. rusticana* in the snowy Japan-Sea climate.

This creates an important within-colour counterexample:

> **movement to a substantially colder niche does not require a monotonic increase in visible floral redness.**

It does not show that anthocyanin is biologically irrelevant. Both species retain a red/anthocyanin phenotype, and pigment composition was not reduced to a single quantitative anthocyanin measurement in this macro analysis. It specifically rejects the simple quantitative model `colder niche -> more visible red pigment` as a general explanation.

## 5. Combined with the previous chun macro synthesis

The literature-level conservative synthesis already gave only 2 supportive, 1 macro-null and 1 explicit counterexample unit for the proposition that stronger floral pigmentation is a universal cold/high-UV enabler (`2/4`, exact `P=1.0`).

The direct Camellia screen adds two pieces of information rather than reversing that conclusion:

1. a **suggestive state-level thermal separation** between the admitted red and yellow taxa;
2. a **strong within-red thermal separation** between *C. japonica* and *C. rusticana* without increased redness in the colder species.

These are most naturally reconciled by a conditional model: pigment states may correlate with some large-scale climatic histories, but the amount or visible category of floral pigment is not a universal climatic adaptation axis.

## 6. Revised conclusion

The current data reject a strong universal model:

> `more floral anthocyanin/redness -> colder niche -> Camellia diversification`

The surviving model is:

> **Pigment-network accessibility repeatedly generates colour states; historical geography and ecological filters determine where those states persist. Climate can be one filter, but its effect is conditional and need not scale monotonically with visible redness.**

This is the direct macro counterpart of the micro result that regulatory/flux changes are highly recurrent while macro cold-enabler evidence is much less consistent.

## 7. Why BM/OU/EB/BBM are not yet fitted to this direct dataset

The taxon-audited direct climate matrix contains only four species (two A, two Y) and no W taxon. A meaningful comparison among BM, OU, EB, BBM or multi-regime/state-dependent models would be statistically non-identifiable or dominated by parameter count and topology assumptions.

Those models remain the correct **M9 baselines**, but forcing them onto four tips would manufacture precision rather than add evidence. M9 therefore remains gated on a broader defensible species-colour table joined to a machine-readable nuclear tree.

This is a data-admission limit, not a reason to weaken the current conclusion.
