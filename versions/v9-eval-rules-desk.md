# v9: Eval-rules desk (design draft, 2026-10-18)

**Status:** built, calibrated and pre-registered. Run 1 was submitted on 2026-10-18 at 23:18:40 (+08), HTTP 202. Runs 2–5 are scheduled by `scripts/submit_chain.py`, one per slot (run 2 at about 2026-10-19 23:20), and the chain stops if a run is rejected or fails.

**Image:** `ghcr.io/moarshy/workbench@sha256:abc5496b…00a5`. **Dataset:** `arshy/eval-rules-desk`.

## The idea in one line
Train the **survival habits** the day-0 proxy showed are missing, under the **hidden test's exact rules**. The aim is that the model reaches a clean finish instead of dying first.

## Evidence it rests on
- **Day-0 proxy:** 23 public SkillsBench tasks, 91 episodes. 0/91 reached `submit`.
  - 48 died on an invalid reply: prose before the JSON 21, script cut off by the budget 15, broken escaping 10.
  - 35 ran out of budget.
  - Observations took 76% of the budget.
  - All 9 solves were files written before the episode died.
- **r2/r5:** content never transferred (every domain-targeting run missed). The only real effect is "any training" (≈+1.5). Noise is ±1.2–1.7 per run.
- **r3:** about 450 episodes per run can shift habits, not skills. Qwen responds to format-shaped rewards. The only process reward with an ablation behind it is a repeat-turn penalty.
- **r4:** the eval rules:
  - organizers' adapter: `run_bash`/`submit`/`finalize`
  - strict one-JSON replies
  - 8,192 completion budget counting observations, 16,384 context
  - head-only 8,192-character output
  - `/root`
  - no skills and no hint text

## Design
### 1. Interface: a copy of the eval's
| | v4 (ours) | **v9** |
|---|---|---|
| Action | `{type: run_bash/submit, command, answer}` | **`PostTrainAction`, field for field:** `type ∈ {run_bash, submit, finalize}`, `command`, `answer` |
| Observation | output (3k chars, head+tail), exit_code, steps_left | **`PostTrainObservation`:** `output` (**first 8,192 chars + "[benchflow output truncated]"**), `task_id`, `rollout_dir`, `last_returncode` |
| First observation | instruction + our HINT with worked JSON examples | **the instruction only**: no examples or warnings, which the eval doesn't give |
| Workdir | `/app` | **`/root`** (absolute paths in instructions) |
| Budget | 12,288 / 16,384, 12 actions | **8,192 counting observations / 16,384, 128 tool calls** |
| Finish | submit | **`finalize`**; the sandbox is graded however the episode ends |

### 2. Tasks: practice for the habits, in SkillsBench shape
About 10 tasks, 1 or 2 per family, each about 11 training steps:
- **Rebuilt from our verified generators**, with inputs moved to `/root`. Files are made *too big to `cat`* (an 8,192-character head shows under 10% of them), so reading selectively is required. The answer needs one short script plus an exact JSON or xlsx output.
- **Binary formats in about half the tasks:** inputs as `.xlsx` (openpyxl) or `.pdf` (reportlab-generated tables), and some outputs as `.xlsx`. This trains "use the library, don't cat a binary".
- **Candidates:**
  - loans (xlsx book + pdf memos)
  - expenses (xlsx claims)
  - downtime (large CSV log)
  - reflow (CSV + pdf handbook)
  - pyrepo-bug1 (real library)
  - a "report" family: a docx/pdf in, an xlsx summary out
- **Instructions:** 120–280 words, like SkillsBench. Paths, filenames and wording vary per seed so the model can't memorise a template.

### 3. Reward: the task score, plus the two habits with evidence
```
task_score = share of the task's checks passed, 0 if a protected check fails   (as v4)
reward     = 0.85 · task_score
           + 0.15 · clean_finish          only if task_score ≥ 0.5   (ended via submit/finalize, not death)
           − 0.05 · repeated_turns         River's ablated penalty, capped at 0.2
           clipped to [0, 1]
```
- **Gating the clean-finish bonus** stops "submit immediately" from paying.
- **No length or efficiency bonus.** The real 8k budget enforces economy by itself: an episode that wastes it dies.

### 4. Calibration before building the image (strict, eval rules, local)
- Every task should be at **30–70% full solves** under strict parsing with the 8k-counting budget, 8 episodes each.
- **Run the day-0 proxy harness on our own training tasks too**, so the death profile is comparable. Training tasks should die the same ways the public tasks do (format, budget), or they aren't practising the right thing.

### 5. Image
`python:3.12-slim` + openpyxl, pdfplumber, pypdf, python-docx, reportlab, pandas, numpy, pytest, jq, ripgrep. LibreOffice is left out for size; it's a candidate for later. The answer key stays in server memory and the server code is unreadable to the agent, as now.

## Evaluation plan (to pre-register before day 1)
- **Five identical submissions** on consecutive slots.
- **Primary verdict:** the pooled 5-run mean minus the same-day field mean. ≥ +1.5 supports "eval-rules habits transfer". ≤ 0 is against.
- **Validity check per run** (dashboard): mixed reward groups on most steps, rising reward, few failed rollouts.
- **Stop rule:** if run 1 shows a broken training curve (reward flat at 0, most groups zero-variance), fix it before spending runs 2–5.

## Risks
- **The eval may serve the model through a native-tool-call harness (OpenCode), not one JSON per turn.** Then the format habits matter less, but economy, selective reading and writing early still apply.
- **The 8k budget may cut too many training episodes** (v6's failure). That's why the clean-finish bonus and calibration at 30–70% matter. v6 was 4k with about 10% solves.
- **The proxy has 91 episodes on public tasks.** The private tasks may differ.

## Calibration, round 1 (2026-10-18)
Built as designed: `server/evalrules_environment.py`, `evalrules_models.py` and `server/Dockerfile.evalrules`, with 7 tests including a full-marks reference solution on all 9 tasks after the xlsx/pdf conversion.

**Run:** Qwen3.8-27B via OpenRouter, thinking off, temperature 1.0, strict one-JSON parsing, 8,192 completion budget counting observations, 16,384 context, 8 episodes per task.

**Result: 5/72 full solves (7%).**

| task | full solves | episodes with reward > 0 |
|---|---|---|
| loans-medium | 0/8 | 0 |
| loans-hard | 0/8 | 0 |
| expenses-easy | 0/8 | 0 |
| expenses-medium | 0/8 | 0 |
| downtime-medium | 1/8 | 1 |
| reflow-hard | 2/8 | 3 |
| pyrepo-bug1 | 1/8 | 8 |
| pyrepo-implement | 0/8 | 8 |
| repair-medium | 1/8 | 5 |

**Death profile matches the day-0 public tasks**, which is the design's check that the tasks practise the right thing:

| ending | v9 | public tasks (day 0) |
|---|---|---|
| broken JSON escaping | 24 | 10 |
| prose before the JSON | 19 | 21 |
| budget | 13 | 35 |
| `<tool_call>` tags | 10 | 2 |
| clean submit | 2 | 0 |

## Amendment 1 (2026-10-18, before submission): survival term
**Problem:** the 4 data tasks gave reward 0 in all 32 episodes, because the model broke format before writing output. All-zero GRPO groups teach nothing, which would waste about 40% of steps.

**Change (approved by the user):** reward += 0.02 per valid action, counting at most 5 (max +0.1), still clipped to [0, 1]. This is a format-survival reward, of the kind Qwen responds to (r3).

**Effect, recomputed on the round-1 episodes:** every task now has reward spread. Loans and expenses have SD 0.02–0.03 from survival alone. pyrepo-implement (SD 0.01) and expenses-easy (SD 0.01) remain weak but are kept, to avoid another round of task changes.

**Not met:** the design's 30–70% full-solve target. Under the eval's rules, the untrained model dies on format first. The training signal comes from survival and partial credit.

## Pre-registration (2026-10-18, before the first submission)
**Submission:** `eval-rules-desk-v1` and four identical replicates (`-v1-r2` … `-r5`), one per slot, with the same image digest, tasks and contract.
- **Contract:** completion 8,192, context 16,384, 128 tool calls, finish_action `{"type": "finalize"}`.
- **Image:** `ghcr.io/moarshy/workbench:v9`. All container checks pass.

**Hypothesis H-habits:** training the survival habits under the hidden test's own rules transfers to the hidden test. The habits are one clean JSON per turn, small observations, writing output early, and a clean submit.

**Primary measure:** our 5-run mean minus the mean of all other users' runs evaluated on the same days (the drift-matched control).
- **≥ +1.5:** supports H-habits.
- **≤ 0:** against H-habits.
- **Between:** inconclusive. Report it as such, and don't extend the run count to chase significance.

**Interim rule:**
- **After run 1:** if the training curve is invalid (reward flat at about 0, most groups with no spread, or many failed rollouts), stop and fix it before spending runs 2–5. The hidden score of a single run is not used to stop or continue.
- **After run 3:** no peeking rule. All 5 runs are completed regardless.

**Secondary, descriptive only:**
- per-domain points against field base rates (office 0.93, industrial 0.77, software 0.18, finance 0.09; others ≤ 0.03)
- training reward trend
- the share of steps with mixed groups

**Context:**
- Our previous 8 runs averaged 2.5. The field's runs average about 2.75 (SD 1.17) and drift downward over time.
- One run's SD is about 1.2–1.7, so 5 runs give about ±0.75 on the mean difference.

## Run 1 (`eval-rules-desk-v1`, run `8b8f055414db4dac7adff019`, 114 steps)
**Hidden score: 3/40** (office 2, industrial 1). As pre-registered, a single run's score is not used to stop or continue.

**Training validity check (the interim rule), from Trackio:**

| quarter | mean reward | share of steps with zero-spread groups |
|---|---|---|
| 1 | 0.33 | 0.11 |
| 2 | 0.38 | 0.25 |
| 3 | 0.39 | 0.21 |
| 4 | 0.46 | 0.29 |

- 0 retries. The mean completion length rose from 672 to 943 tokens.
- **Verdict: valid.** Reward rises, most groups have a spread, and nothing failed. **The chain continues to run 2.**

**Per-task reward, first half → second half** (mapping step/task 1–9 to the submission's task order):

| task | first half | second half |
|---|---|---|
| reflow-hard | 0.32 | 0.73 |
| downtime-medium | 0.33 | 0.53 |
| loans-medium | 0.23 | 0.25 |
| pyrepo-bug1 | 0.69 | 0.76 |
| repair-medium | 0.72 | 0.71 |
| pyrepo-implement | 0.71 | 0.68 |
| loans-hard | 0.09 | 0.11 |
| expenses-medium | 0.08 | 0.10 |
| expenses-easy | 0.09 | 0.13 |

The industrial tasks learned clearly. Loans and expenses (xlsx/pdf inputs) barely moved past survival-level reward.
