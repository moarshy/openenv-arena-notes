# OpenEnv Arena: results by version

The benchmark is heldout-v2: 40 hidden tasks, 5 per domain, one attempt each. The untrained Qwen3.8-27B scores **4/40** (industrial 2, office 2).

| version | submitted | idea | tasks | steps | score | Δ | software | industrial | science | office | finance | math | security | media |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| [v1 Stepwise Math](versions/v1-stepwise-math.md) | 2026-10-10 | Exact-answer math via a calculator tool | 8 | 257 | **2/40** | −2 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 |
| [v2 Workbench](versions/v2-workbench.md) | 2026-10-11 | Workspace habits via run_bash, hidden caveats, exact output files | 9 | 104 | **3/40** | −1 | 0 | 1 | 0 | 2 | 0 | 0 | 0 | 0 |
| [v3 Workbench v2](versions/v3-workbench-v2.md) | 2026-10-12 | + code repair family, 12-action episodes, harder medium | 11 | 109 | **4/40** | 0 | 0 | 1 | 0 | 2 | 0 | **1** | 0 | 0 |
| [v4 replicate of v3](versions/v4-replicate.md) | 2026-10-13 | identical image and tasks, to measure noise | 11 | 117 | **3/40** | −1 | 0 | 1 | 0 | 2 | 0 | 0 | 0 | 0 |
| [v8 Workbench v4](versions/v8-workbench-v4.md) | 2026-10-17 | **pre-registered**: loans finance family (late caveat, false premise) + protected-check reward | 9 | 108 | **3/40** | −1 | 0 | 1 | 0 | **2** | 0 | 0 | 0 | 0 |
| [v7 T-Desk roomy](versions/v7-tdesk-roomy.md) | 2026-10-16 | **pre-registered**: tbench2 interface with v5's budget and tasks | 8 | 105 | **2/40** | −2 | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0 |
| [v6 T-Desk](versions/v6-tdesk.md) | 2026-10-15 | **pre-registered**: same task families behind the organizers' tbench2_env interface and smoke budgets | 8 | 119 | **0/40** | −4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| [v5 Workbench v3](versions/v5-workbench-v3.md) | 2026-10-14 | software (real-library repair) + industrial (reflow, plant tuning) | 10 | 121 | **3/40** | −1 | 0 | **2** | 0 | 1 | 0 | 0 | 0 | 0 |

**Leaderboard row** (best per domain across our runs): office 2/5, **industrial 2/5**, math 1/5, so an average of **12.5%**. v3 had the only math point among the runs at the time, but **the identical replicate (v4) scored math 0**, so it was most likely noise.

Landscape snapshots, which cover every entrant's runs, are in [landscape/](landscape/). Refresh them with `python scripts/study_board.py`.
