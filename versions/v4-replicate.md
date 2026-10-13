# v4: Workbench v2, replicate run

| | |
|---|---|
| Submission ID | `workbench-v2-rep1` |
| Submitted | 2026-10-13 20:52 (+08), sent automatically; run `a3202ff4fa12f39b098502db`, 117 steps |
| Image | `ghcr.io/moarshy/workbench:v2`, **identical** to v3 (same digest, same 11 tasks, same contract) |
| Arena result | **3/40** (Δ −1): office 2, industrial 1, **math 0** |

## Hypothesis
The hidden test is noisy: about ±2 tasks for one run, and a zero-learning null control scored 1/40 against the 4/40 reference. v3's math point (the only one among 45 runs) could be signal or luck. Rerunning the identical environment is the cleanest test:
- **math > 0 again** → evidence that the routing/optimisation family transfers. Invest in it for the next build.
- **math = 0** → likely noise. Don't chase it.

It also gives one more draw for the best-per-domain leaderboard row, which can't go down.

## Design
Unchanged from [v3](v3-workbench-v2.md).

## Result
| domain | v3 (original) | v4 (identical replicate) |
|---|---|---|
| office | 2 | 2 |
| industrial | 1 | 1 |
| math | **1** | **0** |
| total | 4 | 3 |

## Lessons
- **The math point did not replicate.** The same image, tasks and contract gave math 1 and then 0. Treat v3's math point as most likely noise, not evidence that the routing family transfers.
- **Office 2 / industrial 1 did replicate.** That fits a stable effect: our environment reliably keeps office, but keeps only one of the two industrial tasks the base model solves (the untrained reference solves 2). With n=2 it is still weak evidence.
- **The two runs' totals (4 and 3) differ by one task**, consistent with the ±2-task noise estimate.
- **Method:** replicating cost one slot and settled a question that one run could not. Do it again before investing in any single-domain "signal".
