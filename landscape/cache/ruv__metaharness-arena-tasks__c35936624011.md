---
license: mit
task_categories:
  - reinforcement-learning
language:
  - en
configs:
  - config_name: default
    data_files:
      - split: train
        path: tasks.jsonl
---
# MetaHarness Arena Tasks

Original synthetic procedural tasks across eight domains, generated from
https://github.com/ruvnet/metaharness/pull/383.
The files_json column preserves each virtual filename and content as lossless JSON.
These public seeds are training fixtures; held-out evaluation uses fresh instances.
Training runs the pinned container, not this JSONL. Explicit seeds replay inputs.
The container generates fresh variants for unseeded resets. The reward is a
deterministic semantic checker with bounded partial credit for correct sub-results.
Empty answers receive zero. Oracle correctness is not model performance.
No official evaluation, training improvement or leaderboard rank is claimed.
No private customer data or copied benchmark problems are included.

## Version

- generator_version: 2
- source commit: `4657e5b82e124917b01d79ee5e9de41badb48fda` (https://github.com/ruvnet/metaharness/pull/383)
- environment image (public, linux/amd64, anonymous pull):
  `ghcr.io/ruvnet/metaharness-arena@sha256:228329c4928eef054d6e1d3021c9867df416539d4d5e656cc760f97c17c9e35a`
- tasks.jsonl sha256: `ffa57cbf04758156b15d61662a8faa7f4129f938bdc21c023dc897330e771ed3` (768 rows, 2,471,014 bytes)
- previous generator_version 1 rows remain at revision `8323b7b221ea977d8fce4409973678a80e50fb77`.
