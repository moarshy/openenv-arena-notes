---
license: apache-2.0
pretty_name: Five Desks v2 (OpenEnv environment)
tags:
- openenv
- reinforcement-learning
- rl-environment
- tool-use
- agents
configs:
- config_name: default
  data_files:
  - split: train
    path: tasks.jsonl
---

# Five Desks v2: find the caveat, think in metadata

Five Desks v2 is an [OpenEnv](https://github.com/meta-pytorch/OpenEnv) environment of procedurally generated tasks
in all eight [OpenEnv Arena](https://openenvarena-arena.hf.space/) domains. It trains two habits that the untrained
Qwen3.8-27B lacks when it runs with thinking off, as in the arena:

1. **Look before answering.** Most tasks hide one caveat that a careful worker finds by reading: a late email, an
   errata line in a maintenance log, a lab notebook correction, a maintainer's decision in an issue thread, a
   clarification from a problem setter, a deployment note, a credit-notes table, page 2 of a style guide.
   Missing it gives a plausible but wrong answer.
2. **Reason somewhere.** Every OpenEnv action has a free-form `metadata` object. About half of the resets
   suggest putting the working there (`{"tool": ..., "args": ..., "metadata": {"reasoning": "..."}}`), so the
   model can think before acting while still replying with exactly one JSON object. A tool-free reasoning
   task (counting, schedules, expected values, recurrences, knights and knaves) can only be solved that way.

- **Image:** `ghcr.io/rca-umb/five-desks:v2` (linux/amd64, public). The arena pins the digest at submission.
- **Source:** environment, tests, calibration and evaluation code are in [`source/`](./source).
- **Tasks:** [`tasks.jsonl`](./tasks.jsonl) has one row per task id with a seed-0 example (prompt, files, a
  scripted solution, a "caveat missed" solution) and the calibration below.
- **Version 1** is at revision
  [`1138ff6`](https://huggingface.co/datasets/rca-umb/five-desks/tree/1138ff662305c8765223d3ddfdeeeaa87302db43).
  It trained for 265 steps with healthy reward variance (about 80% of groups mixed) and scored 2/40 on the
  private tasks against 4/40 untrained, so learning signal alone was not the problem.

## Why these tasks

Before building v2 we ran the untrained Qwen3.8-27B (thinking off, strict one-JSON-object replies) on a separate
stand-in test, eight task types with their own action formats (`calibration/stand_in_test_findings.md`).

- It stops gathering information once it has a plausible answer (0/15 on a scheduling task whose decisive
  detail is in a second email).
- Without thinking it answers instantly: one-shot math 1/10 with thinking off, 5/5 with it on.
- Telling it to "be diligent" did nothing (0.53 vs 0.54 base), and neither did worked demonstrations (0.54).
- Telling it to **reason step by step inside the action's metadata** raised the stand-in score from 0.56 to
  0.70 (pooled over two runs of 80 episodes each, about 3 standard errors). The extra working fixed interval
  arithmetic, multi-step finance and one-shot math (0.15 to 0.50).

Training cannot rely on the hint: the arena's private tasks will not give it. v2 therefore shows the hint on
only about half of the resets, and rewards the outcome either way, so reasoning that pays off can become the
model's own habit. Whether it does is exactly what one arena run tests.

## Interaction

One generic action for every task: `{"tool": "<name>", "args": {...}}` plus the optional `metadata` object.
The reset observation describes the task and lists its tools with argument names and types, for example:

```
- read_file {"path": string}: show one file
- python {"code": string}: run Python 3 code (standard library only) in the workspace directory
- submit {"answer": object}: submit the answer (ends the episode)
```

Observations are `{"output": str, "steps_left": int}`. An unknown tool, or unknown, missing or mistyped
arguments, returns an error and uses up a tool call. `{"tool": "submit", "args": {}}` always ends the episode
(the arena's finish action) and scores the work so far. Reset takes `task_id` and an optional `seed`; without a
seed every reset generates a fresh instance.

| family | domain | tools | what decides the answer |
|---|---|---|---|
| software-repofix | software engineering | files, write_file, run_tests | maintainer decision in `issue_comments.md`, checked by hidden release tests |
| industrial-telemetry | industrial | files, python | `maintenance_log.md` invalidates an earlier, decoy cavitation run |
| science-lab | natural science | files, python | `notebook.md` corrects a temperature, dilution, outlier or genotype call |
| office-scheduling | office | inbox, calendars, check_slot, create_event | an attendee's later email blocks the obvious slot |
| finance-receivables | finance | SQL | credit notes / refunds tables change the balance or the duplicate count |
| math-problems | math | files, python | `clarifications.md` changes one condition of the problem |
| security-audit | cybersecurity | files, search | the obvious vulnerability is in `legacy/`, which `DEPLOYMENT.md` says is not deployed |
| media-copyedit | media | show, guide, set_line, check | page 2 of the style guide (a client addendum the checker does not cover) |
| math-reasoning | math / formal reasoning | submit only | the working itself: no tools, one answer, 2 calls |

The eight diligence families have two levels: `-l1` points at the caveat in the brief, `-l2` does not.
math-reasoning has an easier `-l1` and a harder `-l2`.

## Reward

Binary or near-binary, in [0, 1]: 1 for the right answer (numbers to 1% or $1.00, exact integers, slots, lines
within one, reduced fractions); partial credit only where a multi-part answer is partly right (finance,
science), a fix passes the visible but not the hidden tests (0.3), a finding names the right file and CWE but
the wrong line (0.5), or an edit follows page 1 but not page 2 of the guide (0.4). The reasoning hint never
changes the reward.

Checks in `source/tests/`: for every task id over 25 seeds the scripted solution scores 1, the caveat-missing
solution scores below 1 and the finish action scores 0; every answer is re-derived independently from what the
agent can see; a fuzzer sends 3,045 hostile tool calls (0 failures); and known reward hacks are closed (a test
file that exits early, path traversal, recursive SQL, runaway processes and output).

## Calibration (Qwen3.8-27B, thinking off, strict arena reply rules)

Served by HF Inference Providers (DeepInfra), temperature 1.0, arena-style system prompt with the action schema,
JSON observations. "Hint" means the reset suggested reasoning in metadata; the model used metadata in 80 of 92
hinted episodes and in 4 of 84 unhinted ones. The nine trained tasks are marked.

| task id | mean | n | with hint | without hint | trained |
|---|---|---|---|---|---|
| software-repofix-l2 | 0.47 | 16 | 0.42 (6) | 0.51 (10) | yes |
| industrial-telemetry-l2 | 0.31 | 16 | 0.56 (9) | 0.00 (7) | yes |
| science-lab-l2 | 0.69 | 16 | 0.89 (9) | 0.43 (7) | yes |
| office-scheduling-l2 | 0.19 | 16 | 0.30 (10) | 0.00 (6) | yes |
| finance-receivables-l2 | 0.31 | 16 | 0.33 (12) | 0.25 (4) | yes |
| math-problems-l2 | 0.19 | 16 | 0.18 (11) | 0.20 (5) | yes |
| security-audit-l2 | 0.66 | 16 | 0.43 (7) | 0.83 (9) | yes |
| media-copyedit-l2 | 0.50 | 16 | 0.56 (9) | 0.43 (7) | yes |
| math-reasoning-l1 | 0.29 | 24 | 0.33 (9) | 0.27 (15) | yes |
| math-reasoning-l2 | 0.08 | 24 | 0.20 (10) | 0.00 (14) | |

Pooled, hinted episodes averaged 0.41 and unhinted ones 0.29. All nine trained tasks have mixed outcomes, so
GRPO groups carry signal. The samples are small, and none of this measures a training gain or an arena score.

## Transfer check on other entrants' environments

Does the reasoning habit help outside this environment? We ran the untrained model on two other public arena
environments, with and without the instruction to reason step by step in the action's metadata (the same arena
reply rules; containers run offline; outcomes only in `calibration/transfer/far-*`):

| environment | tasks | base | with reasoning instruction |
|---|---|---|---|
| MetaHarness (ruv), its 8 submitted cells | 96 episodes per arm | 0.175 | 0.143 |
| Verified Compute Lab (rycerzes), 9 families x levels 2-3 | 54 per arm | 0.031 | 0.019 |

No gain on either. The base model is near the floor on both under strict reply rules (on Compute Lab 34 of 54
base episodes ended on malformed JSON, 24 with the instruction), so these runs have little power, but they give no
sign that the instruction transfers. The positive result is only on our own stand-in test (near transfer, 0.56
to 0.70). We submit anyway because the diligence tasks are the core of the environment and the hint is shown on
only half of the resets; the arena run is the real test.

## Run it

```sh
docker run --rm -p 8000:8000 ghcr.io/rca-umb/five-desks:v2
openenv validate --url http://localhost:8000
python source/scripts/replay_v2.py --url http://localhost:8000
```
