# v7: T-Desk with a roomy budget (pre-registered)

**Status:** pre-registration, written 2026-10-16 before building or submitting.

| | |
|---|---|
| Submission ID | `tdesk-roomy-v1` (planned) |
| Image | `ghcr.io/moarshy/workbench:tdesk-roomy-v1` (planned) |
| Arena result | (filled in after evaluation) |

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

## Calibration, contract, result
(filled in before submission and after evaluation)
