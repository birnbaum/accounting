Verify that a specific claim in the paper is supported by a primary source in `references/`.

Argument: the claim to verify, e.g. `/verify-claim Bashir says tSCI re-inherits the sunk-carbon bug`

## Steps

1. **Restate** the claim in one sentence. Identify the cited author/doc.
2. **Locate the source file** — do NOT use memory or working-doc summaries:
   - Taxonomy / metric claims → `references/SCI_SUNK_CARBON.md` first, then `references/sources/bashir-2024-sunk-carbon/bashir-2024-sunk-carbon.tex`
   - Provider methodology claims → `references/carbon_accounting_methodologies/<provider>/README.md`, then the `.txt` companion of the relevant PDF
   - Standard / GHG Protocol claims → grep the relevant `references/sources/ghg-protocol-*.txt`
   - Other academic priors → use the `.txt` companion (e.g. `greensku-isca-2024.txt`, `accountable-carbon-footprints-serverless.txt`)
3. **Grep** the `.txt` companion (or `.tex` source) for a key term from the claim. Use `grep -n` to get line numbers.
4. **Read a narrow window** around the matching lines (`Read offset=… limit=30`). Quote the exact passage.
5. **Assess**:
   - If the passage supports the claim → output: `VERIFIED: "<quoted passage>" (§X / p.Y of <source>)`. Propose the cite string for `paper.tex` and bib key for `references.bib`.
   - If the passage contradicts the claim → output: `CONFLICT: draft says "…", source says "…". Do not write the claim until the user resolves this.`
   - If no supporting passage found → output: `NOT FOUND in <source>. Do not write this claim. Ask the user to point to the correct source or add a missing reference.`
6. **Living-file check**: should this finding update `references/terminology.md` or a provider README? If yes, do it in the same turn.

## Hard constraints

- Never skip to step 5 using memory. Always run the grep.
- `.txt` companions are the primary search target; only open the PDF if the text extraction clearly missed the relevant passage (figures, tables).
- If the source file does not exist in `references/`, stop at step 2 and ask the user to add it.
