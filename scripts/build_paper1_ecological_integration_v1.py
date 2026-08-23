#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path


def replace_between(text: str, start: str, end: str, replacement: str) -> str:
    i = text.index(start)
    j = text.index(end, i)
    return text[:i] + replacement.rstrip() + "\n\n" + text[j:]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args()
    t = a.input.read_text(encoding='utf-8')

    abstract = '''## ABSTRACT

### Premise of the study

Flower-colour states can be generated through multiple pigment-pathway routes, but molecular accessibility need not imply macroevolutionary lability. We asked whether molecular routes to colour are repeatable, whether wild flower colours remain phylogenetically constrained, and which ecological processes repeatedly affect reproduction.

### Methods

We combined sequence-aware synthesis of *Camellia* pigment mechanisms with a 339-locus Angiosperms353 nuclear framework, accepted taxonomy, audited wild-colour states, and phylogenetic permutations. We also synthesized study-level ecological effects for pollinator service, pollen limitation, climate/season mediation, sensory choice, and floral pigment manipulation without pooling incompatible outcomes.

### Key results

Molecular recurrence did not require one exact gene: FLS showed same-lineage recurrence, whereas independent DFR clusters used different paralog subclasses. Nearest-same-colour conservatism persisted across trait and topology sensitivities; on the UFBoot topology, *P* = 0.00116 (strict) and *P* = 0.000080 (dominant), while broad mean pairwise-distance clustering was topology-sensitive. Bird access increased fruit set 2.29–6.35-fold across three independent A, W, and Y systems (geometric mean RR = 3.53). Independent *Camellia oleifera* experiments replicated strong bird and bee service effects, and five reliability-gradient effects all matched prediction. Climate or season altered pollination conditions in five studies across four taxa, whereas direct abiotic floral-pigment evidence remained limited to one confounded experiment. No accepted-species colour-transition branch was robust to both trait scenarios.

### Conclusions

Flexible molecular implementations coexist with local phylogenetic conservatism, while reproductive-service filtering has quantitative support across *Camellia*. Public data support this ecological mechanism but cannot assign it causally to individual macroevolutionary colour transitions.'''
    t = replace_between(t, '## ABSTRACT', '**Key words:**', abstract)

    methods = '''## Ecological-driver quantitative synthesis

Ecological evidence was synthesized after the molecular and accepted-species macro analyses were frozen. We separated outcome families rather than converting pollinator exclusion, pollen supplementation, seasonal reward, sensory choice, and pigment manipulation into one omnibus effect. For proportional or mean contrasts with positive values, the preferred common magnitude was the log response ratio (lnRR). One primary effect was retained per study/species/outcome for cross-species synthesis; correlated secondary outcomes and repeated contrasts from the same study were retained as sensitivity evidence. Sampling variance was reconstructed only when raw event counts or defensible standard errors were available. Provisional standard errors inferred indirectly from published test statistics were not admitted to inverse-variance pooling.

The primary cross-species service family comprised fruit-set contrasts between full/open access and bird exclusion in three independent species. Because not all three effects had defensible sampling variances, we report an equal-weight mean lnRR, its geometric-mean RR, the observed RR range, and leave-one-study-out sensitivity rather than a conventional random-effects estimate. Repeated *C. oleifera* pollinator-service experiments were analyzed separately as within-species replication so that one species did not gain extra weight in the genus-level comparison.

Pollen limitation was treated separately from pollinator-group contribution. Exact event counts were used where available to reconstruct lnRR variance. Pollinator-reliability gradients were evaluated for directional replication but were not numerically pooled when regression coefficients were on incompatible scales. Climate/season evidence was admitted when it explicitly changed flowering-window conditions, visitor activity, reward, pollen delivery, or reproductive service; heterogeneous outcomes were triangulated by study and taxon rather than pooled. Flower-specific abiotic pigment manipulations were kept in a separate response family from leaf experiments and from macro climatic associations.

Coarse visible A/W/Y state was used only as a descriptive moderator where independent replication permitted. It was not assumed to represent a unique sensory or reproductive state. Ecological effects were not assigned to individual macroevolutionary colour-transition branches unless those branches passed the independent strict-versus-dominant trait-history robustness gate.'''
    t = replace_between(t, '## Climate and pollination screening', '## Reproducibility and manuscript-result governance', methods)

    results = '''## Ecological synthesis supports reproductive-service filtering but not a visible-hue syndrome

The quantitative ecological evidence was strongest for reproductive service and reliability. Three independent bird-access/exclusion systems could be placed on a common fruit-set response-ratio scale. Full/open access increased fruit set 6.35-fold in *C. japonica* (A), 3.04-fold in *C. petelotii* (Y), and 2.29-fold in *C. oleifera* (W). All three effects pointed in the same direction; the equal-weight geometric mean RR was **3.53**, and leave-one-study-out geometric means remained **2.64–4.39**. Because defensible sampling variances were unavailable for all three studies, this is a magnitude synthesis rather than an inverse-variance random-effects estimate. The presence of large service effects in A, W, and Y systems did not support a red-specific bird-pollination syndrome.

Independent experiments within *C. oleifera* replicated the service effect using different pollinator guilds and designs. Bird access versus bird exclusion gave RR = **2.29**, whereas *Apis cerana* introduction versus no-bee cages gave RR = **2.56**; their equal-weight geometric mean was **2.42**. A secondary open-field honey-bee contrast from the latter study gave RR = **4.31** but was not counted as an independent genus-level study. Pollinator-reliability gradients converged on the same mechanism: across five registered effects, higher legitimate-bee availability predicted greater fruit set or lower pollen limitation and greater distance from a nesting aggregation predicted lower fruit set (**5/5** in the expected direction).

Pollen limitation was context dependent rather than equivalent to pollinator-group contribution. In *C. pubipetala*, supplemental pollination increased fruit set from 4/60 to 7/30 flowers (RR = **3.50**, reconstructed SE[lnRR] = 0.586, approximate 95% RR interval 1.11–11.03). In contrast, *C. petelotii* showed no detectable open-versus-supplemental difference despite a large bird-exclusion effect. Across eight *C. oleifera* forests, pollen limitation declined as legitimate *Andrena camellia* visit density increased (reported *P* = 0.004).

Climate and season repeatedly altered the conditions under which pollination service was delivered. Five studies across four taxa contained explicit flowering-window effects on phenology, visitor activity, reward, pollen delivery, or reproduction. A cooler northward *C. hainanica* site delayed anthesis by 45 d, reduced peak visitation by 92%, reduced pollen deposition by 57%, and produced zero natural fruit set while hand cross-pollination still produced fruit. Seasonal *C. perpetua* data showed winter/summer nectar-volume and sucrose:hexose ratios of approximately 3.51 and 7.11, with stronger winter bird/reproductive weighting. *C. oleifera* studies independently linked reproductive service to pollinator availability, flowering-weather thresholds, and interannual weather dependence.

By comparison, direct abiotic evidence for petal pigment deployment remained sparse. Only one admitted flower-specific *Camellia* manipulation measured pigment response directly, and its cold treatment was confounded with darkness. Formal pooling of a direct abiotic floral-pigment response was therefore not justified. Finally, a paired same-visible-red comparison between *C. rusticana* and *C. japonica* showed an approximately **23.45-fold** difference in bumblebee visitation together with UV/fluorescence differences, demonstrating that coarse visible hue is not a unique pollinator-functional state.

The ecological synthesis therefore supports a conditional reproductive-service filter at the mechanism level. It does not resolve the macroevolutionary event level: no accepted-species colour-transition branch was robust to both strict and dominant wild-colour scenarios, so ecological effects could not be assigned causally to particular colour transitions.'''
    t = replace_between(t, '## Simple visible-colour ecological explanations were insufficient', '# DISCUSSION', results)

    discussion = '''## Ecological filtering is supported at the service level, not the branch-causal level

The ecological synthesis changes the interpretation of the cross-scale mismatch. It is no longer accurate to say only that ecological causes are untestable. Across independent *Camellia* systems, access to effective pollinators repeatedly produces large reproductive consequences, and repeated gradients within *C. oleifera* connect pollinator availability to fruit set and pollen limitation. These data provide quantitative support for reproductive-service filtering as a biologically important process. They also show why a simple visible-hue syndrome is inadequate: large bird-service effects occur in A, W, and Y flowers, while two flowers classified as similarly red can differ by more than an order of magnitude in bee choice.

Climate and season fit this model more coherently as modifiers of reproductive service than as a universal direct cause of visible colour. Flowering-window temperature and weather can shift anthesis timing, visitor activity, reward, and pollen delivery; these links recur across several taxa even though the response variables are too heterogeneous for one pooled effect. By contrast, flower-specific experiments that isolate direct abiotic control of petal pigment remain too sparse and confounded for a parallel synthesis. The present evidence therefore favors an indirect chain in which environment changes the reliability and economics of reproductive interactions, without establishing that annual climate means directly determine A/W/Y state.

A useful working model is consequently:

`molecular accessibility -> latent pigment/spectral/reward phenotype -> flowering-window environment + pollinator availability/effectiveness -> reproductive success -> evolutionary persistence`.

The first half of this chain is supported by the molecular and ecological mechanism layers, but the final macroevolutionary link remains unresolved. Accepted-species colour-history uncertainty prevents us from identifying a set of branch events that is robust enough to test whether high pollinator service or particular flowering environments caused specific colour transitions. This is an identifiability boundary, not evidence against ecological filtering. It separates a quantitatively supported mechanism/service process from an unproven macroevolutionary causal assignment.

The resulting empirical priority is sharper than simply collecting more species-level colour labels. Tests of persistence should measure effective pollination, reproductive fitness, flowering-window environment, and the full sensory/reward phenotype within naturally variable lineages. That design can ask whether the ecological filters detected here actually favor one molecularly accessible floral state over another while controlling for shared lineage background.'''
    t = replace_between(t, '## Visible hue is an observation layer, not necessarily the ecological selection target', '## Pattern without identifiable events defines the public-data boundary', discussion)

    old_conclusion = '''The resulting picture is a cross-scale mismatch between flexible generation and constrained persistence. Current public data are sufficient to detect that mismatch, but not to assign branch-specific ecological or molecular causes. The next decisive step is therefore population-resolved empirical work in naturally variable *Camellia* lineages, where sensory phenotype, pollination service, reproductive fitness, flowering-window environment, and paralog-specific pigment-pathway deployment can be measured together.'''
    new_conclusion = '''The resulting picture is a cross-scale mismatch between flexible generation and constrained persistence, now linked to a quantitatively supported ecological filter. Pollinator access and reliability repeatedly affect reproductive performance, and climate/season repeatedly alters the conditions under which that service is delivered. These effects are not restricted to one visible colour state, and coarse hue is not a unique ecological phenotype. Current public data therefore support reproductive-service filtering at the mechanism level, but they still do not identify robust accepted-species colour-transition events to which that mechanism can be assigned causally. The next decisive step is population-resolved work in naturally variable *Camellia* lineages, where sensory phenotype, pollination service, reproductive fitness, flowering-window environment, and paralog-specific pigment-pathway deployment can be measured together.'''
    if old_conclusion not in t:
        raise SystemExit('expected conclusion paragraph not found')
    t = t.replace(old_conclusion, new_conclusion)

    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(t, encoding='utf-8')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
