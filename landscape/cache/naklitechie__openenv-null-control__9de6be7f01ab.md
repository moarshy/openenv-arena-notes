---
license: mit
pretty_name: OpenEnv Arena null control
tags:
- openenv
- openenv-arena
- reinforcement-learning
- control
---

# OpenEnv Arena null control

This environment is a constant-reward pipeline control, not an entry. It teaches nothing on purpose.

Every episode has one step. Any action ends it with reward 0.5. All rollouts in a GRPO group get the same reward, so the advantage is zero on every step. The arena's public Trackio logs show loss 0 and grad_norm 0 on every zero-variance step (1,759 of 1,759 steps across 14 runs), so the gradient is zero on every step. Whether the recipe applies weight decay is not published.

The evaluated score of this run is one observation of the arena's train-and-evaluate path with no reward signal. It is not by itself a noise floor: one score cannot separate evaluation variability from changes the pipeline makes without a gradient. The prediction, registered before submission, is 2/40 with industrial 1 and office 1, the score of an earlier run that also logged zero gradient on every step. The control counts as valid only if its Trackio log shows reward 0.5, loss 0 and grad_norm 0 on every logged step.

## Interface

- Task ids: `null` (one task, `train` split). See `tasks.jsonl`.
- Action: one JSON object; `answer` is optional, any JSON value, and ignored; extra keys are accepted. A reply that fails the schema ends the episode and is scored through `finish_action`, which also returns 0.5.
- Observation: a one-line prompt; `done` is true after the first action; `reward` is 0.5.

## Reward

Constant 0.5. Nothing is checked.

## Image and source

- Image: `ghcr.io/naklitechie/openenv-null-control:v1` (linux/amd64; the submission pins its digest).
- Source: `source/` in this dataset (server, Dockerfile, locked requirements, replay script, tests), pinned to OpenEnv `86a180ede21e044f7929b9a7783ad83aa67d83a3`. Build from `source/` with `DOCKER_DEFAULT_PLATFORM=linux/amd64 openenv build -t <ref>`.
