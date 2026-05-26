# paper.tex Section Map

Living file — update line ranges when sections shift.
Use this to orient before reading paper.tex; Claude should read the narrow line range, not the whole file.

| § | Title | Lines | Key references |
|---|-------|-------|----------------|
| §1 | Introduction | L54–202 | Bashir 2024, SCI.md, greensku-isca-2024.txt, accountable-carbon-footprints-serverless.txt |
| §2 | Background: SCI and the Sunk Carbon Fallacy | L314–381 | SCI.md, SCI_SUNK_CARBON.md, sources/bashir-2024-sunk-carbon/bashir-2024-sunk-carbon.tex |
| §3 | State of the Art in Cloud Carbon Accounting | L382–546 | cross_provider_synthesis.md, all carbon_accounting_methodologies/<provider>/README.md, terminology.md |
| §4 | rSCI: Reconciling Bottom-Up and Top-Down | L547–789 | SHARMA_2024_SHAPLEY.md, BOAVIZTAPI_2024.md, CINERGY_2025.md |
| §5 | rSCI in Practice: Why It Cannot Be Computed Today | L790–915 | provider READMEs (gaps), terminology.md |
| §6 | Closing the Gap: A Call to Action | L916–954 | cross_provider_synthesis.md §5 |
| §7 | Future Work | L955–1025 | TODO: Acun 2023, Radovanović, Wiesner et al. (self-citations — not yet in references/) |
| §8 | Conclusion | L1026–1040 | — |
| App A | Cloud provider survey universe (47 providers) | L1042–end | carbon_accounting_methodologies/README.md + tier-b-c-providers.md |

## Subsection landmarks (§4)

| Subsection | Lines |
|------------|-------|
| Weight families: the residual as a design surface | L595– |


I am manually verifying the appendix table at the moment. few things to clarify, answer each independently:
- I think we should include Railway (PaaS)
- Heroku seems to be sunset? I'm not sure how we should handle the Sailsforce / Heroku split? If we include Saildforce, why not include e.g. Snowflake or Databricks? Should we include DigitalOcean somewhere? How about Encore Cloud? I'm VERY uncertain at the moment on where to do a good cutoff on who to include and who not.
- Shouldn't "Operational metrics only" be Tier C? I mean you can claim a lot 
- Check out https://www.together.ai/blog/together-crusoe-reduce-carbon-impact-of-generative-ai
- I cannot find any sustainability claims for lambda.ai or Hyperstack
- VERIFY ALL LINKS! I ASKED YOU TO DO THIS 5 TIMES NOW AND THERE ARE STILL ERRORS! DataCrunch DOES NOT EXIST ANY MORE; THEY ARE CALLED Verda. I think they beling in "Marketing claims" based on https://verda.com/? Where are they located?
- Where on https://coreweave.com/about-us (or anywhere else) are sustainability claims for coreweave?
- Where is crusoe's GHG report? the provided link seem to be marketing claims!
- Cloudflare seems to have nice reports (not sure if official or self-reported) but where did you find out about their customer-facing tool?
- Akamai is nice, but better link https://akamaisustainability.com/circularity/customer-engagement/
The top hyperscaler, regional, and green providers I still have to verify, but you can already start answering these :) 