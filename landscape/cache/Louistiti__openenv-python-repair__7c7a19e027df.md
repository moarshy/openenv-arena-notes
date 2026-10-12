---
license: mit
language:
- en
tags:
- openenv
- reinforcement-learning
- code-repair
size_categories:
- 1K<n<10K
task_categories:
- text-generation
configs:
- config_name: default
  data_files:
  - split: train
    path: viewer_train.jsonl
---
# Python Repair Lab

An original OpenEnv curriculum of 1,200 deterministic Python function-repair episodes: 12 problem families, four distinct bug patterns per family, and 25 seeded case sets per pattern. There are 151,780 executable checks across the episodes. These are 48 repair patterns with data variants, not 1,200 unrelated algorithms. Tasks cover interval algorithms, rolling calculations, weighted statistics, stable deduplication, Unicode run-length encoding, Luhn checksums, edit distance, meeting scheduling, percentiles, FIFO inventory accounting, CSV parsing and shortest paths.

Source: https://github.com/louistiti/openenv-python-repair

Public image: `ghcr.io/louistiti/openenv-python-repair:v2`

Arena selection: 50 representative task IDs in `curriculum.json`, covering all 48 bug patterns. Only these declared tasks train in Arena; the other 1,150 public rows are available for reproduction and other training runs. Row count alone does not imply an Arena score. Original v1 image and release remain available.

Dataset: https://huggingface.co/datasets/Louistiti/openenv-python-repair

## Contract

OpenEnv is pinned to `86a180ede21e044f7929b9a7783ad83aa67d83a3`. Image platform is linux/amd64. Server starts without environment variables, secrets, external files or volumes, as non-root, on 0.0.0.0:8000.

Reset with `{"task_id":"moving-sums","seed":42}`. Task IDs are in tasks.json/tasks.jsonl. Each observation supplies the task instruction and initial buggy solve function. Actions are `{"operation":"write","code":"def solve(...): ..."}`, `{"operation":"test"}`, and `{"operation":"submit"}`. Write replaces source; test reports at most three failures; submit grades and terminates. Maximum 12 calls. Set finish_action to `{"operation":"submit"}` in Arena. No imports/I/O/private attributes; ordinary Python builtins and container/string methods are allowed.

Terminal reward is fraction of deterministic cases passed, including nonmutation checks. Intermediate rewards are zero. Invalid source, missing solve, nonfinite outputs and timeouts score zero. Reset clears code/state. Each WebSocket connection has an isolated environment. Pinned SDK HTTP routes are stateless; stateful episodes use /ws with raw action data.

## Execution and limitations

AST restriction and builtin allowlisting are defense in depth, not a general-purpose secure Python sandbox. Code executes in a fresh isolated-interpreter subprocess with 2 CPU seconds, 3 seconds wall time, 256 MiB address-space cap on Linux and descriptor/file/core limits. The outer container sandbox is the isolation boundary. No grading credentials exist. Gold source files are public for audit/replay but excluded from the runtime image. Deterministic public cases can be overfit; this is a training curriculum, not a private benchmark or evidence of Arena performance. Luhn positive/negative cases and percentile boundaries are balanced to avoid skewed easy rewards.

## Reproduce

```
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python generate_expanded.py
.venv/bin/python -m pytest -q test_environment.py test_curriculum.py
.venv/bin/uvicorn server:app --host 0.0.0.0 --port 8000
.venv/bin/python replay.py http://127.0.0.1:8000
.venv/bin/openenv validate --url http://127.0.0.1:8000 --level runtime --json

docker build --platform linux/amd64 -t ghcr.io/louistiti/openenv-python-repair:v2 .
docker run --rm -p 8000:8000 ghcr.io/louistiti/openenv-python-repair:v2
```

requirements.txt locks dependencies from a Python 3.11 environment. Local v2 checks: 1,214 tests passed, 1,200/1,200 task oracle/floor/reset replays passed, official OpenEnv runtime validation 6/6 passed. All correct reference repairs score 1.0 and every broken starter scores below 1.0. Regeneration reproduces all data-file hashes exactly. Linux image replay reports and digest are published by GitHub Actions. No Arena admission, training or private evaluation result is claimed until a real submission completes.

## Dataset and provenance

The dataset viewer explicitly loads `viewer_train.jsonl` as the `train` split, rather than inferring splits from the repository's test code or validation reports. It contains the same 1,200 episodes and 151,780 checks as canonical `tasks.jsonl`. Each row has task_id, family, bug_pattern, case_seed, prompt, starter, split, arena_selected, num_cases and cases_json. The arena_selected column identifies the 50 tasks declared for Arena. `cases_json` is a lossless JSON string because different tasks use different nested argument and answer types; decode it with `json.loads`. Run `python prepare_viewer.py` to regenerate the viewer file. The viewer representation preserves the canonical executable cases exactly.

All task instructions, starters, generators and reference implementations were created for this repository. No imported benchmark or private evaluation data is included. tasks.jsonl has one training task per line with task_id, prompt, starter, executable argument/expected-value cases and split. See generate_expanded.py and generate_tasks.py for deterministic seeds and curriculum construction, curriculum.json for the 50 selected IDs, server.py for rewards, solutions.json for the oracle and replay.py for runtime verification. Base seed is 20261008; cohort seeds increment by 7919. All repository code/data are MIT-licensed; OpenEnv is a separate BSD-3-Clause dependency. This is synthetic programming data with no personal information.
