# v7: T-Desk with a roomy budget (pre-registered)

**Status:** pre-registration, written 2026-10-16 before building or submitting.

| | |
|---|---|
| Submission ID | `tdesk-roomy-v1`, submitted 2026-10-16 20:59; run `e621699d3942100a2ff114eb`, 105 steps |
| Image | `ghcr.io/moarshy/workbench:tdesk-roomy-v1` (planned) |
| Arena result | **2/40**: industrial 1, office 1 |

## Why
v6 T-Desk scored **0/40**, at the no-update floor, even though its training reward rose. It changed three things at once compared with v5 (Workbench v3, 3/40):
1. the interface: `tbench2_env`, with the instruction repeated and output untrimmed
2. the budget: 4,096 / 8,192 tokens instead of 12,288 / 16,384
3. the tasks: budget-fit "lite" and "located" versions

v7 keeps the **tbench2 interface** and restores the **v5 budget and v5 tasks**. That isolates the interface from the budget.

## The design
| | v5 Workbench v3 | v6 T-Desk | **v7 T-Desk roomy** |
|---|---|---|---|
| Interface | run_bash/submit | tbench2 | **tbench2** (identical to v6) |
| Budget | 12,288 / 16,384 | 4,096 / 8,192 | **12,288 / 16,384** (as v5) |
| Tasks | v5 set (10) | budget-fit set (8) | **v5 set minus plant (8)**: pyrepo-bug1/bug2/implement, repair-medium/hard, reflow-hard, downtime-medium, expenses-easy |
| Reward | partial + all-pass | binary | binary (as v6: the tbench2 `evaluate`) |

`plant` is excluded because v6 calibration showed the model decoding its sealed parameters (a reward hack).

**A remaining confound.** v7 also differs from v5 in reward: binary vs partial. That is inherent to mirroring `evaluate`, and is noted rather than controlled.

## Hypotheses and predictions
- **H-budget (the tight budget is what hurt in v6):** v7 lands in the normal trained band, **2–5/40**, keeping office and/or industrial.
- **H-interface (the tbench2 interface itself doesn't transfer, or harms):** v7 lands at the no-update floor, **0–1/40**, like v6.

**Verdict rules (fixed now):**
- **≥ 2/40 → supports H-budget.** The interface alone is not harmful. v6's 0 was the budget and its side effects (overflowing episodes being dropped, budget-fit tasks).
- **≤ 1/40 → supports H-interface.** Training on the tbench2 interface doesn't transfer, whatever the budget.
- Base rates for context: no-update runs score 0–2 (mean ≈1.25), trained runs ≈2.97, and identical reruns differ by up to 2. So one run is suggestive, not conclusive. **Replicate before a firm conclusion.**

**Training-curve expectation:** with the roomy budget, offline calibration predicts 40–60% solves, so early reward should start well above v6's ≈0.1–0.2. There should be far fewer "Rollout failed" alerts.

## Calibration (before submission)
Qwen3.8-27B via OpenRouter, thinking off, **strict** one-JSON parsing, 12,288 / 16,384 budget accounting, 8 episodes per task:

| task | solved |
|---|---|
| pyrepo-bug1 | 0/8 |
| pyrepo-bug2 | 0/8 |
| pyrepo-implement | 3/8 |
| repair-medium | 1/8 |
| repair-hard | 1/8 |
| reflow-hard | 3/8 |
| downtime-medium | 2/8 |
| expenses-easy | 1/8 |
| **total** | **11/64 (17%)** |

- **The failure mode changed.** Budget exhaustion fell from about half of all episodes (v6) to 5/64. **Invalid replies ended 55/64 episodes.** Longer episodes give more chances to break format: prose before the JSON, unescaped quotes, `<tool_call>` tags.
- In past runs the arena's training reward sat well above our strict calibration (v2 about 0.6–0.8 against about 2/8 strict; v6 0.2–0.55 against about 10%). So the arena likely parses more leniently, and the real signal should exceed 17% (inference).
- **Decision:** submit without tuning, so the one-factor comparison with v5/v6 holds.
- **Added prediction:** fewer "Rollout failed" alerts than v6, and a starting training reward clearly above v6's.


## Result (2026-10-17)
**2/40** (industrial 1, office 1), 105 steps.

**Verdict against the pre-registered rules: ≥ 2/40 → supports H-budget.** The tbench2 interface with a roomy budget lands in the trained band, not at the no-update floor where v6 (tight budget) landed.

**Caveats:**
- 2 sits at the edge of both ranges: the no-update range is 0–2 and trained runs average about 3. So the evidence is weak, and the 0 vs 2 difference between v6 and v7 is within single-run noise (identical reruns differ by up to 2).
- v7 also changed the tasks back to v5's. The budget and the budget-fit tasks are not separated.

**Comparison:**
| | interface | budget | tasks | score |
|---|---|---|---|---|
| v5 | run_bash | 12k/16k | Workbench v3 | 3 |
| v6 | tbench2 | 4k/8k | budget-fit | 0 |
| v7 | tbench2 | 12k/16k | Workbench v3 − plant | 2 |

**Reading:** consistent with "the tight budget, or what it did to training (dropped overflow episodes, near-zero solve rates), is what put v6 at the floor". The tbench2 interface by itself did not help either: v7 ≤ v5. Copying the smoke-test interface is neutral at best.
