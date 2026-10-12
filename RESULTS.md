# OpenEnv Arena: results by version

The benchmark is heldout-v2: 40 hidden tasks, 5 per domain, one attempt each. The untrained Qwen3.8-27B scores **4/40** (industrial 2, office 2).

| version | submitted | idea | tasks | steps | score | Δ | software | industrial | science | office | finance | math | security | media |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| [v1 Stepwise Math](versions/v1-stepwise-math.md) | 2026-10-10 | Exact-answer math via a calculator tool | 8 | 257 | **2/40** | −2 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 |
| [v2 Workbench](versions/v2-workbench.md) | 2026-10-11 | Workspace habits via run_bash, hidden caveats, exact output files | 9 | 104 | **3/40** | −1 | 0 | 1 | 0 | 2 | 0 | 0 | 0 | 0 |
| [v3 Workbench v2](versions/v3-workbench-v2.md) | 2026-10-12 | + code repair family, 12-action episodes, harder medium | 11 | 109 | **4/40** | 0 | 0 | 1 | 0 | 2 | 0 | **1** | 0 | 0 |

**Leaderboard row** (best per domain across our runs): office 2/5, industrial 1/5, **math 1/5**, so an average of **10%**. As of 2026-10-13, v3 is the only one of 41 scored runs with a math point.

Landscape snapshots, which cover every entrant's runs, are in [landscape/](landscape/). Refresh them with `python scripts/study_board.py`.
