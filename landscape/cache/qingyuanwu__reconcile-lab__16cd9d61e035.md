---
license: mit
language:
- en
tags:
- reinforcement-learning
- openenv
- synthetic
pretty_name: Reconcile Lab
---

# Reconcile Lab

Nine procedural settings teach relational investigation in finance, science and office workflows. Every episode generates fresh synthetic records. The agent inspects a table schema, queries read-only SQLite, and submits a three-field numerical report. Inputs are original synthetic records and contain no personal data.

`tasks.jsonl` lists the nine training task IDs, families and levels. `examples.jsonl` provides 27 reproducible input instances, including briefs, columns, tables and output metric names. These are examples of the generator's distribution; training generates fresh inputs at reset. Three levels vary record counts and exception rules. Difficulty against the target model must be measured before claiming useful learning signal.

Each correctly computed report metric earns one-third of the terminal reward. Monetary and mean fields use an absolute tolerance of 0.011; integer counts match within 1e-9. Missing, non-finite, Boolean or string values earn zero for that field. An empty finish or the 24-action limit yields zero reward. The verifier independently recomputes values from input records using Python; it does not check a reference SQL string. Reference reports are not included in these files or the agent's accessible tables.

Source and reproduction instructions: https://github.com/QingyuanWuNothing/openenv-reconcile-lab

The runtime depends on OpenEnv revision `86a180ede21e044f7929b9a7783ad83aa67d83a3`. Validated linux/amd64 image: `ghcr.io/qingyuanwunothing/openenv-reconcile-lab@sha256:dd13c35036488a8ac6444a892095c1acdb225f03a783cc794f812b7e91811816`. Container validation: https://github.com/QingyuanWuNothing/openenv-reconcile-lab/actions/runs/37969746046 . The image is anonymously accessible, 173,872,395 compressed bytes in 10 layers. It passed all six pinned OpenEnv endpoint checks, 27 full-reward WebSocket episodes and terminal finish replays on all nine task settings. Unit and protocol validation establish environment correctness, not improvement in private tasks. Training completion and rising rewards are not leaderboard results. No evaluated result is claimed here.

Fresh anonymous-pull validation also passed: https://github.com/QingyuanWuNothing/openenv-reconcile-lab/actions/runs/37970096011 .
