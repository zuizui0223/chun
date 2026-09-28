# Evolution Letters v0.3 prehuman bundle — v0.1

## Purpose

Everything that can be generated before author, declaration, and archive metadata is now deterministic.

The workflow produces:

- a line-numbered 12-point Times New Roman, double-spaced DOCX manuscript generated from the frozen v0.3 science source;
- five individual vector PDF figures from the frozen figure builder;
- the cover-letter scaffold;
- the submission metadata scaffold;
- the upload manifest and readiness receipt;
- a filtered reproducibility snapshot ZIP containing all 20 frozen science assets plus submission tooling and a machine-readable checksum manifest.

## Science boundary

The frozen manuscript and all protected v0.3 science assets are read-only inputs.

The DOCX renderer may inject only the mutable metadata classes already allowed by the science-freeze governance: authors, affiliations, corresponding-author contact, CRediT roles, funding, acknowledgements, and archive DOI/version/URL.

While those fields are empty, the generated DOCX is explicitly labeled PREHUMAN in its filename and status receipt.

## Archive boundary

The reproducibility ZIP is an archive candidate, not yet a persistent archive.

It records the workflow source commit, the original science-freeze commit, each protected asset's git-blob SHA and SHA-256 digest, and all current submission tooling.

The DOI, version, and URL remain null until a persistent repository actually mints them.

## Final transition

After confirmed human metadata is entered:

1. rerun the metadata validator;
2. rerun this bundle workflow;
3. visually QA the generated DOCX;
4. deposit the reproducibility snapshot and populate DOI/version/URL;
5. rerun once more with archive metadata populated;
6. submit the resulting DOCX, five PDF figures, and finalized cover letter.

No further biological analysis is required by the current v0.3 route.
