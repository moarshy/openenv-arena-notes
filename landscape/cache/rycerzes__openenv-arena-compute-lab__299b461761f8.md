---
license: bsd-3-clause
pretty_name: Verified Compute Lab
tags:
  - openenv
  - reinforcement-learning
  - tool-use
  - math
  - science
  - finance
configs:
  - config_name: default
    data_files:
      - split: train
        path: tasks.jsonl
---

# Verified Compute Lab

An [OpenEnv](https://github.com/meta-pytorch/OpenEnv) environment for
[OpenEnv Arena](https://huggingface.co/spaces/openenvarena/arena): procedural,
multi-step tasks in **math and formal reasoning**, **natural science** and
**finance** that reward careful work with a tool rather than mental arithmetic.

Each episode is a fresh instance: a question, named answer fields and a few
small files (data, rules, sometimes a corrections memo). The agent works with
three tools and gets 12 calls:

```json
{"tool": "read", "path": "rules.md"}
{"tool": "python", "code": "print(sum(range(10)))"}
{"tool": "submit", "answer": {"balance": 1234.56, "interest": 789.01}}
```

`python` runs Python 3 (standard library) in the episode's folder as an
unprivileged user, with CPU, memory and output limits. `submit` ends the episode.

## What it teaches

- **Compute, don't guess.** Answers need exact simulation, fitting or counting
  (amortization schedules, XIRR, least-squares kinetics, Euler integration,
  digit DP, Dijkstra with path counts, matrix powers for huge N).
- **Read everything that's provided.** Level 2 adds the formatting real data
  has: accounting amounts like `(1,234.50)`, day-first dates, mixed units
  (min/mM, km/h, g, ft, knots, mg/kg), case variants and two-way roads.
  `rules.md` describes all of them. Level 3 adds a `memo.txt` whose
  corrections override the data files.
- **Strict output format.** One JSON object per turn, as the Arena trainer requires.

## Reward

The verifier recomputes every answer field from the generated instance and its
stated rules. The reward is the share of fields within tolerance: 1.0 when all
fields are right, partial credit only for multi-field answers. Running out of
tool calls, or the finish action `{"tool": "submit", "answer": {}}`, scores 0.

| Family | Domain | Levels |
|---|---|---|
| `loan_schedule` | finance | balance and interest after month k; extra payments and a rate reset; payoff with deferrals and a memo |
| `fx_ledger` | finance | multi-currency balance with reversals and missing FX days; accounting formats; memo, plus the top currency exposure |
| `xnpv_xirr` | finance | XNPV; XIRR with kUSD units and day-first dates; ranking three projects after a memo |
| `reaction_kinetics` | natural science | order and k; min/mM units, QC-failed rows and a prediction; Arrhenius Ea from two runs (C and K) |
| `projectile_ode` | natural science | Euler with quadratic drag; mixed units; wind bands in ft and knots |
| `stoichiometry` | natural science | limiting reagent and yield; mg/kg, purity formats and percent yield; two-step synthesis with a memo |
| `constrained_count` | math | brute-forceable counts; worded constraints; 10^12-scale digit DP with a forbidden digit |
| `graph_paths` | math | shortest path; h/min times, two-way and closed roads, a waypoint; counting all cheapest routes |
| `recurrence_mod` | math | a_N mod M; 1-indexed with a prefix sum; coupled sequences at N ~ 10^15 |

Task ids are `<family>-l<level>`; the server accepts any of the 27 at reset
(`task_id`), with an optional `seed` for a reproducible instance.

## Verification

- 27 independent reference solvers see only the prompt and files, run through
  the environment's own `python` tool and score 1.0 on every task. They were
  checked on 30+ seeds each. Empty and wrong answers score 0.
- `openenv validate --url` passes 6/6 against the linux/amd64 image. A WebSocket
  replay of every task passes against the container, and the sandbox runs as
  `nobody` and cannot read the environment source.

## Calibration

Measured on the real Qwen/Qwen3.8-27B (thinking off, temperature 1.0) through Hugging Face Inference Providers, with an Arena-style loop: a system message with the action schema, JSON observations as user turns, and one JSON object per reply (anything else ends the episode, scored through the finish action). This is a difficulty probe, not a training or leaderboard result.

A first version stated everything plainly and was saturated: every submitted answer was right, and the only failures were reply format. Levels 2 and 3 were then rebuilt around messy formats and corrections memos. In this second sweep (153 episodes), 94% of submitted answers are correct. Most zeros come from replies that are not one valid JSON object (usually unescaped quotes or backslashes in long `code` strings, sometimes empty replies). Ten submitted answers were wrong, several of them memo or unit mistakes.

The Arena submission trains on the 17 tasks with mixed outcomes (mean reward 0.17-0.83), so most 5-rollout GRPO groups should have non-zero reward variance. The other 10 tasks stay in the server and dataset.

| Task | Episodes | Mean reward | Correct when submitted | Format failures | In submission |
|---|---|---|---|---|---|
| `constrained_count-l1` | 6 | 0.67 | 1.0 | 2 | yes |
| `constrained_count-l2` | 6 | 0.83 | 1.0 | 1 | yes |
| `constrained_count-l3` | 6 | 0.50 | 0.75 | 2 | yes |
| `fx_ledger-l1` | 6 | 1.00 | 1.0 | 0 |  |
| `fx_ledger-l2` | 3 | 0.33 | 1.0 | 2 | yes |
| `fx_ledger-l3` | 5 | 0.20 | 1.0 | 4 | yes |
| `graph_paths-l1` | 6 | 1.00 | 1.0 | 0 |  |
| `graph_paths-l2` | 6 | 0.92 | 0.917 | 0 |  |
| `graph_paths-l3` | 5 | 0.80 | 1.0 | 1 | yes |
| `loan_schedule-l1` | 6 | 0.50 | 0.75 | 2 | yes |
| `loan_schedule-l2` | 5 | 0.80 | 0.8 | 0 | yes |
| `loan_schedule-l3` | 5 | 0.80 | 1.0 | 1 | yes |
| `projectile_ode-l1` | 6 | 0.83 | 1.0 | 1 | yes |
| `projectile_ode-l2` | 6 | 1.00 | 1.0 | 0 |  |
| `projectile_ode-l3` | 6 | 1.00 | 1.0 | 0 |  |
| `reaction_kinetics-l1` | 6 | 1.00 | 1.0 | 0 |  |
| `reaction_kinetics-l2` | 4 | 1.00 | 1.0 | 0 |  |
| `reaction_kinetics-l3` | 6 | 0.50 | 1.0 | 3 | yes |
| `recurrence_mod-l1` | 6 | 1.00 | 1.0 | 0 |  |
| `recurrence_mod-l2` | 6 | 0.75 | 0.9 | 1 | yes |
| `recurrence_mod-l3` | 6 | 0.17 | 0.5 | 4 | yes |
| `stoichiometry-l1` | 6 | 0.58 | 0.7 | 1 | yes |
| `stoichiometry-l2` | 6 | 0.83 | 1.0 | 1 | yes |
| `stoichiometry-l3` | 6 | 0.50 | 0.75 | 2 | yes |
| `xnpv_xirr-l1` | 6 | 1.00 | 1.0 | 0 |  |
| `xnpv_xirr-l2` | 6 | 1.00 | 1.0 | 0 |  |
| `xnpv_xirr-l3` | 6 | 0.67 | 1.0 | 2 | yes |

## Links

- Image: `ghcr.io/rycerzes/openenv-arena-compute-lab:v1` (linux/amd64)
- Source: https://github.com/rycerzes/openenv-arena-compute-lab
- Dataset: https://huggingface.co/datasets/rycerzes/openenv-arena-compute-lab
- Built for OpenEnv Arena with OpenEnv at `86a180ede21e044f7929b9a7783ad83aa67d83a3`

## Files

- `tasks.jsonl`: one row per task id, with its domain, whether it is in the
  Arena submission, its calibration, and a seed-0 example instance (prompt,
  files and answer).
- `source/`: the environment source, tests, reference solvers and scripts.
- `calibration_summary.json`: per-task results against Qwen3.8-27B.
