#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected exactly one source paragraph, found {n}")
    return text.replace(old, new, 1)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    args = ap.parse_args()

    text = args.source.read_text(encoding="utf-8")

    banner_old = (
        "> Draft v0.2. This manuscript is governed by `data/paper1_authoritative_results_v0_2.csv`, "
        "`data/paper1_main_figure_manifest_v0_2.csv`, and `data/paper1_reference_registry_v0_2.csv`. "
        "The v0.1 manuscript is retained as provenance and must not be patched back into the molecular framing "
        "when it conflicts with the v0.2 result hierarchy."
    )
    banner_new = (
        "> Draft v0.3 framing revision. The scientific result set remains Paper 1 v0.2. Novelty framing was "
        "revised after the 2026-08-27 high-recall prior-art audit; no biological estimate, contrast, figure input, "
        "or inferential gate is changed by this document."
    )
    text = replace_once(text, banner_old, banner_new, "governance banner")

    intro1_old = (
        "Repeated evolution is commonly used as evidence for constraint or predictability. When similar phenotypes evolve more than once, "
        "the same genes, pathways, or developmental routes may be reused because only a limited set of changes can produce a viable phenotype. "
        "Yet “the same mechanism” is not a single scale of description. Repetition can occur at an exact nucleotide, gene, paralog family, "
        "biochemical branch, multivariate pathway state, or final phenotype. A recurrent phenotype can therefore coexist with substantial "
        "mechanistic heterogeneity, and apparent mechanistic convergence can depend on which level an investigator chooses to measure "
        "(Rausher, 2008; Wessinger and Rausher, 2012)."
    )
    intro1_new = (
        "Repeated phenotypic evolution does not require exact molecular repetition. Flower-colour studies have already shown both alternative "
        "genetic architectures for similar visible states and convergence at broader biochemical or pathway levels, while work on repeated "
        "evolution more generally has shown that estimated genetic reuse can depend on how candidate mechanisms are discovered (Conte et al., "
        "2012; Ng and Smith, 2016; Larter et al., 2018; Wheeler et al., 2023). The unresolved problem addressed here is therefore narrower: "
        "when different studies have observed different subsets of a multivariate pigment system, how much mechanistic recurrence is actually "
        "identified by the published evidence, and does that conclusion persist when the same biological systems are remeasured under one "
        "outcome-independent observation protocol?"
    )
    text = replace_once(text, intro1_old, intro1_new, "introduction prior-art paragraph")

    obs_old = (
        "A second problem is observational. Molecular studies are rarely random samples of all components of a pathway. Candidate genes are "
        "chosen because prior knowledge makes them plausible, assays differ among studies, and published contrasts often emphasize the pathway "
        "expected to explain the focal visible phenotype. This does not make candidate-based work invalid; it means that the literature "
        "observation process is different from the biological process being inferred. If anthocyanin-related genes are measured more often than "
        "competing pigment branches, recurrence of anthocyanin regulation can appear stronger simply because other axes remain unobserved. A "
        "defensible test of recurrence must therefore distinguish biological repeatability from the measurement regime that makes repeatability visible."
    )
    obs_new = (
        "A second problem is observational. Estimates of repeated genetic reuse are already known to depend on discovery design; for example, "
        "candidate-gene syntheses can yield different repeatability estimates from less targeted genetic approaches (Conte et al., 2012). "
        "In flower-colour studies, candidate genes are chosen because prior knowledge makes them plausible, assays differ among studies, and "
        "published contrasts often emphasize the pathway expected to explain the focal visible phenotype. The question here is not whether "
        "candidate-based studies are valid, but whether a multivariate recurrence claim survives when the same admitted biological systems are "
        "placed under a common observation rule. If anthocyanin-related genes are measured more often than competing pigment branches, the "
        "literature-conditioned identified set can differ from the one obtained after standardized pathway-wide remeasurement."
    )
    text = replace_once(text, obs_old, obs_new, "introduction observation paragraph")

    cam_old = (
        "The genus *Camellia* is well suited to separate these quantities. It contains extensive flower-colour diversity and a growing molecular "
        "literature spanning cultivars, petal sectors, developmental series, transcriptomes, genomes, and functional studies. It also has unusually "
        "rich phylogenomic resources, but deep gene-tree discordance, rapid radiation, reticulate evolution, historical taxonomic duplication, and "
        "natural within-species colour variation complicate naive trait-history reconstruction (Wu et al., 2022; Zan et al., 2023; Zhang et al., "
        "2023; Yan et al., 2024). Fan et al. (2026) further showed broad genomic and structural-variant contributions to colour diversification. "
        "The remaining opportunity is therefore not to claim that *Camellia* has a white ancestor or that regulatory variation matters, but to ask "
        "how strongly recurrent molecular state is actually identified by the available evidence and how that compares with the realized "
        "macroevolutionary pattern."
    )
    cam_new = (
        "*Camellia* is not an unexplored molecular or macroevolutionary system. Recent work has synthesized the flavonoid, DFR/FLS, and MBW "
        "regulatory literature in detail, while genus-scale phylogenomics has already linked flower-colour diversification to structural variation "
        "and transposable-element-mediated regulatory change (Xiao et al., 2025; Fan et al., 2026). At the same time, deep gene-tree discordance, "
        "rapid radiation, reticulate evolution, historical taxonomic duplication, and natural within-species colour variation complicate naive "
        "trait-history reconstruction (Wu et al., 2022; Zan et al., 2023; Zhang et al., 2023; Yan et al., 2024). The opportunity is therefore not "
        "to provide the first molecular explanation of *Camellia* colour diversity or the first micro-to-macro reconstruction. Instead, we ask "
        "whether the strength of recurrent mechanism inferred from the existing literature survives standardized remeasurement of the same public "
        "systems, and how far any resulting molecular inference can be projected onto macroevolution once taxonomy, wild-colour coding, and "
        "nuclear-topology sensitivity are made explicit."
    )
    text = replace_once(text, cam_old, cam_new, "Camellia gap paragraph")

    questions_old = (
        "Here we used a falsification-oriented analysis with an explicit observation layer. We asked four questions. First, how incomplete and "
        "nonuniform is the published A/F/C/P mechanism matrix? Second, when the same public biological systems are remeasured with one frozen "
        "pathway-wide protocol, does whole-package mechanistic recurrence survive, or is repeatability modular? Third, after accepted-taxonomy "
        "normalization and wild-colour auditing, is visible flower colour still phylogenetically structured on independent nuclear topologies? "
        "Fourth, can individual historical transition branches be identified robustly enough to support branch-specific ecological or molecular "
        "causation? Our results reject a simple equivalence between repeated visible colour and repeated whole pigment-state package. Standardized "
        "remeasurement instead reveals transition-class-dependent modular recurrence, while the macro data identify local colour structure but not "
        "robust individual transition events."
    )
    questions_new = (
        "Here we treated observation and historical identification as explicit inferential layers rather than assuming that published molecular "
        "mechanisms and reconstructed transition branches were direct samples of biological recurrence. We first represented the literature as "
        "partially observed A/F/C/P pigment-state signatures and bounded recurrence over unresolved axes. We then remeasured the same public RNA-seq "
        "systems with one frozen candidate-free protocol. Separately, we tested whether accepted wild flower colours showed phylogenetic structure "
        "robust to independent nuclear topologies and alternative trait codings, and whether any individual transition branches survived those same "
        "coding sensitivities. This design asks not whether mechanistic heterogeneity or ancestral-state uncertainty exist in principle, but where "
        "the available *Camellia* evidence ceases to identify the stronger cross-scale claim."
    )
    text = replace_once(text, questions_old, questions_new, "introduction question paragraph")

    disc_mol_old = (
        "The central molecular result is not simply that different genes can produce similar flower colours. It is that the inferred repeatability "
        "of a multivariate pigment state changes when the observation regime is standardized on the same biological systems. Selected literature "
        "left complete A/F/C/P recurrence admissible for both red/pink gain and yellow development. Candidate-free remeasurement removed that "
        "possibility in both classes."
    )
    disc_mol_new = (
        "The molecular result should not be read as the first demonstration that similar flower colours can arise through different mechanisms; "
        "that principle is established across floral systems (Ng and Smith, 2016; Larter et al., 2018; Wheeler et al., 2023). The new empirical "
        "point is that the estimated degree of multivariate recurrence changes when the observation regime is standardized on the same *Camellia* "
        "systems. Literature-selected measurements left complete A/F/C/P recurrence admissible over broad identified sets, whereas candidate-free "
        "remeasurement contracted those sets and removed an invariant whole-package interpretation in both transition classes."
    )
    text = replace_once(text, disc_mol_old, disc_mol_new, "discussion molecular novelty paragraph")

    disc_obs_old = (
        "The comparison is not a test of whether candidate-gene papers are “right” or “wrong.” Candidate-selected studies often ask targeted "
        "biological questions and can resolve specific causal nodes more precisely than a broad module score. The candidate-free protocol asks a "
        "different question: if the same systems are measured with one outcome-independent pathway-wide representation, what multivariate recurrence "
        "remains identifiable?"
    )
    disc_obs_new = (
        "The comparison is not a test of whether candidate-gene papers are “right” or “wrong,” nor is observation-method dependence itself a new "
        "concept (Conte et al., 2012). Candidate-selected studies often ask targeted biological questions and can resolve specific causal nodes more "
        "precisely than a broad module score. The candidate-free protocol asks the narrower matched question: if the same systems are measured with "
        "one outcome-independent pathway-wide representation, what multivariate recurrence remains identifiable and how much does the identified "
        "set contract relative to literature-selected observation?"
    )
    text = replace_once(text, disc_obs_old, disc_obs_new, "discussion observation paragraph")

    disc_event_old = (
        "The macro analysis provides a second identification result. Local visible-colour structure was robust, yet no individual accepted-species "
        "transition branch survived alternative treatment of naturally variable colour states. The data therefore support a pattern without "
        "identifying the historical events that generated it."
    )
    disc_event_new = (
        "The macro analysis provides a second identification result. Uncertainty in ancestral-state reconstruction and sensitivity to model or "
        "character treatment are longstanding phylogenetic problems (Revell, 2025), so event instability is not itself a new methodological "
        "discovery. The empirical result here is the split under one predeclared robustness design: local visible-colour structure survived two "
        "independently inferred nuclear topologies and both wild-colour encodings, yet no individual accepted-species transition branch survived "
        "strict versus dominant treatment of naturally variable colour states. The data therefore support a robust pattern without identifying a "
        "comparably robust set of historical events that generated it."
    )
    text = replace_once(text, disc_event_old, disc_event_new, "discussion event-identification paragraph")

    ecology_old = (
        "The current ecological screens do not support a universal visible-colour syndrome and are deliberately secondary in v0.2. Coarse A/W/Y "
        "state does not uniquely encode ultraviolet reflectance, fluorescence, reward, morphology, flowering phenology, visitor effectiveness, or "
        "physiological pigment function. Pollination and abiotic selection remain plausible filters, but branch-specific causal assignment would "
        "require transition events that current public hard-state data do not identify (Trunschke et al., 2021; Berardi et al., 2026)."
    )
    ecology_new = (
        "The ecological value of the present result is an inferential boundary rather than a newly proposed universal colour syndrome. Pollination "
        "and abiotic effects on flower colour are established research areas, while coarse A/W/Y state does not uniquely encode ultraviolet "
        "reflectance, fluorescence, reward, morphology, flowering phenology, visitor effectiveness, or physiological pigment function (Trunschke "
        "et al., 2021; Berardi et al., 2026). These processes remain plausible filters on establishment and persistence, but branch-specific causal "
        "assignment would require transition events that current public hard-state data do not identify. Ecology therefore enters after, rather "
        "than substitutes for, the event-identity gate."
    )
    text = replace_once(text, ecology_old, ecology_new, "discussion ecology paragraph")

    additional_refs = [
        "Conte, G. L., M. E. Arnegard, C. L. Peichel, and D. Schluter. 2012. The probability of genetic parallelism and convergence in natural populations. *Proceedings of the Royal Society B: Biological Sciences* 279: 5039–5047. https://doi.org/10.1098/rspb.2012.2146",
        "Larter, M., A. Dunbar-Wallis, A. E. Berardi, and S. D. Smith. 2018. Convergent evolution at the pathway level: Predictable regulatory changes during flower color transitions. *Molecular Biology and Evolution* 35: 2159–2169. https://doi.org/10.1093/molbev/msy117",
        "Ng, J., and S. D. Smith. 2016. Widespread flower color convergence in Solanaceae via alternate biochemical pathways. *New Phytologist* 209: 407–417. https://doi.org/10.1111/nph.13576",
        "Revell, L. J. 2025. Ancestral state reconstruction of phenotypic characters. *Evolutionary Biology* 52: 1–25. https://doi.org/10.1007/s11692-025-09645-y",
        "Wheeler, L. C., A. Dunbar-Wallis, K. Schutz, and S. D. Smith. 2023. Evolutionary walks through flower colour space driven by gene expression in *Petunia* and allies (Petunieae). *Proceedings of the Royal Society B: Biological Sciences* 290: 20230275. https://doi.org/10.1098/rspb.2023.0275",
        "Xiao, H., D. Zhang, J. Li, H. Yin, L. Chen, Z. Wang, W. Liu, and F. Geng. 2025. The molecular basis underlying phenotypic diversity in *Camellia* flower coloration and the evolution of research paradigms. *Scientia Horticulturae* 353: 114474. https://doi.org/10.1016/j.scienta.2025.114474",
    ]

    lit_marker = "# LITERATURE CITED\n\n"
    if text.count(lit_marker) != 1:
        raise SystemExit("literature marker drift")
    before, refs = text.split(lit_marker, 1)
    ref_blocks = [x.strip() for x in refs.strip().split("\n\n") if x.strip()]
    existing_dois = {r.rsplit("https://doi.org/", 1)[-1].strip() for r in ref_blocks if "https://doi.org/" in r}
    for ref in additional_refs:
        doi = ref.rsplit("https://doi.org/", 1)[-1].strip()
        if doi not in existing_dois:
            ref_blocks.append(ref)
    ref_blocks.sort(key=lambda x: x.casefold())
    text = before.rstrip() + "\n\n" + lit_marker + "\n\n".join(ref_blocks) + "\n"

    required_citations = [
        "Conte et al., 2012",
        "Ng and Smith, 2016",
        "Larter et al., 2018",
        "Wheeler et al., 2023",
        "Xiao et al., 2025",
        "Revell, 2025",
    ]
    missing_citations = [x for x in required_citations if x not in text]
    if missing_citations:
        raise SystemExit(f"missing novelty-audit in-text citations: {missing_citations}")

    required_dois = [
        "10.1098/rspb.2012.2146",
        "10.1111/nph.13576",
        "10.1093/molbev/msy117",
        "10.1098/rspb.2023.0275",
        "10.1016/j.scienta.2025.114474",
        "10.1007/s11692-025-09645-y",
    ]
    missing_dois = [d for d in required_dois if d not in text]
    if missing_dois:
        raise SystemExit(f"missing novelty-audit references: {missing_dois}")

    frozen_tokens = [
        "Candidate-free remeasurement fixed exact-signature recurrence at 0.333",
        "pairwise concordance at **0.75**",
        "strict×dominant shared robust event count was therefore zero",
        "A/F/C/P = 8/4/1/3",
        "P=0.00116",
        "P=0.000080",
    ]
    lost = [x for x in frozen_tokens if x not in text]
    if lost:
        raise SystemExit(f"framing revision lost frozen science tokens: {lost}")

    forbidden_positive_priority = [
        "we provide the first pathway-level",
        "we present the first pathway-level",
        "this is the first pathway-level",
        "we provide the first micro-to-macro",
        "we present the first micro-to-macro",
        "this is the first micro-to-macro",
        "we show for the first time",
        "we demonstrate for the first time",
    ]
    retained = [x for x in forbidden_positive_priority if x.lower() in text.lower()]
    if retained:
        raise SystemExit(f"framing revision retained forbidden positive priority language: {retained}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text.rstrip() + "\n", encoding="utf-8")
    summary = {
        "document_version": "Paper 1 framing v0.3",
        "source_science_version": "Paper 1 v0.2",
        "scientific_results_changed": False,
        "novelty_audit_date": "2026-08-27",
        "new_required_references": len(additional_refs),
        "frozen_science_tokens_preserved": len(frozen_tokens),
        "status": "novelty-framed manuscript built",
    }
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
