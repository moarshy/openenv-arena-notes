---
license: mit
language:
- en
tags:
- openenv
- reinforcement-learning
- office
- data-analysis
pretty_name: Office Workflow Lab v1 Seed Previews
configs:
- config_name: default
  data_files:
  - split: train
    path: preview.jsonl
---
# Office Workflow Lab v1

Built by Leon AI (https://github.com/leon-ai/leon) with Louistiti.

Source: https://github.com/louistiti/openenv-office-workflow
Verification: https://github.com/louistiti/openenv-office-workflow/releases/tag/office-v1

36 synthetic seed previews: 12 task identities across six office/data workflow families, each shown at three reproducible seeds. The runtime image generates fresh input tables on reset. These are inspectable previews, not 36 independent programs or an empirical learning result.

Fields `files_json` and `expected_summary_json` are JSON encoded strings to keep the viewer schema uniform. `expected_report_csv` is the reference output for that seed. No real-world personal or business records are included. Public targets are not exposed in the runtime tool workspace. Arena runs only the immutable image, not this dataset.

Local validation: 507 tests including 480 independent SQL/Python comparisons, 24 real-network reference episodes, all six pinned SDK runtime checks. A deliberately capped local quantized-Qwen proxy smoke test completed two attempts with rewards 1.0 and 0.55625. This does not demonstrate training benefit or predict an Arena score. Linux container and anonymous image verification reports are in the source release when complete. No new Arena submission without approval of the exact request.
