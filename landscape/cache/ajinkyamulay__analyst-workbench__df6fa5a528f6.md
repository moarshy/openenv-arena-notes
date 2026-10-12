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
| `write` | `path`, `content` | replaces a whole file |
| `edit` | `path`, `old`, `new` | replaces the one exact occurrence of `old` |
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

## Version 5: difficulty levels, calibrated on the arena's own model

Every family now has a level 2 (task id suffix `-l2`, or `@2`). Level 2 adds the kinds of
traps a careful analyst still has to handle: per-pump limits with dropouts and maintenance
windows, a tank interlock, a stock split, a payment holiday, firewall chains, subtitle sync,
dissolves and speed changes, four-function code repair with three bugs, and so on.
Independent solvers that see only the agent's files agree with every level-2 verifier on
hundreds of seeds per family.

Calibration with Qwen3.8-27B (Q4 GGUF, thinking on, arena-style turns) found that, once the
model gets a well-formed action out, it answers level-2 instances correctly 75 times in 76.
Its failures are almost all JSON formatting of long python code. The 17 families submitted
in v5 are the ones whose level-2 scores fell between 0.1 and 0.8 for the 27B; their signal is
mostly about getting code into a valid JSON action, not about the analysis itself. See
docs/v6_design.md for the next step.

## Version 6: Repo Repair

Because the 27B solves rule-following analysis once it gets a well-formed action out, v6 adds
software repair in real code. Four open-source libraries are vendored into the image at pinned
versions with their own test suites: boltons 26.2.0, more-itertools 11.1.0, toolz 1.2.0 and
inflection 0.5.1. A catalog of 636 single-token mutations (comparison and arithmetic operator
swaps, off-by-one constants, and/or, in/not in, is/is not) was built by applying each candidate
and keeping those that 1 to 8 of the library's own tests detect; edits are made in place, so the
file's formatting never reveals the location.

Each episode copies one library (without tests) into the workspace and injects 1 to 3 catalogued
bugs in different functions. BUG_REPORT.md shows the source of a failing test; at levels 3 and 4
some regressions are unreported and must be found by reading the code. The agent edits files
with `edit` (replace one exact snippet) or `write`. Grading runs the library's full test suite
on the agent's files: reward is the share of injected bugs whose tests all pass, and 0 if any
other test fails. Task ids: `swe-repo-<library>-l<level>`, for example `swe-repo-toolz-l3`.

Calibration with Qwen3.8-27B (thinking on, native tool calls): with one or two reported bugs it
fixed nearly every instance in which it got its tool calls right (1.00 and 0.90). With unreported
regressions (levels 3 and 4) its rewards were mixed with partial credit, about 0.4 on average,
which is where GRPO has something to learn. v6 submits levels 3 and 4 for each library.

## Run it

```sh
docker run --rm -p 8000:8000 docker.io/aji28/analyst-workbench:v6
openenv validate --url http://localhost:8000
```

Reset with `{"task_id": "fin-loan-balance"}` (optionally `"seed"`) over `/ws`, then send
actions such as `{"tool": "python", "code": "print(open('loan.txt').read())"}`.
