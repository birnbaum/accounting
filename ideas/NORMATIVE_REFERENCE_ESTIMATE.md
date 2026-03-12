# Normative Reference Estimate

## Status

Future work. Not part of the core framework.

The primary goal of this project remains a **reconciliation framework**:

- compute an actionable, SCI-based metric on the observable boundary
- reconcile that metric to the provider-reported carbon number at the provider's reporting boundary

This document records a possible extension that should remain explicitly separate from that core goal.

## Idea

In addition to the provider-reconcilable estimate, compute a second estimate that represents a more complete or more methodologically defensible carbon account when provider methodologies appear incomplete, coarse, or faulty.

Examples:

- missing end-of-life Scope 3 treatment
- omitted Scope 3 categories
- questionable amortization logic
- coarse allocation methods that are known to distort incentives
- provider-specific methodological flaws

This should not be framed as "the one true number." A better name is:

- **normative reference estimate**

Alternatives:

- **full-boundary estimate**
- **best-available estimate**

Avoid "gold standard," which overclaims.

## Why It Could Be Useful

The value of a normative reference estimate would be comparative, not substitutive.

It could make visible:

- the gap between what providers report and what a more complete methodology would report
- which omissions or modeling choices matter most
- where provider methodologies undercount or misallocate emissions
- where users are prevented from seeing the real effect of their actions

That comparison could increase pressure on providers to improve disclosure, allocation logic, and Scope 3 coverage.

## Why It Should Stay Separate

This project is strongest when it makes a disciplined claim:

- "here is how to reconcile an actionable signal to the number providers actually report"

The normative-reference idea is a different claim:

- "here is how provider reporting differs from a more complete or more defensible accounting model"

That second claim is valuable, but it introduces a different burden:

- justify the normative baseline
- justify category inclusion and exclusion
- justify any corrections to provider methodology
- distinguish measured quantities from modeled quantities

If mixed into the core framework too early, it risks blurring the main thesis.

## Clean Separation

If implemented in the future, the framework should present three distinct views:

1. **Action metric**: SCI-based signal on the observable boundary
2. **Provider-reconcilable estimate**: estimate aligned to provider reporting
3. **Normative reference estimate**: best-available full-boundary estimate

The most interesting derived quantity would be:

$$\text{provider methodology gap} = \text{normative reference estimate} - \text{provider-reconcilable estimate}$$

That gap could be decomposed into:

- omitted categories
- faulty lifetime treatment
- coarse temporal resolution
- coarse allocation logic
- undisclosed or weakly justified assumptions

## Open Questions

Before pursuing this extension, answer:

1. What normative baseline is being claimed: GHG Protocol minimum compliance, best-available lifecycle accounting, or something else?
2. Is the normative reference still restricted to location-based accounting, or does it widen the scope?
3. Which corrections are principle-based versus provider-specific critiques?
4. How much of the estimate is measured, and how much is modeled?
5. How should uncertainty be communicated when the normative estimate is less auditable than the provider estimate?

## Current Position

Keep this idea documented, but out of the core README and out of the primary system definition for now.

The project should remain primarily a reconciliation framework, with the normative reference estimate considered a possible later comparative layer or methodology-audit layer.
