# v6: T-Desk (pre-registered experiment)

**Status:** pre-registration, written 2026-10-15 before building or submitting. The predictions below are fixed. The result will be compared against them, not reinterpreted afterwards.

| | |
|---|---|
| Submission ID | `tdesk-v1` (planned) |
| Image | `ghcr.io/moarshy/workbench:tdesk-v1` (planned) |
| Arena result | (filled in after evaluation) |

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

## Calibration (budget-fit set)
(pending)
