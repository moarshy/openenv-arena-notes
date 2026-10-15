# v6: T-Desk (pre-registered experiment)

**Status:** pre-registration, written 2026-10-15 before building or submitting. The predictions below are fixed. The result will be compared against them, not reinterpreted afterwards.

| | |
|---|---|
| Submission ID | `tdesk-v1` (planned) |
| Image | `ghcr.io/moarshy/workbench:tdesk-v1` (planned) |
| Arena result | **0/40** (every domain 0): run `f22f124a548debdd4821f64b`, 119 steps, submitted 2026-10-15 20:58 |

## Why we are trying this
**Background: no environment has measurably moved the private score.** Evidence as of 2026-10-15, 68 scored runs:
- **Totals:** the untrained model's expected score is about 2.9/40, and trained runs average 2.98. rca-umb's permutation test found no entrant different from chance (p = 0.6).
- **Controls by other entrants:**
  - null control (zero learning): 1/40
  - collapse control (trained to quit early): 3/40
  - identical resubmissions: 4/2 (ruv) and 4/3 (ours)
- **Our five runs:** 2, 3, 4, 3, 3. Each design moved *which* base tasks survived (industrial vs office), never the total.

**Hypothesis H1 (interface and budget mismatch).** The private eval is likely served through OpenEnv's `tbench2_env`, as in the organizers' own smoke tests (`benchflow/arena-tb2-*`, `benchflow/openenv-smoke-fix-git`), on SkillsBench-style tasks:
- **Actions:** `exec` / `write_file` / `evaluate`.
- **Observations:** the full instruction repeated every turn, plus output that is never trimmed.
- **Budget:** 4,096 completion and 8,192 context tokens. The completion budget counts every observation after the first, so the model gets about 4–6 actions.
- **Grading:** binary pytest via `evaluate`.

Every entrant, including us, trained a different schema with looser budgets. The model may learn habits (exploration, long scripts, prose before JSON) that don't apply, or that hurt, under the real interface. Qwen3.8-27B is reported at about 73% on Terminal-Bench with its own harness, against about 10% here. That suggests the capability exists and the *harness fit* is missing.

**Test.** Keep the task content we already have (real-library repair, reflow, plant, expenses, routing). Change **only** the interface and budget, to match `tbench2_env` exactly.

## What changes vs v5 (Workbench v3)
| | v5 Workbench v3 | v6 T-Desk |
|---|---|---|
| Action schema | `{type: run_bash/submit, command, answer}` | **Identical to `Tbench2Action`:** `{action_type, command, session_id, block, wait_seconds, file_path, content}` |
| Observation | output (truncated to 3k) + steps_left | **Identical to `Tbench2Observation`:** instruction repeated every turn, untrimmed output, success/error |
| Budget | completion 12,288 / context 16,384, 14 calls | **completion 4,096 / context 8,192, 32 calls** (the organizers' smoke values) |
| End of episode | `submit` → our checks | **`evaluate`** → checks; `finish_action` = evaluate |
| Reward | 0.5·share + 0.5·all-pass | **Binary:** 1 only if every check passes |
| Instructions | Long, 300–600 words | **Short**, because they repeat every turn |
| Tasks | 10 (5 software, 4 industrial, 1 office) | 10: software 3, industrial 3, office 2, math 2 (planned) |
| Sandbox | setuid to `agent` | setuid, **falling back to the server user** if the arena blocks user switching |

## Pre-registered predictions
**If H1 is true** (interface mismatch was the barrier):
1. The **total is ≥ 5/40**. Base rate: 5 or more in about 5 of 68 runs (≈ 7%) by chance.
2. **Office stays at 2** (base rate ≈ 49% of runs).
3. **Software ≥ 1 or math ≥ 1.** Base rates: software about 22–29% of runs, math 1 of 68.
4. **Training curves:** early reward is *lower* than v5's (the tight budget makes episodes fail), then rises. Mean completion length falls. `frac_reward_zero_std` stays below about 0.6.

**Verdict rules (fixed now):**
- **Supports H1:** total ≥ 5 **and** (software ≥ 1 or math ≥ 1). The chance of this by luck alone is small, roughly ≤ 5%.
- **Against H1:** total ≤ 3, or the training reward rises while the score stays in the usual 2–4 band.
- **Inconclusive:** total = 4, or the success rule met with weak training curves. Replicate before drawing conclusions.
- **Any positive result is replicated** (identical resubmission) before we claim an effect, as we did for the v3 math point.

**What we will compare:** this run against v1–v5 (mean 3.0) and the field (mean 2.98), domain by domain, plus the training curves against v5's.

## Amendment 1 (2026-10-15, before submission): budget-fit tasks
Written after the first calibration and before any arena result. The predictions and verdict rules above are unchanged.

**What calibration found.** Calibration used Qwen3.8-27B via OpenRouter, thinking off, **strict** one-JSON parsing, and the arena's budget rules: completion 4,096 counting replies plus every observation after the first, and context 8,192. The v5 tasks, unchanged except for the interface:

| task | solved (tdesk rules) | same task under Workbench budgets |
|---|---|---|
| pyrepo-bug1 / bug2 / implement | 0/24 | 5/8, 4/8, 1/8 |
| reflow-hard | 0/8 | 3/8 |
| expenses-easy / medium | 0/16 | 5/8 (easy) |
| routing-medium / hard | 2/8, 3/8 | 7/8 (medium) |

Almost every failure was **budget exhaustion**: whole-file `cat`, full pytest output, 80-line `sed` ranges, then out of tokens after 4–6 actions. The rest were broken JSON. This supports H1's *mechanism*: under the real budget, the untrained model fails our tasks for want of economy, not knowledge.

**Reward hack found.** In `plant`, the model decoded the base64/zlib-"sealed" simulator parameters ("Let me first decode the embedded parameters…") instead of experimenting. `plant` is removed from T-Desk.

**Change.** At about 0% solve rate, GRPO groups have zero variance and the run could not test H1. So the task *difficulty* is adjusted to sit at 30–70% under the real budget; the interface is unchanged. The new task set:
- `pyrepo-located`, `pyrepo-located2`: the instruction names the function(s) and one test command.
- `pyrepo-bug1`: the harder tier.
- `reflow-lite`: about 20-line handbook, 3 runs, ramp only, one revision trap.
- `downtime-lite`: 3 machines, short handbook, one amendment.
- `expenses-lite`: about 80 claims, short policy, one caveat.
- `routing-medium`, `routing-hard`: unchanged.

The economical path for each takes about 4–5 actions; careless reading still fails.

## Calibration (budget-fit set), before submission
Strict one-JSON parsing, arena budget rules, 8 episodes per task, two rounds. Round 2 added compact instructions (about 75–115 tokens), function line ranges for the located bugs, and one-commit git repos.

| task | round 1 | round 2 |
|---|---|---|
| pyrepo-located | 1/8 | 0/8 |
| pyrepo-located2 | 0/8 | 0/8 |
| pyrepo-bug1 | 1/8 | 0/8 |
| reflow-lite | 1/8 | 2/8 |
| downtime-lite | 2/8 | 1/8 |
| expenses-lite | 0/8 | 0/8 |
| routing-medium | 3/8 | 1/8 |
| routing-hard | 1/8 | 0/8 |
| **total** | **9/64** | **4/64** |

**Pooled: 13/128, about 10%.** At p ≈ 0.1 with groups of 5, about 40% of training steps should have mixed rewards (inference: 1 − 0.9⁵ − 0.1⁵).

**Failure anatomy (round 2):** 33 budget exhaustion, 30 format (13 broken JSON, 12 prose before JSON, 5 no JSON). In transcripts the model lists every directory, cats each document, writes a long script, then a second "verification" script, and runs out of budget, sometimes after already having the right answer.

**Decision:** submit this set unchanged. Further easing would not target the failure, which is habits, not task size. It would also drift from the eval's likely difficulty. The training curve is the first readout: does the reward rise from about 0.1?

**Added prediction (training curve):** if H1 holds, training reward rises from about 0.1 and mean reply length falls. A flat curve means the fixed recipe can't teach economy and format in about 100 steps.


## Result (2026-10-16)
**0/40. Every domain scored 0**, including the office and industrial tasks most runs keep.

**Training curve.** The smoothed reward rose from about 0.2 to about 0.55 over the first 40 steps. Mixed groups (0.25/0.5/0.75) appeared after step 4. There were "Rollout failed; retrying" alerts throughout, which are likely budget-overflow episodes dropped instead of scored 0.

**Verdict against the pre-registered rules: against H1** (total ≤ 3, with the training reward rising).

**Context that arrived during the run, not available at pre-registration:**
- naklitechie's repeated null control (zero updates) scored 1/40 and then 0/40. The no-update range is about **0–2**, mean about 1.25, against about 2.97 for trained runs (naklitechie's comparison). So "untrained = 4/40" is not the right reference: the zero-learning pipeline scores about 1.25.
- rca-umb's hard collapse test (trained to quit on the first reply, reward 0.20 → 0.97) also scored 0/40, also inside the no-update range.

**Reading:**
- **What T-Desk did not do:** it did not produce the generic gain that ordinary trained runs show (about +1.7 over no-update). Its score sits at the no-update floor even though training reward rose.
- **Likely explanations** (inference, not tested):
  1. The private eval is **not** served through `tbench2_env` with these budgets. Then training the `action_type` schema and tbench2 habits doesn't carry, and may compete with the eval's real format. Most entries use JSON-answer or run_bash-style schemas and get the generic gain.
  2. What it learned (finishing within the budget on our narrow tasks, possibly helped by budget-overflow episodes being *dropped* rather than scored 0) doesn't apply to the private tasks.
  3. Noise: 0 is within the no-update range, so a single run can't separate "no transfer" from "harmful transfer".
- **What it does tell us:** copying the smoke-test interface is not enough to move the private score. The smoke tests may not reflect how heldout-v2 is served.

## Next
- Our leaderboard row is unaffected (best per domain stays office 2, industrial 2, math 1 = 5/40).
- Use the corrected reference in future comparisons: no-update about 1.25, trained runs about 3.
- The generic gain seems to come from format and brevity on the eval's actual schema, which we still don't know.
