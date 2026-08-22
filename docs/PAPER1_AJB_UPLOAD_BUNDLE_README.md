# Paper 1 AJB upload bundle v0.4

This is the journal-facing packaging layer. It adds no biological analysis.

## Files ready for journal upload

- `manuscript/PAPER1_AJB_UPLOAD_V0_4.md` — manuscript with AJB structured abstract, Data Availability statement, and Appendix S1–S9 legends.
- `main_figures/` — Main Fig 1–6 in PNG and SVG; choose the journal-preferred production format at upload.
- `appendices/Appendix_S1.csv` through `Appendix_S6.csv` — tabular Supporting Information.
- `appendices/Appendix_S7.png` through `Appendix_S9.png` — Supporting Information figures.
- `appendices/Appendix_index.csv` — mapping from Appendix IDs to the internal frozen Table/Figure provenance.
- `provenance/` — scientific result registry, source provenance, bibliographic corrections, appendix mapping, release-component manifest, and validation summaries.
- `BUNDLE_MANIFEST.json` — SHA256 digest and byte size for every generated file.

## Only remaining submission inputs

The analysis, figures, Supporting Information, bibliography, and AJB formatting are reproducible from the repository. Before actual Editorial Manager submission, supply:

1. final author list and order;
2. affiliations and corresponding-author details;
3. author contributions;
4. funding and acknowledgments;
5. conflict-of-interest statement if required;
6. DOI for the versioned archived release, replacing `[ARCHIVE DOI TO ADD AT SUBMISSION]`.

None of these inputs requires reopening the frozen biological analysis.
