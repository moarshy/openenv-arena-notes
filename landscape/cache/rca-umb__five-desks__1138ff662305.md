---
license: apache-2.0
pretty_name: Five Desks (OpenEnv environment)
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

# Five Desks

Five Desks is an [OpenEnv](https://github.com/meta-pytorch/OpenEnv) environment of procedurally generated,
multi-step "desk work" tasks in five domains: **finance, natural science, math, cybersecurity and media
production**. It was built for [OpenEnv Arena](https://openenvarena-arena.hf.space/), which trains
Qwen/Qwen3.8-27B with GRPO and evaluates it on private tasks. These five domains had no solved
evaluation tasks in earlier arena runs.

- **Image:** `ghcr.io/rca-umb/five-desks:v1` (linux/amd64, public). The pinned digest is recorded in the arena submission.
- **Source:** the full environment, tests and calibration scripts are in [`source/`](./source).
- **Tasks:** [`tasks.jsonl`](./tasks.jsonl) has one row per task id, with a worked example (seed 0) including the expected answer.

## What the environment teaches

Every episode is a small investigation: read a few short files, apply the rules they state, compute
carefully and submit a structured answer. The tasks reward:

- reading instructions and data closely, including decoys (reversed ledger entries, out-of-range assay
  readings, allowlisted scanners, near-miss IP addresses, dropped edit events);
- turning a word problem into the right formula (amortisation, Beer-Lambert calibration, exponential
  decay, inclusion-exclusion, CRT, closed-form recurrences, timecode arithmetic);
- using a calculator tool instead of mental arithmetic;
- replying with one valid JSON action per turn and finishing with a well-formed answer.

## Interaction

Action (one JSON object per turn):

| tool | fields | effect |
|---|---|---|
| `list` | | list the workspace files |
| `read` | `path` | show one file |
| `calc` | `expr` | evaluate one arithmetic expression (numbers, `+ - * / // % **`, `sqrt ln log10 log2 exp abs round min max pow(a,b,m) floor ceil gcd lcm comb perm factorial`) |
| `submit` | `answer` | submit an object with the requested keys; ends the episode |

The reset observation states the question, the files, the exact answer keys and the action budget (8 to 10
actions). Observations are `{"output": str, "steps_left": int}` and stay short (the longest file is under
4,500 characters). Unknown extra keys in an action are ignored. Running out of actions ends the episode with
reward 0.

Reset takes `task_id` (one of the ids below) and an optional `seed`. Without a seed every reset generates a
fresh random instance, so the five parallel rollouts of a GRPO group see different data.

## Reward

The reward is the mean score over the answer's parts (2 or 3 per task), in [0, 1]:

- numbers: correct within a stated tolerance (for example 1% relative, or USD 1.00 on a ledger total);
  strings such as `"$1,234.50"` are parsed;
- integers, ids and rule numbers: exact, with forgiving formatting (`"1,183"`, `"rule 20"`, `"003"`);
- timecodes: exact `HH:MM:SS:FF`;
- lists (allowed packets, subtitle cues): 1 for the exact set, otherwise 0.5 times the Jaccard overlap.

Ground truth is computed by the generator. The tests in `source/tests` recompute every answer
independently from the files the agent sees, over 40 seeds per task, and every one of 320 deliberately
corrupted answers was caught.

## Tasks and difficulty calibration

Each of 10 families has three levels (`-d1` to `-d3`). Difficulty was measured against the target model,
**Qwen/Qwen3.8-27B with thinking off** (served by HF Inference Providers through DeepInfra, temperature 1.0,
arena-style prompts: a system message with the action schema and JSON observations), over 8 fresh episodes
per task. The arena submission trains on the **18 ids with mixed outcomes** (mean reward roughly 0.2 to 0.8).
Saturated or near-zero ids are excluded because a GRPO group whose rollouts all score the same gives no
learning signal.

| task id | desk | Qwen3.8-27B mean (8 eps) | trained |
|---|---|---|---|
| finance-ledger-d1 | finance | 0.94 | |
| finance-ledger-d2 | finance | 0.94 | |
| finance-ledger-d3 | finance | 0.44 | yes |
| finance-loan-d1 | finance | 1.00 | |
| finance-loan-d2 | finance | 0.06 | |
| finance-loan-d3 | finance | 0.62 | yes |
| science-assay-d1 | science | 0.94 | |
| science-assay-d2 | science | 0.88 | |
| science-assay-d3 | science | 0.44 | yes |
| science-decay-d1 | science | 0.69 | yes |
| science-decay-d2 | science | 0.69 | yes |
| science-decay-d3 | science | 0.56 | yes |
| math-counting-d1 | math | 0.94 | |
| math-counting-d2 | math | 0.50 | yes |
| math-counting-d3 | math | 0.25 | yes |
| math-modular-d1 | math | 0.25 | yes |
| math-modular-d2 | math | 0.25 | yes |
| math-modular-d3 | math | 0.25 | yes |
| security-authlog-d1 | cybersecurity | 1.00 | |
| security-authlog-d2 | cybersecurity | 0.75 | yes |
| security-authlog-d3 | cybersecurity | 0.08 | |
| security-firewall-d1 | cybersecurity | 0.88 | |
| security-firewall-d2 | cybersecurity | 0.47 | yes |
| security-firewall-d3 | cybersecurity | 0.30 | yes |
| media-subtitles-d1 | media | 0.39 | yes |
| media-subtitles-d2 | media | 0.50 | yes |
| media-subtitles-d3 | media | 0.70 | yes |
| media-edl-d1 | media | 0.19 | yes |
| media-edl-d2 | media | 0.06 | |
| media-edl-d3 | media | 0.00 | |

Raw per-episode rewards and outcome types are in [`calibration/`](./calibration). Caveats: 8 episodes per
task is a small sample, the provider's serving stack may differ from the arena trainer, and about 1.4% of
provider responses came back empty and were retried. None of this measures a training gain or an
evaluation score.

## Families

- **finance-ledger**: net USD for one account over a period, from a multi-currency ledger with monthly FX
  rates and reversal entries; plus the largest outflow.
- **finance-loan**: level-payment amortisation; prepayments; rate resets with re-amortisation.
- **science-assay**: Beer-Lambert concentrations with blanks, duplicate readings, dilutions, a
  least-squares calibration through the origin, and out-of-range readings.
- **science-decay**: half-life from background-corrected count rates (mixed minute and hour units),
  predicted count rate, threshold time, or activity in Bq given detector efficiency.
- **math-counting**: inclusion-exclusion over divisibility with non-coprime divisors.
- **math-modular**: Chinese remainder systems (coprime and non-coprime) and affine recurrences mod a prime
  at very large n.
- **security-authlog**: find the brute-force compromise in an SSH log under a threshold and time-window
  rule, with noisy IPs, legitimate typos, slow guessers and allowlisted scanners as decoys.
- **security-firewall**: first-match firewall evaluation with CIDR blocks (including /20, /27, /29), port
  ranges and protocols; near-miss addresses just outside a block.
- **media-subtitles**: subtitle QC: reading speed (CPS), overlaps and minimum-gap violations.
- **media-edl**: edit decision list timecode arithmetic at 24, 25 and 30 fps, with ripple deletes.

## Run it

```sh
docker run --rm -p 8000:8000 ghcr.io/rca-umb/five-desks:v1
openenv validate --url http://localhost:8000
python source/scripts/replay.py --url http://localhost:8000
```
