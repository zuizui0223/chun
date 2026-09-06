# Petunieae historical-event topology gate — v0.2

## Current decision

Petunieae remains **ADMITTED_PENDING_EVENT_MAPPING**. Source-level evidence for repeated pigment transitions is strong, but no transition is yet counted as an independent atlas event.

The reason is now explicit: recent phylogenomics shows substantial tree discordance, incomplete lineage sorting and hybridization in the *Petunia–Calibrachoa–Fabiana* (PCF) radiation. Historical pigment events must therefore survive a topology/reticulation gate rather than being read from one convenient species tree.

## Pinned external source

Topology and network sensitivity files are pinned to:

- repository: `pedrohpezzi/Petunia-Calibrachoa-Fabiana_TreeDiscordance`;
- external commit: `0b33d5e992c39e191393bc0b86671c5c6a378e1e`;
- publication: Pezzi et al. 2024, DOI `10.1016/j.ympev.2024.108136`.

Exact paths/blob SHAs are frozen in `data/petunieae_topology_sensitivity_manifest_v0_2.csv`.

## Species-tree sensitivities

### ASTRAL

Use the species-assigned ASTRAL topology as the primary PCF coalescent-tree sensitivity:

`Data/ASTRAL/SpeciesAssigned/ASTRAL_SpeciesAssigned_pp_scored.treefile`

This is a species-level tree and may be used directly for trait-event remapping after the pigment-state taxon crosswalk is frozen.

### SVDQuartets

Use `Data/SVDQuartets/svdq_pfc.tre` as the second species-level tree sensitivity. It is methodologically distinct from ASTRAL and supplies a direct species-tip topology without requiring post-hoc collapse of replicate individuals.

### IQ-TREE

The published supermatrix consensus tree retains individual samples. It is preserved as an additional discordance diagnostic but **must not** be used directly for species-level trait-event mapping. Any later species collapse must be a separately versioned deterministic transformation performed without looking at pigment-event results.

## Reticulation sensitivity

The SNaQ analysis provides a frozen 19-species subset (`Data/SNaQ/speciesmap.txt`) and selected network files for hmax = 0 through 5.

All h values are retained. The atlas does **not** choose one h after inspecting flower-colour or pigment transitions.

`data/petunieae_snaq_likelihood_series_v0_2.csv` freezes the source values exactly as reported. The source column is named `loglik`; this gate does not reinterpret its sign/direction and does not use it to tune a trait result.

An important source diagnostic is retained explicitly: `net2.tree` and `net3.tree` are the same blob in the pinned repository commit. Increasing hmax therefore does not guarantee a different selected network topology.

## Two spatial scopes

### Full 60-taxon Petunieae scope

Wheeler et al. 2023 inferred pigment transitions on a 60-taxon tree (59 Petunieae + *Browallia*). The exact updated 60-taxon tree and terminal pigment table still need to be ingested under Issue #168 before atlas event remapping can begin.

Events involving taxa outside the PCF sensitivity dataset cannot receive network-robust status from the Pezzi et al. data.

### PCF topology/network scope

The 2024 phylogenomic study provides broad species-tree sensitivity across Petunia, Calibrachoa and Fabiana plus outgroups. The SNaQ network sensitivity is narrower: exactly the 19 species listed by the frozen species map.

The event gate must therefore track whether every descendant/endpoint taxon used to define an event is represented in the relevant sensitivity scope.

## Event confidence classes

### `NETWORK_ROBUST_PCF`

Reserved for an event that:

1. is fully represented in the frozen 19-species SNaQ subset;
2. is recovered under both species-level ASTRAL and SVDQuartets remappings;
3. retains the same source/target pigment-state interpretation under all prespecified trait-state resolutions;
4. is not contradicted by the full h=0..5 SNaQ network sensitivity under a prespecified network-to-event projection rule.

No event currently has this status; the projection rule is not yet implemented.

### `TREE_ROBUST_PCF`

An event survives the ASTRAL/SVDQuartets species-tree sensitivity and trait-state resolution sensitivity but is not fully testable across the SNaQ 19-species subset.

This is weaker than network-robust evidence.

### `FULL_CLADE_PROVISIONAL`

An event is inferred on the 60-taxon Petunieae source tree but lacks a matched independent topology/network sensitivity. Such events may be described as source-supported transitions but cannot enter the strongest cross-clade historical-recurrence estimator.

### `UNRESOLVED_EVENT`

Any event whose branch/direction/state identity changes across the prespecified tree or trait-state sensitivities.

## Promotion gate

A Petunieae historical recurrence estimate may be promoted only if:

- the 60-taxon terminal pigment table and source tree are ingested with exact taxon crosswalk;
- at least two trait-state resolutions are frozen before event overlap is inspected;
- >=3 independent transition events survive at least `TREE_ROBUST_PCF` or an equivalent full-clade two-topology gate;
- the recurrence estimator reports confidence class per event rather than mixing provisional and robust events;
- no SNaQ h value is selected based on the pigment result.

If fewer than three events survive, Petunieae remains a dense molecular-accessibility benchmark rather than an event-level recurrence anchor.

## Biological consequence

This topology gate is itself informative. Petunieae is an external test of the same distinction exposed by Camellia:

`repeated phenotypic pattern != robust identity of the historical events that generated it`.

If the repeated pigment-transition signal survives despite documented ILS and reticulation, the cross-clade recurrence argument becomes much stronger. If it contracts, that contraction is a result rather than a failure.

## Paper-1 boundary

This is post-Paper-1 atlas development only. Camellia Paper 1 science v0.2.2, framing v0.3.4 and AJB v1.0 remain unchanged.
