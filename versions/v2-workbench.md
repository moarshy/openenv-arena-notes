# v2: Workbench

| | |
|---|---|
| Submission ID | `workbench-v1` |
| Submitted | 2026-10-11 20:50 (+08); validated 20:51; no GPU queue |
| Run | `a600462943db31233cdc0214` ([dashboard](https://openenvarena-training.hf.space/?project=arshy&runs=a600462943db31233cdc0214)) |
| Image | `ghcr.io/moarshy/workbench@sha256:dcaba95f5ab1808b95f51d319f1a922835c20d149014c12c369df5d1f84a9da7` |
| Dataset / source | [arshy/workbench](https://huggingface.co/datasets/arshy/workbench) · [github.com/moarshy/workbench](https://github.com/moarshy/workbench) |
| Arena result | **3/40** (Δ −1): office 2, industrial 1 |

## Hypothesis
- **Evidence:**
  - An old commit of the arena Space named its reference benchmark `skillsbench-balanced40-v2`.
  - SkillsBench's taxonomy matches the arena's 8 domain IDs exactly.
  - The organizers' OpenEnv adapter uses `run_bash` + `submit`.
  - Board evidence says the base model already *knows* the domains; it fails on *habits*.
- **Bet:** train workspace habits in the hidden test's likely interface:
  - explore a workspace too big to read
  - grep
  - catch hidden caveats
  - compute with code
  - write an exact output file

## Design
- **Actions:** `{"type": "run_bash", "command": ...}` and `{"type": "submit", "answer": ...}`.
  - Output capped at 8,192 chars, 120 s per command, 20 actions.
  - Runs as an unprivileged `agent` user in `/app`; the answer key stays in server memory.
  - Tools: python3 + pandas/numpy, grep/rg, jq, sqlite3. No network.
- **Families** (easy/medium/hard each, 9 tasks):
  - **downtime (industrial).** 52k-row sensor log and a 600-line handbook. Caveats: micro-stop amendments (superseded), a limit revision, a future-dated rule, a night shift crossing midnight. Output `downtime.json`.
  - **expenses (office/finance).** 3,000 multi-currency claims. Caveats: cap changes mid-month applied by claim date, superseded caps, a city tier change, FX corrections in a separate folder. Output `expense_report.json`.
  - **routing (math as optimisation).** A two-van VRP with capacity and time windows. Caveats: dispatch notes (forbidden van, closed road, cancelled order). Must be feasible and within 5% of a brute-forced optimum.
- **Reward:** 0.5 × (share of checks passed) + 0.5 × (all passed), with 6–8 checks per task.
- **Verification:**
  - Independent reference solvers score 1.0 on every tested seed (180/180 downtime workspaces).
  - Ignoring the caveats always fails medium and hard.
  - The container security checks pass.
- **Bug caught before submitting:** two amendments with the same date overwrote each other, making 2 of 60 hard tasks unsolvable. There is now a regression test.

## Calibration
Qwen3.8-27B via OpenRouter, thinking off, 8 episodes per task, 4 parallel containers. Total cost about $1.

| family | easy | medium | hard |
|---|---|---|---|
| downtime | 7/8 (strict) | 2/8 strict → **5/8** lenient | 2/8 strict → **4/8** lenient |
| expenses | 4/8 | 4/8 | 3/8 (lenient) |
| routing | 5/8 | 3/8 | 4/8 (lenient) |

**Key finding: most failures were format slips, not reasoning.**
- A sentence of reasoning before the JSON (most common).
- Unescaped quotes from shell commands inside the JSON string.
- Qwen's native `<tool_call>` format leaking out.
- An extra field (`"done": true`). The schema was made forgiving of extra fields before submitting.
- Token use: 30/43 successful episodes fit an 8k trajectory and 34/43 fit 12k. We chose completion 12288 and context 16384.

## Submission contract
- 9 tasks.
- Per task:
  - reset 180 s; rollout 900 s (kept tight on purpose); verifier 120 s
  - 24 tool calls
  - completion 12288, context 16384
  - 4 GiB memory, 2 vCPU
- Example actions: `ls /app`, then `submit`. Finish action: an empty `submit`.

## Training (dashboard)
- **Only 104 steps** (v1 had 257). Multi-turn episodes are long, so each step takes longer.
- By step 12 the smoothed reward was 0.64 → 0.84, with raw values hitting 1.0 on several steps (all 5 attempts at full marks, so no gradient).
- The tasks were easier under the arena's setup than in our calibration.
- **Inference:** the arena's reply parsing is more forgiving than our strict test, or its budget is more generous.

## Result
| domain | untrained | v1 | v2 |
|---|---|---|---|
| office | 2 | 2 | 2 |
| industrial | 2 | 0 | **1** |
| math | 0 | 0 | 0 |
| others | 0 | 0 | 0 |
| **total** | **4** | **2** | **3** |

The leaderboard row (best per domain across runs) went from 5% to 7.5%.

## Lessons
- **Fact:** 3/40 is within noise. 28 runs, none above 5/40, math still 0 everywhere. rca-umb's caveat-style Five Desks v2 scored 2/40.
- **Fact:** fewer than half the training steps of v1. Long multi-turn episodes cost training budget.
- **Fact:** rewards ran high early. Calibrating with strict parsing understated how easy the tasks were in the arena.
- **Inference:** it damaged industrial less than v1 (1 vs 0), consistent with practising industrial-style work. It is one task, so weak evidence.
- **Inference:** the routing family didn't reach the hidden math tasks. SkillsBench math is much bigger: many constraints, solver-quality objectives, PDDL and Lean.

## Next (candidates for v3)
- **More useful steps:**
  - harder tasks, calibrated with lenient parsing so groups stay mixed in the arena
  - shorter episodes (fewer allowed actions, smaller workspaces) so more optimizer steps fit in 4 hours
- **A format-discipline signal:** possibly reject prose-wrapped replies inside the environment (needs thought: the arena owns parsing).
- **Different domains:** science and finance are still untouched. Use SkillsBench-shaped tasks with domain libraries.
