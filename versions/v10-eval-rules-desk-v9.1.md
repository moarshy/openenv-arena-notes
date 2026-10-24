# v10: Eval-rules desk v9.1 (daily-improvement track)

| | |
|---|---|
| Submission ID | `eval-rules-desk-v2`, submitted 2026-10-24 08:50 (+08), HTTP 202 |
| Image | `ghcr.io/moarshy/workbench@sha256:1ac8bdb9…30a1` |
| Dataset | `arshy/eval-rules-desk` (v9.1 revision) |
| Arena result | pending |

**Track:** after the 5-run v9 test (mean 3.0 vs field 2.96), the user chose to improve v9 a little each day and submit daily. The aim is the leaderboard row (currently 6/40), using each run's per-task training curves as the gauge. There are no pass/fail rules.

**Change from v9:**
- Finance and office tasks were flat in v9 training (about 0.1). v9.1 adds smaller levels: **loans-lite** (40 loans, short policy, one trap) and **expenses-lite** (about 80 claims, short policy), and swaps in loans-easy.
- It drops the three tasks with no reward spread in v9 training: loans-hard, expenses-easy, pyrepo-implement.
- It keeps loans-medium, expenses-medium, downtime-medium, reflow-hard, pyrepo-bug1 and repair-medium.
- The interface and reward are unchanged.

**Not calibrated:** the OpenRouter key stopped working (401). Tests and container checks all pass. This run's training curves are the first measurement of the new tasks.

**What to watch:** per-task reward for loans-lite, loans-easy and expenses-lite. Do they rise above the about-0.1 survival level?
