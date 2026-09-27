# PHAIDRA abiotic moderator — transport diagnosis v0.4

## Current state

The frozen abiotic-heterogeneity moderator remains untested.

Terminal state:

HOLD_PHAIDRA_SOURCE_TRANSPORT_ENVIRONMENTAL_ROWS_UNOPENED

## What the broader source diagnostics resolved

The two previously frozen identifiers are not simply dead or malformed identifiers.

Handle API resolution succeeds for both:

- o:2098641 -> https://phaidra.univie.ac.at/o:2098641
- o:2322953 -> https://phaidra.univie.ac.at/o:2322953

The Handle API returned HTTP 200 for both identifiers.

However, following the public frontend route returns an Anubis anti-bot interstitial whose page title begins:

“Making sure you're not a bot!”

Meanwhile, the services object-info routes return HTTP 200 with empty response bodies for the target objects, and the broader alternate-metadata search found no article-relevant member PID or file metadata that can be admitted under the frozen source rule.

The diagnostic terminal state from the transport-control workflow is:

HOLD_PHAIDRA_API_RESPONSE_LAYER_NONDIAGNOSTIC_TARGET_AND_CONTROL

## Interpretation

This narrows the reason for the HOLD.

It is not evidence that the frozen PHAIDRA PIDs are invalid.

It is not evidence against an abiotic heterogeneity effect.

It is a public transport/response-layer access limitation: CHUN cannot currently obtain source identity/member metadata or environmental rows through an auditable automated route.

## Firewall

Still unopened:

- environmental data rows;
- clade abiotic heterogeneity;
- matched-species fractions;
- memory-moderator fit.

A fresh GBIF reconstruction remains forbidden under the frozen moderator contract.

Frozen Evolution Letters v0.3 and Camellia Paper 1 remain unchanged.
