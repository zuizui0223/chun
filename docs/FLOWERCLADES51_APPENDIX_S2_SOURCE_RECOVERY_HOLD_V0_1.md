# Flower-clades-51 Appendix S2 recovery — source HOLD v0.1

## Target

The temporal-lability bridge requires exact clade-level mean flower-color transition counts reported in Sinnott-Armstrong et al. (2026), Appendix S2.

The publisher page identifies the target supplement exactly as:

`ajb270146-sup-0002-AJB_SinnottArmstrong_D_24_00358_AppendixS2_ce.docx`

and describes it as the correlation between numbers of flower- and fruit-color transitions across clades.

## Recovery attempt

A source-only runner was written and tested before any CHUN outcome fit. It:

- validates actual Word DOCX bytes rather than trusting HTTP status;
- parses Word table XML only after valid DOCX recovery;
- probes the exact Wiley supplement download route and article-discovered links;
- does not select, transform, or fit any clade transition value.

GitHub Actions completed the recovery workflow successfully, but all Wiley article and supplement routes returned HTTP 403. No DOCX bytes were recovered.

## Decision

`HOLD_SOURCE_LABILITY_VALUE_UNRESOLVED`

No clade-level transition count is extracted and the frozen temporal-lability moderator model is **not fit**.

We do not substitute:

- a new stochastic-map re-estimation;
- preprint values whose final-paper identity is not guaranteed;
- manual plot digitization;
- fruit transition counts or another predictor.

The published aggregate transition-lability result remains biological context, but cannot be promoted to a CHUN clade-level moderator under the frozen bridge contract.

This is a source-access HOLD, not a biological negative.

Camellia Paper 1 and frozen EL v0.2 remain unchanged.
