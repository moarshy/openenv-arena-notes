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

# MiMo curriculum for OpenEnv

Twelve original tasks from [XiaomiMiMo/MiMo-V2.6-RL-oss](https://huggingface.co/datasets/XiaomiMiMo/MiMo-V2.6-RL-oss/tree/639865fd3374018d6cb29b9fb82dd531406fcf5f), served through one OpenEnv shell/finish interface. Nine are code tasks and three are terminal tasks. Problem statements, test patches, embedded test files and scoring rules are preserved. No LLM judge or external service credentials are required.

[Source repository](https://github.com/akseljoonas/mimo-openenv-software) · [Public dataset](https://huggingface.co/datasets/akseljoonas/mimo-openenv-software)

## Curriculum

`tasks.jsonl` records task identities, immutable upstream images, source positions and intended skills. `tasks/` contains the original records. The dataset viewer exposes the uniform task catalog; original code and terminal records retain their separate schemas. The selected tasks exercise:

- SQLGlot: BigQuery conditional counting and SQL dialect conversion.
- pandas: CSV string preservation and Excel append integrity.
- PYroMat: exact material lookup and boundary handling.
- pdfplumber: positional character deduplication.
- statsmodels: expanding-window regression before rolling estimation.
- MRI-NUFFT: multidimensional sampling-density compensation.
- libfmp: cost matrices and dynamic time warping.
- Camelot: table exports across text, workbook, database and archive formats.
- OpenSCAD: range parsing, AST semantics and derived artifacts.
- Authlib: explicit JOSE key inputs and security boundaries.
- Partitura: MusicXML-to-MIDI conversion and artifact consistency.

Selection favors a compact mix of data, document, numerical, media, CAD and security operations. It is a qualitative curriculum choice, not an empirically established optimum. Most tasks remain repository repair or implementation work; topic overlap does not demonstrate transfer to full benchmark workflows. The exact private Arena questions and task IDs remain unknown. Environment checks establish functioning graders, not model performance or an expected evaluation score.

## Runtime contract

Each task has a separate public `linux/amd64` image tagged `ghcr.io/akseljoonas/mimo-openenv-software:TASK_ID-v3c`. Submission references use immutable digests. The image starts its OpenEnv server on port 8000 without mounted files, credentials or additional environment variables. In a WebSocket session at `/ws`, `reset` accepts `task_id`; `step` accepts `{"operation":"shell","command":"..."}` or `{"operation":"finish"}`. Standalone HTTP `/reset` and `/step` are stateless in the pinned OpenEnv release.

Reset restores the original workspace snapshot. The build removes its temporary workspace after archiving it to avoid retaining a second prepared copy in the final image layer. Shell commands start in the task's original working directory, run as UID 2000, last at most 60 seconds and return at most 12,000 output bytes. `finish` invokes the original grader and returns `done: true`; reaching 64 actions also grades. A terminal session returns its cached verdict until reset. The server, original task record and snapshot are inaccessible to the agent user. This is not a security boundary against every possible reward exploit in arbitrary upstream repositories.

Code tasks use Xiaomi's published `OpenSourceCodeEnvironment` unchanged. Its original test patch is installed for grading; runtime verifier commands and patch writes run as UID 2000. Build preparation uses Xiaomi's existing Git-history stripping routine and setup assertion before snapshotting. This removes reachable future fixes in some original images without rewriting the task or grader.

Terminal tasks restore `/app`. Their original base64-encoded test files are decoded without modification, materialized in root-owned `/tests` only during grading and removed afterward. The original `test.sh` runs as UID 2000 outside the writable workspace. Its binary `/logs/verifier/reward.txt` is authoritative: ordinary pytest failure statuses (including collection errors caused by a broken solution) with reward 0 are valid, as is the original guard's exit 0 with reward 0. Missing/invalid verdicts, timeout or abnormal exit statuses are errors. Reward 1 requires exit 0. Original integrity guards remain enabled.

The adapter uses a separate Python runtime. Two terminal images need explicit dependency repairs outside `/app`: OpenSCAD needs Arpeggio 2.0.3; Authlib needs cryptography 46.0.3, cffi 2.0.0 and pycparser 2.23. These exact additions are declared in `task-dependencies.json`; task code and graders remain unchanged.

The Arena request allows 180 seconds for reset and 120 seconds for grading, with 64 tool calls, 32,768 completion/context tokens, 2 CPUs, 16 GiB of memory and a 10 GiB workspace. Code rollouts retain the earlier 1,200-second budget; terminal rollouts retain their original 900-second task deadline. Arena supplies outbound internet. The terminal records request offline operation, but this adapter does not enforce a network restriction; their original graders and the reference repairs run without external services.

## Pinned sources and ownership

- Dataset: `639865fd3374018d6cb29b9fb82dd531406fcf5f` (Apache-2.0).
- [MiMo-Agent](https://github.com/XiaomiMiMo/MiMo-Agent/tree/467f0a19016f0ac4d63b8d17a1f0da9ba07f232c): `467f0a19016f0ac4d63b8d17a1f0da9ba07f232c` (MIT).
- [OpenEnv](https://github.com/meta-pytorch/OpenEnv/tree/86a180ede21e044f7929b9a7783ad83aa67d83a3): `86a180ede21e044f7929b9a7783ad83aa67d83a3`, Arena's required revision.
- Python runtime base and task images are pinned by digest; adapter packages are pinned in `requirements.lock`.

The original code-task runner is Xiaomi's `recipes/code/mimoagent_runner.py` at [verl revision a2ad9f6](https://github.com/XiaomiMiMo/verl/tree/a2ad9f6160b03ff2d47e59832bfb6b289f37c917). XiaomiMiMo owns the published task and grader. This repository owns the OpenEnv transport, terminal reward-file integration, packaging and selection. Arena owns training, task scheduling and private evaluation; those implementations are not configured by this adapter. Upstream project licenses remain applicable inside each image.

## Build and verify

Install the pinned OpenEnv CLI. For a row in `tasks.jsonl`:

```sh
export DOCKER_DEFAULT_PLATFORM=linux/amd64
openenv build -t ghcr.io/akseljoonas/mimo-openenv-software:TASK_ID-v3c \
  --build-arg TASK_ID=TASK_ID --build-arg TASK_IMAGE=SOURCE_IMAGE_DIGEST
python verify.py IMAGE TASK_ID --dataset-type DATASET_TYPE \
  --solution solutions/TASK_ID.py --output evidence/TASK_ID.json
```

`verify.py` runs the image with 2 CPUs and 16 GiB, checks readiness and the OpenEnv endpoints, then replays real WebSocket episodes. Every image must pass untouched reward 0, reference repair reward 1, reset back to reward 0, stable terminal reward and workspace isolation. Code tasks additionally check absent future Git refs and unprivileged verifier Git hooks. Terminal tasks also check that an agent-introduced syntax error earns reward 0, hidden-test cleanup and rejection of a workspace tampering probe by the original guard.

Reference repair fixtures are solely for deterministic grader validation. They are excluded by `.dockerignore` and are never copied into the images or workspace snapshots. They are not training trajectories. No model trials or ablations are performed by this workflow.

The `Publish images` GitHub workflow builds each image on native Linux, performs these checks and publishes only successful images using short-lived GitHub Actions registry authentication. Submission is separate, limited to one accepted request per account per rolling 24 hours. The previous experiment schedule is paused and its variant requests are archived.

## Release status

All twelve final `v3c` images passed [native Linux CI](https://github.com/akseljoonas/mimo-openenv-software/actions/runs/37940898454), anonymous pulls and complete positive/negative/reset episodes: 159 checks in each pass. The largest image is 1.87 GB compressed; unique layers total 11.17 GB. Peak observed writable usage was 903 MB, within the requested 10 GiB workspace. The digest-pinned request is `submission.json`; evidence is under `evidence/v3/`. Publication and environment validation do not establish Arena admission or a benchmark score. Earlier `v3` tags are superseded; one exceeded the image-size cap. The final images use `v3c` tags and new digests. No v3 submission has been made yet.

The earlier eight-task [v2 run](https://openenvarena-training.hf.space/?project=akseljoonas&runs=03bfc81de59cf3e53b9e05d0) completed 77 optimizer steps and scored 4/40 on its private evaluation. This historical individual-run result is distinct from an account leaderboard's best-per-domain aggregate and is not a prediction for the new curriculum.
