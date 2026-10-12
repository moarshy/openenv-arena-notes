---
license: bsd-3-clause
pretty_name: Verified Compute Lab
tags:
  - openenv
  - reinforcement-learning
  - tool-use
  - agents
configs:
  - config_name: default
    data_files:
      - split: train
        path: tasks.jsonl
---

# Verified Compute Lab (Workbench v2)

An [OpenEnv](https://github.com/meta-pytorch/OpenEnv) environment for
[OpenEnv Arena](https://huggingface.co/spaces/openenvarena/arena): 14 procedural
task families across the eight Arena domains. Each task brings its own tools,
and every answer is checked by an exact verifier.

Each reset builds a fresh task: a question, a few files or an inbox, and a tool
list in the first observation. The action is always one JSON object:

```json
{"tool": "read", "args": {"path": "rules.md"}}
{"tool": "edit", "args": {"path": "lib.py", "old": "d -= 10", "new": "d -= 9"}}
{"tool": "grep", "args": {"pattern": "Accepted password", "path": "auth.log"}}
{"tool": "submit", "args": {"answer": {"start": "2026-10-14 10:30"}}}
```

The agent gets 16 tool calls. Code runs in a sandbox as an unprivileged user,
with CPU, memory and output limits.

| Family | Domain | Tools | What it takes |
|---|---|---|---|
| `code_repair` | software engineering | list, read, edit, write, run_tests | fix seeded bugs; at higher levels some bugs have no failing visible test and must be found from SPEC.md |
| `machine_schedule` | industrial | list, read, python | optimal job order for weighted tardiness, with setups, a maintenance window and cancellations |
| `inbox_scheduling` | office | list, read, python, list_emails, read_email | earliest meeting slot from constraints spread across emails, UTC offsets and corrections |
| `auth_forensics` | cybersecurity | list, read, grep (no python) | first successful login from a brute-force source, with decoys, password-using office staff, a rotating /24 and log rotation |
| `subtitle_sync` | media | list, read, python | retime an SRT file from sync points, frame-rate conversion and a scene insert |
| `loan_schedule`, `fx_ledger`, `xnpv_xirr` | finance | list, read, python | amortization with corrections, multi-currency ledgers, XNPV and XIRR |
| `reaction_kinetics`, `projectile_ode`, `stoichiometry` | natural science | list, read, python | fits and Arrhenius, Euler integration with drag and wind, yields |
| `constrained_count`, `graph_paths`, `recurrence_mod` | math | list, read, python | digit DP, shortest-path counting, matrix powers for huge N |

Task ids: `<family>` draws a difficulty from 1-4 on every reset; `<family>-d<k>`
pins difficulty k. Level 2 and up add messy real-world formats, and level 3 and
up add corrections memos that override the data.

## Reward

Grading is all-or-nothing: a multi-field answer earns 1 only when every field is
right. A local pilot found that partial credit let a small policy learn to guess
categorical fields (reaction order, limiting reagent) instead of working, so
partial credit was removed. `code_repair` keeps a share-of-bugs-fixed reward,
because every point needs a real edit; breaking a function that was correct
scores 0. Running out of tool calls, or `{"tool": "submit", "args": {"answer": {}}}`,
scores 0.

## Verification

- Every family has an oracle that is checked to score 1.0 for every difficulty
  and seed; empty and wrong answers score less. Agent-view solvers use only the
  tools and the prompt (Python through the sandbox, grep output, parsed emails),
  and they solve the new families on 40+ seeds each.
- 418 tests, including a regression test for a sandbox launch that could
  deadlock under threads (it no longer uses `preexec_fn`) and a test that
  guessing a categorical field earns nothing.
- The linux/amd64 image passes `openenv validate --url`, and a WebSocket replay
  of every submitted task passes against an anonymous pull on a native x86 host.

## Calibration

Qwen3.8-27B, thinking off, temperature 1.0, through Hugging Face Inference
Providers, with an Arena-style loop (one JSON object per reply; anything else
ends the episode). Three episodes per pinned task. The submission trains on the
29 tasks the model solved in 1 or 2 of 3 episodes, which cover all 14 families and
all eight domains. Per-task results are in `calibration_summary.json`.

## Local transfer experiments (honest null)

On one RTX 4090, Qwen3-4B was trained with GRPO (LoRA, a custom Unsloth trainer
with shared-weight vLLM; 80 steps of 16 episodes). Four families were held out
completely. Results on fixed seeds:

| | Base | Broad (10 varied families) | Narrow (7 v1-style families) |
|---|---|---|---|
| Own trained families | 0.11 | 0.16 | 0.19 |
| Held-out families (64 episodes) | 0.09 | 0.05 | 0.14 |

Both arms learned their training tasks, and reply-format failures dropped. Neither
showed a held-out gain beyond noise. Expect in-distribution learning; transfer to
unseen task types was not detectable at this scale.

## History

v1 (`verified-compute-lab-v1`, 17 tasks in finance, science and math) trained for
140 updates in the Arena and scored 4/40 on the private tasks, the same as the
untrained reference in every domain. v2 adds the five non-math families, per-task
tool sets, random difficulty per reset, all-or-nothing grading and the sandbox
fix.

## Links

- Image: `ghcr.io/rycerzes/openenv-arena-compute-lab:v2` (linux/amd64)
- Source: https://github.com/rycerzes/openenv-arena-compute-lab
- Dataset: https://huggingface.co/datasets/rycerzes/openenv-arena-compute-lab
- OpenEnv at `86a180ede21e044f7929b9a7783ad83aa67d83a3`, as pinned by the Arena

## Files

- `tasks.jsonl`: one row per pinned task id (56), with its domain, tools, whether
  it is in the submission, its calibration, and a seed-0 example prompt and oracle.
- `source/`: environment source, tests, solvers, the trainers and scripts.
- `calibration_summary.json`: per-task results against Qwen3.8-27B.
