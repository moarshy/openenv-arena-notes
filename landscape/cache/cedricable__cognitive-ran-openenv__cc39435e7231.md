---
license: other
license_name: cognitive-ran-research-export
license_link: https://huggingface.co/datasets/cedricable/cognitive-ran-openenv/resolve/main/LICENSE.txt
task_categories:
- reinforcement-learning
language:
- en
tags:
- openenv
- synthetic
- cognitive-ran
---
# Cognitive RAN OpenEnv

This environment wraps the existing private Cognitive RAN project, not a new analytical implementation. The image contains 15 byte-identical deterministic analytics modules plus inert namespace initializers. CORE_MANIFEST.json records the original source commit, selected files, and hashes. The full repository, fleet configuration, credentials, real CSVs, evaluator internals, and Prime Agent runtime are excluded.

Twenty-four synthetic task ids: 18 train and six holdout across level shifts, transient spikes, missingness, directed topology reachability, lane capability scoping, and digest-mismatch abstention. Each dataset row contains the seed, instructions, and bounded manifest. No raw arrays or answer labels are included. Synthetic source generation and grading run inside the image; raw series are never exposed by its tools.

The image uses the existing anomaly.detector.detect, specialists.timerlm.skills, specialists.toporlm.skills.propagation_reach, and pipeline.domain_profiles.get_domain seams. Tools return bounded summaries with verified evidence handles. Every tool invocation verifies the synthetic source digest; mismatches deny analytics. Output remains recommendation-only: graph reachability is not fault propagation, correlation is not causation, and missing evidence is recorded rather than inferred.

The agent submits three report fields stated in the observation. Each strictly typed correct field earns one-third; all correct earns one. Finish and the 16-action budget yield zero. Canonical task ids generate deterministic comparable evidence; optional seeds provide alternative synthetic cases. Holdout ids are excluded from the Arena request.

Public image: ghcr.io/ricable/cognitive-ran-openenv:v1 (linux/amd64).
OpenEnv revision: 86a180ede21e044f7929b9a7783ad83aa67d83a3.

The public image necessarily exposes the selected deterministic source bytes listed in CORE_MANIFEST.json. Original source rights are retained; no open-source relicensing is asserted. The source repository remains private. No Qwen3.8-27B difficulty calibration, GRPO training gain, transfer result, operational RAN qualification, or private leaderboard score is claimed. Focused synthetic checks and protocol validation establish only their named local checks.
