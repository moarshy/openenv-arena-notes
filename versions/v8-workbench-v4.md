# v8: Workbench v4, "finance traps + protected reward" (pre-registered)

**Status:** pre-registration, written 2026-10-17 before building the release image or submitting. The predictions and verdict rules below are fixed; the result will be compared against them, not reinterpreted.

| | |
|---|---|
| Submission ID | `workbench-v4` (scheduled for the next slot, about 2026-10-17 21:00 +08) |
| Submitted | 2026-10-17 21:00:33 (+08), HTTP 202 |
| Run | `a611a52d44618eac4641f5e2`, 108 steps ([dashboard](https://openenvarena-training.hf.space/?project=arshy&runs=a611a52d44618eac4641f5e2)) |
| Image | `ghcr.io/moarshy/workbench:v4@sha256:90ad6f254133c5cbc9989f9149d8fb3a0e05cbf787e13b4a78298bbd2e7575f6` (public) |
| Dataset / source | `arshy/workbench` (task list), github.com/moarshy/workbench |
| Arena result | **3/40** (Δ −1): office 2, industrial 1, finance 0, software 0 |

## Why
- **The interface experiments are finished.** v6 (tbench2, tight budget) scored 0 and v7 (tbench2, roomy) 2. Copying the smoke-test interface did not help ([v7](v7-tdesk-roomy.md)). v8 goes back to our best setup: `run_bash`/`submit`, a 12,288 / 16,384 budget, 12 actions.
- **Our row needs new domains, and finance is reachable.** The row is office 2, industrial 2, math 1 = 5/40. Finance scores in about 11% of field runs and software in about 29%. The best recent run (distributedtensor, 5/40) used procedural workspaces with *late caveat* and *false premise* families ([two-streams research](../research/2026-10-16-two-streams.md)).
- **The research says reward behaviours, not just answers.** Transfer is tied to verifying completion and not breaking things. The strongest recipe (Kimi) rewards the fraction of checks but **zeroes the reward if a pass-to-pass check fails**. Efficiency bonuses only help when they are **success-gated**.

## What changes vs v5 (Workbench v3, 3/40)
| | v5 | **v8** |
|---|---|---|
| Interface | run_bash/submit, 12 actions, 12k/16k | **same** |
| Tasks | 10: pyrepo ×3, repair ×2, reflow, plant ×2, downtime, expenses | **9:** pyrepo-bug1, pyrepo-implement, repair-medium, **loans-easy, loans-medium, loans-hard**, expenses-easy, reflow-hard, downtime-medium |
| Reward | 0.5·share + 0.5·all-pass | **0 if any protected check fails**; else **full success = 0.9 + 0.1·steps_left/12** (success-gated efficiency), partial = 0.5·share (< 0.5). Kept in [0, 1] |
| Protected checks | none | output exists and has the exact keys/types; **input files unchanged**; pyrepo: **every test that passed before still passes**, tests untouched; repair: no regressions, decoy kept |
| Hint | worked JSON examples | + one sentence: leave the given files unchanged except code you're asked to fix |

`plant` stays out (reward hack found in v6). `routing` and `repair-hard` are dropped to make room for finance.

**This is a multi-factor change**: new tasks *and* a new reward. A result cannot be attributed to one of them. It is a breadth-and-draw run, with one pre-registered domain test (finance).

## The new family: loans (finance)
Month-end loan-loss provisions at a small lender. The agent stages every loan by days past due on the reporting date and computes the EUR provision. Output: `output/provisions.json` with `stage2_loans`, `stage3_loans`, `total_provision_eur` and `discrepancies`.
- **Late caveat:** a dated risk-committee memo changes a provision rate (on hard, a later memo supersedes it), or declares some payments returned by the bank. Noise memos sit around it.
- **False premise:** the CFO says three named loans were written off last month. Usually 1–2 are not in the write-off register: follow the records and list them as discrepancies. In about 25% of instances the CFO is right, and the answer is `[]`.
- **Hard adds:** a future-dated memo to ignore, payments recorded after the reporting date (unpaid on it), and FX on balances.
- **Tests:**
  - a solver reading only the files gets full marks on 60 instances
  - ignoring memos, trusting a false premise, or ignoring post-report payments all fail
  - DPD values never sit within ±3 days of a threshold

## Calibration (before submission)
Qwen3.8-27B via OpenRouter, thinking off, 12,288 completion-budget accounting, 16,384 context, 8 episodes per task:

| task | strict | lenient |
|---|---|---|
| pyrepo-bug1 | 1/8 | 3/8 |
| pyrepo-implement | 2/8 | 1/8 |
| repair-medium | 2/8 | 2/8 |
| loans-easy | 0/8 | 5/8 |
| loans-medium | 0/8 | 5/8 |
| loans-hard | 0/8 | 4/8 |
| expenses-easy | 1/8 | 3/8 |
| reflow-hard | 3/8 | 0/8 |
| downtime-medium | 2/8 | 3/8 |
| **total** | **11/72 (15%)** | **26/72 (36%)** |

- **Strict failures are almost all format** (66/72 strict episodes ended on an invalid reply): prose before the JSON, unescaped quotes, `<tool_call>` tags. Lenient parsing (first JSON object in the reply) is the better estimate of task difficulty. Past arena training rewards sat well above our strict numbers.
- **Loans sit in the 30–70% target under lenient parsing.** Lenient loans failures were broken replies before any output, plus two near-misses on `discrepancies`.
- **Verifier fix after calibration.** One near-miss listed unmentioned write-offs as "contradictions", a defensible reading of the wording. The instruction now says only loans *named in the request* can be discrepancies. The loans tests were rerun and pass. The episodes were not rerun.
- **Reward rescaled after calibration** so it stays in [0, 1], as the arena's admission check requires. The earlier draft could reach 1.075. Solve counts above are unaffected; only the per-episode reward values differ.
- **Decision:** freeze this set. pyrepo-implement and reflow-hard are low, but two 8-episode runs of reflow gave 3/8 and 0/8, so that's within noise.

## Hypotheses and predictions
- **H-finance (loans transfers to the hidden finance tasks):** finance ≥ 1/5. The field base rate is about 11% of runs, and we have never scored finance.
- **H-protected (the zeroing reward doesn't hurt the generic trained gain):** total ≥ 2/40, the trained band. The no-update floor is about 0–2 (mean ≈1.25) and trained runs average ≈2.97.

**Verdict rules (fixed now):**
- **Finance ≥ 1 → supports H-finance**, weakly: single-run noise is large, so replicate before claiming it.
- **Finance 0 → no support.** That's consistent with no transfer, but it can't rule it out at about 11% base rates.
- **Total ≤ 1 → against H-protected.** The protected-zero reward, or the new mix, may have suppressed the generic gain. Compare with v6.
- **Total ≥ 4 → above our mean** (v1–v7 mean 2.4). Treat it as a draw unless it replicates.
- **Leaderboard row:** any new domain point raises it above 5/40. That is the practical goal, independent of the hypotheses.

**Training-curve expectations:**
- More exact-zero rewards early than v5, from protected zeroes and format failures.
- A rising mean reward.
- `frac_reward_zero_std` below about 0.6, since partial credit gives spread within groups.

## Training (arena dashboard)
108 steps; validated, trained and evaluated without errors. The curves are on the dashboard and were not pulled into this record.

## Result (2026-10-18)
**3/40**: office 2, industrial 1, every other domain 0.

| domain | v5 (Workbench v3) | v7 | **v8** |
|---|---|---|---|
| office | 1 | 1 | **2** |
| industrial | 2 | 1 | 1 |
| finance | 0 | 0 | **0** |
| software | 0 | 0 | 0 |
| total | 3 | 2 | **3** |

**Verdicts against the pre-registered rules:**
- **H-finance: no support.** Finance 0. That is consistent with the loans tasks not transferring, but at an ≈11% base rate one run can't rule transfer out.
- **H-protected: not contradicted.** A total of 3 is in the trained band (≥2) and matches the field's trained mean (≈2.97). The zeroing reward did not push the run to the no-update floor the way v6 did.
- **Above our mean (≥4)? No.**
- **Leaderboard row: unchanged** at office 2, industrial 2, math 1 = 5/40.

**One observation, not a test:** office came back to 2. After 2026-10-14, only 2 of 22 field runs had office ≥2 (the "office drift"). We did not predict this, and it may be noise.

## Lessons
- **Facts:**
  - New finance tasks with traps, a protected-check reward and a success-gated bonus gave an ordinary trained-band score.
  - Finance did not move.
- **Inferences:**
  - The hidden finance tasks probably differ from our loan audits in shape (documents? spreadsheets? other file types?), not just in domain label.
  - The protected reward is at least not harmful, so it can stay as the default.

## Next
