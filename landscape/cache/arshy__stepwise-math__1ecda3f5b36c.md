---
license: bsd-3-clause
pretty_name: Stepwise Math (OpenEnv)
tags:
- openenv
- reinforcement-learning
- math
- tool-use
- grpo
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

# Stepwise Math

An OpenEnv environment for RL on **multi-step math solved through a calculator tool**, built for [OpenEnv Arena](https://openenvarena-arena.hf.space/) (*Math & formal reasoning*).

- **Source:** https://github.com/moarshy/stepwise-math
- **Image:** `ghcr.io/moarshy/stepwise-math:v1` (linux/amd64)

## Episode

On reset the model gets one procedurally generated problem. **Every reset draws a fresh instance**, so parallel rollouts of the same task see different numbers and the model has to learn the method, not the answer. It then has up to 20 moves, each one JSON object:

| command | effect |
|---|---|
| `{"command": "calc", "text": "<expr>"}` | Exact calculator: `+ - * / // % **` and brackets, with fractions kept exact. Exponents are capped at 64, so huge powers must be reduced by reasoning. |
| `{"command": "submit", "text": "<answer>"}` | Ends the episode. Reward 1 if the value equals the exact answer (`14/24` = `7/12`), otherwise 0. |

Running out of moves scores 0. The reward is computed from the generated instance; no model acts as judge.

```
ENV   : A bag has 8 red, 5 blue and 7 green marbles. Two are drawn without replacement.
        What is the probability they are the same colour? ...
MODEL : {"command": "calc", "text": "(8*7 + 5*4 + 7*6) / (20*19)"}
ENV   : (8*7 + 5*4 + 7*6) / (20*19) = 59/190
MODEL : {"command": "submit", "text": "59/190"}
ENV   : Correct.            reward 1.0
```

## Tasks (v1)

There are 8 tasks: 4 families × 2 levels. They were chosen because Qwen3.8-27B with thinking off solves them sometimes but not always, which keeps GRPO groups mixed.

| task_id | What it asks | Qwen3.8-27B solved |
|---|---|---|
| counting-medium | Committees where two people refuse to serve together | 5/10 |
| counting-hard | Arrangements of a multiset of letters with a fixed first letter | 2/10 |
| modular-medium | a^n mod m with n of 100–999 (above the calculator's cap) | 3/5 |
| modular-hard | Last 2–3 digits of a^n with n of 1000–9999 | 1/10 |
| sequences-medium | Sum of the terms of an arithmetic sequence inside a range | 2/5 |
| sequences-hard | n-th term of a second-order linear recurrence | 3/10 |
| probability-medium | Two dice, P(sum ≥ k) | 6/10 |
| probability-hard | Three marbles without replacement, P(all different colours) | 3/5 |

Solve counts are pooled over 1–2 calibration runs of 5 episodes each, with thinking off and an arena-style loop. Treat them as rough bands.

**Files**
- `data/tasks.jsonl`: one row per task, with an example question and answer.
- `data/samples.jsonl`: 20 seeded instances per task, for inspection only. The environment generates new ones at runtime.

Every generator's answer key is checked by an independent brute-force test (enumerating committees, permutations, dice and marble draws, and full big-integer powers) in the source repository.
