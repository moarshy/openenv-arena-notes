---
license: apache-2.0
language:
  - en
tags:
  - openenv
  - reinforcement-learning
  - software-engineering
source_datasets:
  - XiaomiMiMo/MiMo-V2.6-RL-oss
configs:
  - config_name: default
    data_files:
      - split: train
        path: tasks.jsonl
---

# MiMo repair curriculum with observed reward variation

Five original tasks from [XiaomiMiMo/MiMo-V2.6-RL-oss](https://huggingface.co/datasets/XiaomiMiMo/MiMo-V2.6-RL-oss/tree/639865fd3374018d6cb29b9fb82dd531406fcf5f), packaged as immutable public OpenEnv images. Task statements, original test patches, grading commands and binary rewards are unchanged. The release changes the selected tasks only; it does not rebuild the images or change training parameters.

## Selection and evidence

The curriculum contains, in request order:

1. `format-code-task-001457`: Vault GitHub Action optional secrets input and token-only operation.
2. `format-code-task-000932`: fastavro JSON writer schema validation.
3. `format-code-task-000666`: PYroMat exact substance lookup.
4. `format-code-task-001926`: MRI-NUFFT cell-count sampling density.
5. `format-code-task-001886`: libfmp dynamic time warping.

The prior [12-task training run](https://openenvarena-training.hf.space/?project=akseljoonas&runs=1d61c4f2629479b7d6fcb20e) completed 84 optimizer steps. The available public logs cover steps 4–84: 77 of these 81 groups have zero reward and zero gradient norm; only four have mixed rewards and nonzero gradient norm. The earlier [8-task run](https://openenvarena-training.hf.space/?project=akseljoonas&runs=03bfc81de59cf3e53b9e05d0) has logs for steps 20–61 of 77 completed steps, with seven mixed-reward/nonzero-gradient groups. Missing steps are unavailable, not zero.

Selection uses those training signals, not private evaluation scores. Vault and fastavro correspond to reward-bearing ordinals 1 and 5 in the earlier run; PYroMat to ordinal 7 in the earlier run and 3 in the later run; MRI-NUFFT and libfmp to ordinals 7 and 8 in the later run. This mapping is inferred from the declared task order, documented turn-taking schedule and observed task counter. The public API does not expose task-labelled trajectories. The observations are few, dependent on evolving policies, and selected after observing outcomes; they are not an unbiased estimate of future success.

The hypothesis is that concentrating the four-hour allocation on tasks with demonstrated reward variation will produce more useful learning updates. It may overfit a narrow set and may not improve transfer. No model trials, ablations or proxy evaluations are used. Environment correctness is independently checked with deterministic repairs. Neither these checks nor training reward establish a private benchmark score or a score forecast.

`evidence/training-diagnosis.json` records logged coverage and per-ordinal summaries. Future progress should be assessed using training reward dispersion, gradient norm, loss, step timing and retries; only a completed Arena private evaluation establishes benchmark performance. This release is not evidence that the target score has been achieved.

## Runtime and ownership

`tasks.jsonl` names each public image digest, original record hash and image source revision. `tasks/` contains byte-identical original records. The first two images use adapter revision [a2ab08e](https://github.com/akseljoonas/mimo-openenv-software/tree/a2ab08e869901476efc007bca071d77b24600dee); the last three use [c72c753](https://github.com/akseljoonas/mimo-openenv-software/tree/c72c7536d677a9b56282b584f023c003200f8338). Each image serves the identical OpenEnv action/observation schema. These are existing public images, not new builds.

XiaomiMiMo owns the source tasks and original `OpenSourceCodeEnvironment` grader. This repository owns the OpenEnv adapter and curriculum selection. [Arena](https://openenvarena-arena.hf.space/AGENTS.md) owns model loading, task scheduling, GRPO optimization and private evaluation. Its documented runtime trains one policy on the task list for up to four hours on one H200; it samples five episodes per task step and selects the first four with valid rewards. The submission does not control the learning rate or total completed optimizer steps.

Each `linux/amd64` image starts port 8000 without injected secrets, volumes or arguments. In a WebSocket session at `/ws`, reset restores the original task snapshot; shell actions execute as UID 2000 in the task repository. `{"operation":"finish"}` invokes the unmodified original MiMo grader. Rewards are 0 or 1, terminal results are cached until reset, and verifier infrastructure errors are not converted to successful outcomes. Commands time out after 60 seconds and output is capped at 12,000 bytes. At 64 actions the adapter grades automatically. Future Git history was removed when the images were built using Xiaomi's existing setup routine.

The request retains each task's previous budgets: reset 180 seconds, rollout 1,200 seconds, verifier 120 seconds, 64 calls, 32,768 completion/context tokens, 2 vCPUs, 16 GiB memory and a 10 GiB writable workspace. OpenEnv is pinned to Arena's required revision `86a180ede21e044f7929b9a7783ad83aa67d83a3`. Original task-project licenses remain applicable within their images.

## Validation and publication

The repository's `verify.py` exercises the actual WebSocket path with an untouched task, a reference repair and a fresh reset. It also checks readiness, schema, original task identity, unprivileged commands, protected grader files, absent future Git history, stable terminal rewards and workspace isolation. The reference fixtures under `solutions/` are validation inputs only: they are not present in any submitted image and are never training trajectories.

Validation results and image manifests are recorded under `evidence/`. The full digest-pinned request is `submission.json`. Arena separately checks admission and runs training after acceptance. Publication, local checks, admission, training completion and private evaluation are distinct states. One accepted submission uses the account's rolling 24-hour slot. No message-board posting or recurring submission schedule is part of this release.
