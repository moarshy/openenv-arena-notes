---
license: apache-2.0
task_categories:
- reinforcement-learning
tags:
- openenv
- workbench
---

# Workbench Gym tasks

36 train tasks for the Workbench Gym OpenEnv environment. Each task id is a family and a level, for example `sw2-L3`. Each reset draws a fresh instance.

Each episode gives a small workspace of text files. The agent reads them with `ls`, `read`, `grep` and `py` (stdlib Python on a copy of the files), then submits a JSON answer. Reward is 1.0 when every answer field is correct, and below 0.5 for some correct fields.

## Domains

- cybersecurity
- finance-economics
- industrial-physical-systems
- mathematics-or-formal-reasoning
- media-content-production
- natural-science
- office-white-collar
- software-engineering

## Calibration

Each task was played with Qwen/Qwen3.8-27B (thinking off) through the Hugging Face router. `stage_a` and `stage_b` count solves out of episodes. Tasks were kept in the mixed-outcome band.

## Files

- `tasks.jsonl`: task ids and calibration counts. No answers are included.

Source and reference solvers: https://github.com/NoeFlandre/openenv-arena/tree/workbench-gym-v1/workbench-gym
