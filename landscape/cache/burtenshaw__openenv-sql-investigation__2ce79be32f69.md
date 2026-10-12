---
license: mit
language:
- en
tags:
- openenv
- reinforcement-learning
- sql
- synthetic
size_categories:
- n<1K
configs:
- config_name: default
  data_files:
  - split: train
    path: tasks.jsonl
---

# OpenEnv SQL Investigation

Ten original procedural SQL investigation families teach joins, duplicate-safe aggregation, missing-data handling, weighted rates, temporal conditions, cohorts, anti-joins, ranking, and streak analysis. All data are synthetic and generated locally; there are no personal data or downloaded task assets.

The container generates a fresh in-memory SQLite database on every unseeded reset. `tasks.jsonl` contains one reproducible seed-42 instance per family, with instructions, schema, reference SQL and independently calculated Python answers serialized in `expected_rows_json`. `data/*.sql` reconstruct those public example databases. `source/` contains the environment, generator, tests and container recipe from [source commit 979946ef5fc6a5ad0bb661073af5e74a56127ea6](https://github.com/burtenshaw/openenv-sql-investigation/tree/979946ef5fc6a5ad0bb661073af5e74a56127ea6). Explicit reset seeds reproduce an instance; normal training samples fresh 63-bit seeds.

The policy sees only its question, schema, and its own query results. It can use read-only SQLite queries and has 12 actions. `op=submit` executes final SQL and ends the episode. Reward is **1** only for the entire correct result table, otherwise **0**; row order is ignored, duplicate multiplicity and column position matter, and numeric absolute tolerance is 0.0001. Python computes the expected rows independently of the submitted SQL. `op=finish`, budget exhaustion, or an invalid final query earns 0. There is no partial credit.

The public reference solutions are intended for audit and reproducibility. The runtime does not expose them through SQL tables or policy observations. SQL file access, writes, database attachment and extensions are denied; function, statement length, result length, execution-time and VM-operation limits bound each query.

All ten families are training tasks for one Arena policy. This dataset does not contain Arena's private evaluation tasks, and no private evaluation improvement is claimed. The common admission example finishes with reward 0; separate oracle tests demonstrate reward 1 for correct solutions.

Image: `ghcr.io/burtenshaw/openenv-sql-investigation:v1`. The Arena submission pins an immutable image digest. OpenEnv is pinned to `86a180ede21e044f7929b9a7783ad83aa67d83a3`; the image is self-contained and requires no secrets, files, volumes, GPU or external downloads at runtime.
