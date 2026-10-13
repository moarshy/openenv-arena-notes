# v4: Workbench v2, replicate run

| | |
|---|---|
| Submission ID | `workbench-v2-rep1` |
| Submitted | scheduled for 2026-10-13 20:52 (+08) |
| Image | `ghcr.io/moarshy/workbench:v2`, **identical** to v3 (same digest, same 11 tasks, same contract) |
| Arena result | pending |

## Hypothesis
The hidden test is noisy: about ±2 tasks for one run, and a zero-learning null control scored 1/40 against the 4/40 reference. v3's math point (the only one among 45 runs) could be signal or luck. Rerunning the identical environment is the cleanest test:
- **math > 0 again** → evidence that the routing/optimisation family transfers. Invest in it for the next build.
- **math = 0** → likely noise. Don't chase it.

It also gives one more draw for the best-per-domain leaderboard row, which can't go down.

## Design
Unchanged from [v3](v3-workbench-v2.md).

## Result
## Lessons
