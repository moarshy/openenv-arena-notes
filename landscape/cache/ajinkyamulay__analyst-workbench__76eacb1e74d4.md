---
license: mit
pretty_name: Analyst Workbench (OpenEnv)
tags:
- openenv
- reinforcement-learning
- agents
- tool-use
configs:
- config_name: tasks
  data_files:
  - split: train
    path: data/tasks.jsonl
- config_name: samples
  data_files:
  - split: train
    path: data/samples.jsonl
---

# Analyst Workbench

An OpenEnv environment for training agents to investigate small, realistic workspaces and
give one exact answer. It has 24 procedurally generated task families, three in each of eight
domains: software engineering, industrial systems, natural science, office work, finance, math,
cybersecurity, and media production.

## What an episode looks like

On reset the agent gets a short brief and a private folder of files (CSV tables, logs, code,
calendars, protocols, subtitles, EDLs and so on). It has 20 actions, each one JSON object:

| tool | fields | effect |
|---|---|---|
| `ls` | | list files with line counts |
| `read` | `path`, `start`, `lines` | numbered lines of a file (at most 80 shown) |
| `grep` | `pattern`, optional `path` | regex matches across files |
| `python` | `code` | runs in the folder as an unprivileged user, 10 s CPU, 1 GiB; numpy and pandas installed |
| `submit` | `answer` | ends the episode and scores the answer |

Observations are kept under about 3,000 characters, and the instruction is shown only once.

## Reward

`submit` returns a reward in [0, 1] from a verifier that recomputes the answer from the
generated instance; nothing is judged by a model. Most tasks are all-or-nothing (exact
strings, exact sets, or numbers within a stated tolerance). Tasks that ask for two or four
separate facts give equal partial credit per correct part, which the instruction states.
Code tasks run 60 hidden test cases in the sandbox and give 1 only if all pass. Running out
of actions or sending an empty answer scores 0.

Every reset without a seed draws a new random instance, so parallel rollouts of the same
task differ. A given `(task_id, seed)` is fully deterministic.

## Tasks

See `data/tasks.jsonl` for the catalog and `data/samples.jsonl` for five seeded instances per
task with reference answers. The code that generates and grades them is in `source/`.

## Checks before release

* 500 seeds per task: the reference answer scores 1; empty, garbage and plausible wrong
  answers (for example the buggy file, an off-by-one count, the decoy IP) score below 1.
* WebSocket replay against the container: example actions end with `done: true` and reward 0,
  reference answers score 1, wrong answers score below 1, the action budget ends an episode
  at reward 0, and the python tool cannot read the task sources.
* `openenv validate --url` passes all six checks.

## Difficulty checks with a local model

Before submitting, a weaker proxy (qwen3:14b, no thinking, temperature 0.7) played fresh
instances through the same one-JSON-object-per-turn protocol the arena uses. Version 1 had a
schema cap on `read` that ended episodes and five families the proxy always solved. Version 3
removes the cap (the server clamps instead) and hardens those five: two bugs spread over a
three-function module, two functions to implement, OEE with breaks and shift clipping, a loan
with a rate reset, and NPV with risk classes, start years and EUR flows. On v3 no family is
known to be always solved by the proxy; the code-repair family dropped from 4/4 to 1/8 and NPV
from 4/4 to 7/8. The proxy is weaker than the arena's model, so easier families may still
saturate there.

## Run it

```sh
docker run --rm -p 8000:8000 docker.io/aji28/analyst-workbench:v4
openenv validate --url http://localhost:8000
```

Reset with `{"task_id": "fin-loan-balance"}` (optionally `"seed"`) over `/ws`, then send
actions such as `{"tool": "python", "code": "print(open('loan.txt').read())"}`.
