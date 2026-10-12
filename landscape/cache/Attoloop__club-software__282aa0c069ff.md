---
license: apache-2.0
pretty_name: Club Software
tags:
  - rl-environment
  - openenv
  - openenv-arena
task_categories:
  - reinforcement-learning
size_categories:
  - n<1K
---

# Club Software

15 software-engineering tasks for the [OpenEnv Arena](https://openenvarena-arena.hf.space/), toned down
from three [Attoloop](https://huggingface.co/Attoloop) environments so that a 27B model succeeds some of
the time. Each task is a real working environment with its original grader; the easier versions change
only the starting state, never the grading.

| Source | Tasks | What the model must do | How it is toned down |
|---|---|---|---|
| dialect-recon | 7 | Make an interpreter match a hidden dialect of a small language, using 40 examples and a metered probe | A working base-language interpreter is given; its dialect settings are a dictionary with the allowed values listed. Rung r1 has all changes but one set, r2 the ones the examples reveal, r3 none |
| table-press | 4 | Encode HTTP/3 header lists in QPACK so two independent decoders reproduce them, in as few bytes as possible | Traces cut to 5 header lists; in e5 a valid literal-only encoder is given and the job is to make its output smaller |
| distribution-robust-sql-rewrite | 4 | Rewrite a PostgreSQL query so it returns exactly the same rows at a lower planner cost on hidden databases | The easiest band (predicate pushdown) |

Tasks are listed in training order: the most-helped rungs of every source first, the least-helped last.

## Interface

One episode is one task in a fresh container. The model replies with exactly one JSON object per turn:

- `{"op": "run", "command": "..."}` runs one shell command in the working directory.
- `{"op": "write", "path": "...", "content": ["line", "line"]}` writes a file, content given as a list of lines.
- `{"op": "edit", "path": "...", "old": "...", "new": "..."}` replaces one exact snippet that occurs once.
- `{"op": "submit"}` ends the episode; the task's own verifier grades the work.

The model's commands run as an unprivileged user; the verifier's files stay root-only until grading.

## Reward

Each verifier's raw score is mapped into [0, 1] with a hyperbolic calibration between two anchors per task
(`tasks.jsonl` lists them): the low anchor scores 0, the high anchor 0.4, and the curve keeps rising toward
1.0 above it.

- dialect-recon: 0 to 300 hidden programs matched (a submission failing the visible-examples gate scores 0).
- table-press: the low anchor is the gate floor, so any valid encoding earns reward; the high anchor is 0.32
  times the reference literal encoding's size, the median ratio a frontier agent reached on the full traces.
- SQL rewrite: the grader's own quality score, 0 to 1.

## Limitations

- The original tasks are sealed offline; the arena sandbox has outbound internet, which an unprivileged
  process cannot be denied. The adapter points the usual proxy variables at a closed port.
- The rungs' difficulty was set from the tasks' own data, not measured on the target model.

## Licences

The tasks and verifiers are released under the Apache License 2.0 (`LICENSE`). Third-party material keeps
its own licence; notices are in `licenses/<environment>/` and inside each image.
