---
license: bsd-3-clause
pretty_name: Workbench (OpenEnv)
tags:
- openenv
- reinforcement-learning
- agents
- tool-use
- grpo
configs:
- config_name: tasks
  data_files:
  - split: train
    path: data/tasks.jsonl
---

# Workbench

An OpenEnv environment that trains **workspace habits**:
- explore a workspace that is too large to read in full
- search it with grep
- catch the hidden caveat (an amendment, a correction or an operations note)
- compute with code
- verify the result
- write an exact output file

It was built for [OpenEnv Arena](https://openenvarena-arena.hf.space/).

- **Source:** https://github.com/moarshy/workbench
- **Image:** `ghcr.io/moarshy/workbench:v1` (linux/amd64)

## Interface
Each action is one JSON object:
- `{"type": "run_bash", "command": "..."}` runs as an unprivileged user in `/app`. Output is capped at 8,192 characters, each command has a 120 s timeout, and there is no network. Available tools: python3 + pandas/numpy, grep/rg, jq, sqlite3.
- `{"type": "submit", "answer": "..."}` ends the task, and the output files are graded.

The answer key is never written to disk, and the server code can't be read from the sandbox. Tasks are graded automatically after 20 actions.

**Reward** = 0.5 × (share of checks passed) + 0.5 × (all checks passed). Each task has 6–8 deterministic checks.

## Tasks (9)
| task_id | domain | the job | caveats |
|---|---|---|---|
| downtime-{easy,medium,hard} | industrial | Per-machine unplanned downtime for one shift, from a per-minute sensor log of up to 52k rows plus a 600-line handbook | micro-stop exclusion, superseded and future-dated amendments, a revised limit, a night shift that crosses midnight |
| expenses-{easy,medium,hard} | office / finance | Audit a department-month of up to 3,000 multi-currency claims against a travel policy | cap changes mid-month (applied by claim date), superseded caps, a city changing tier, FX corrections in a separate folder, a future-dated rule |
| routing-{easy,medium,hard} | math (optimisation) | A two-van routing plan with capacity and time windows, within 5% of the optimum | dispatch notes: a forbidden van, a closed road, a cancelled order |

Every reset generates a fresh random workspace. `data/tasks.jsonl` holds one example instruction and file listing per task.

## Calibration
Qwen3.8-27B, thinking off, 8 episodes per task, counting full-score episodes. The first JSON object in each reply is taken as the action.

| | easy | medium | hard |
|---|---|---|---|
| downtime | 7/8 | 5/8 | 4/8 |
| expenses | 4/8 | 4/8 | 3/8 |
| routing | 5/8 | 3/8 | 4/8 |

Most failures were reply-format slips: prose before the JSON, unescaped quotes in shell commands, and Qwen's `<tool_call>` format. These are habits that RL can fix.

**Verification:** independent reference solvers that read only the agent-visible files score 1.0 on every tested seed. Solvers that ignore the caveats fail on medium and hard. Sandbox isolation is tested inside the container. See the source repository for details.
