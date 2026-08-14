# *Cirsium* visible-colour history gate

## Question

Can the East Asian *Cirsium* comparison already tell us whether the Ryukyu bluish-purple state is ancestral retention, a gain/recruitment from a white ancestor, or true anthocyanin reactivation?

**Not yet.** The 2026 nuclear phylogeny is strong enough to define the candidate transitions, but not strong enough by itself to assign a molecular `reactivation` label.

The immediate purpose of this gate is therefore to freeze only what the published phylogeny and directly documented corolla states support, while preventing the later analysis from silently collapsing polymorphic taxa or inventing branch lengths.

## 1. Published nuclear topology constraints

Chang et al. (2026; DOI `10.1186/s12870-026-08097-6`) reconstructed an ASTRAL tree from 2,999 orthologous-gene trees. The relationships relevant to colour evolution are stored in `data/cirsium_published_topology_constraints_v0_1.csv`.

The robust taxon-level scaffold is:

```text
Sinocirsium
├── C. japonicum var. japonicum  [basal lineage in the complex]
└── Taiwanese clade
    ├── (var. albescens, var. takaoense)
    └── (var. australe, var. fukienense)

Arenicola
├── C. brevicaule
└── C. irumtiense
```

At the deeper level, Arenicola and Nipponocirsium form a clade sister to Sinocirsium.

This is a **constraint representation**, not a substitute Newick tree. The current repository has not recovered a machine-readable tree with the published branch lengths and full sample-level topology. No ancestral-state likelihood is allowed to invent equal branch lengths and then report that as a published result.

## 2. Directly documented visible-colour states

`data/cirsium_visible_colour_states_v0_1.csv` keeps visible phenotype separate from pigment chemistry.

The focal states supported directly by the 2026 treatment are:

- *C. brevicaule*: white;
- *C. irumtiense*: bluish-purple;
- var. *albescens*: white;
- var. *takaoense*: white **and** bluish-purple morphs;
- var. *australe*: bluish-purple;
- var. *fukienense*: bluish-purple to lighter purple, with rare pale-purple forms reported from Penghu.

No one of these visible states is automatically converted to `anthocyanin detected`, `anthocyanin absent`, or a pathway-mechanism state.

## 3. Why the current topology already changes the reactivation question

There are at least two independent comparative contexts rather than one simple white-versus-purple contrast.

### Ryukyu Arenicola contrast

```text
C. brevicaule       white
        ↘
         focal split
        ↗
C. irumtiense       bluish-purple
```

With two terminal states alone, the direction is not identifiable. The possibilities remain:

1. coloured ancestor -> white suppression/loss in *C. brevicaule*;
2. white ancestor -> coloured recruitment in *C. irumtiense*;
3. ancestral polymorphism followed by differential fixation;
4. active pigment -> suppressed white state -> later reactivation, but only if a broader topology places a white internal interval before the *C. irumtiense* coloured state.

The fourth hypothesis cannot be inferred from the sister pair alone.

### Taiwanese Sinocirsium contrast

The pattern is more informative:

```text
              ┌─ var. albescens     white
          ┌───┤
          │   └─ var. takaoense     white + bluish-purple
Taiwan ───┤
          │   ┌─ var. australe      bluish-purple
          └───┤
              └─ var. fukienense    bluish-/pale-purple
```

This creates a natural test of whether:

- the ancestor of the Taiwanese four-variety clade was coloured and the `albescens + takaoense` side experienced white suppression/loss;
- the ancestor was white/low-pigment and the `australe + fukienense` side recruited/retained anthocyanin deployment;
- the ancestor was polymorphic;
- introgression or incomplete lineage sorting decoupled the colour locus from the dominant nuclear species history.

The last alternative matters because Neighbor-Net and DensiTree show substantial reticulation and the paper explicitly notes colour/phylogeny mismatches.

## 4. Polymorphism is an analysis unit, not noise

The strongest immediate clue is var. *takaoense*: white and bluish-purple morphs occur within one named lineage, and the two morphs show little structural divergence in the measured morphology.

But the published study also reports weak and variable internal support for var. *takaoense*. Therefore:

- do not code the taxon as simply `white` because its traditional diagnosis was white;
- do not code it as simply `purple` because purple individuals exist;
- do not split W and BP into fixed sister tips unless the sequence-sample-to-colour-morph mapping and sample-level tree are recovered;
- do preserve `W/BP` as an explicit polymorphic state for models that can handle polymorphism.

This is exactly the type of case in which a regulatory switch, introgressed colour allele, or segregating ancestral polymorphism can produce repeated visible states without taxonomic divergence.

## 5. Minimum analyses before an ancestral visible-colour result is admitted

### Gate C1 — recover a real tree

One of the following is required:

1. author-supplied/supplementary Newick/Nexus tree matching Fig. 1; or
2. an independently reproduced public-data nuclear tree from the admitted sequence inputs; or
3. a digitised published topology with branch-length uncertainty explicitly treated as unknown and all results repeated across a justified branch-length sensitivity set.

Option 3 can support a sensitivity analysis, not a claim that the exact published ancestral state was reproduced.

### Gate C2 — freeze sample-level colour provenance

For var. *takaoense*, recover which sequenced individuals are `(W)` and `(BP)` in Fig. 1 / supplementary voucher metadata. For var. *fukienense*, record whether the sequenced Penghu individuals correspond to ordinary bluish-purple or rare pale-purple flowers where evidence exists.

### Gate C3 — use multiple phenotype models

At minimum compare:

- binary `white/low-colour` versus `coloured`;
- multistate `white`, `bluish-purple`, `pale-purple`, `polymorphic` where model support allows;
- polymorphism-aware or sample-level models rather than forcing a taxon consensus.

The binary model is only a broad phenotype history, not a pigment-mechanism model.

### Gate C4 — tree/reticulation sensitivity

Repeat ancestral-state inference across:

- the main ASTRAL topology;
- the alternative ASTRAL/species-delimitation topology where relevant;
- Bayesian/DensiTree-supported alternatives for unstable within-variety relationships;
- analyses that exclude or collapse unresolved reticulate/polymorphic units.

A direction that changes under those alternatives is reported as unresolved.

## 6. Molecular claim ladder

After a visible-colour history is reconstructed:

### Level V — visible transition

Example: `white -> coloured candidate`.

No pigment mechanism is claimed.

### Level C — coding-capacity retention

White lineage retains intact orthologs of anthocyanin structural machinery such as `DFR` and `ANS`.

This can reject a simple irreversible structural-gene-loss model, but does not show that the pathway is active in petals.

### Level E — expression/chemistry transition

Petal chemistry and/or petal expression shows anthocyanin deployment differs between states.

Now a regulatory recruitment/suppression hypothesis is supported.

### Level R — true reactivation

A broader phylogeny supports ancestral floral activity -> suppressed/absent floral deployment -> later floral activity **and** molecular evidence indicates that the pathway remained available across the suppressed interval.

Only Level R is labelled `reactivation`.

## 7. Immediate consequence

The strongest current conclusion is not that *C. irumtiense* has already been shown to re-express anthocyanin.

It is:

> East Asian *Cirsium* contains repeated and phylogenetically non-trivial white/coloured contrasts, including an especially informative within-lineage colour polymorphism in var. *takaoense*. The published nuclear scaffold is sufficient to define competing transition hypotheses, but the direction of the Ryukyu colour change and a true anthocyanin-reactivation history remain unresolved until a branch-length-aware tree and molecular pigment evidence are connected.

That unresolved state is the target of the next analysis rather than a weakness to hide.