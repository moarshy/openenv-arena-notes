---
license: cc-by-4.0
language:
- en
tags:
- genai-otel-instrument
- genai-observability
- openenv
- reinforcement-learning
- opentelemetry
- synthetic-data
- trace-analysis
configs:
- config_name: default
  data_files:
  - split: train
    path: tasks.jsonl
---

# GenAI OTel Trace Lab tasks

Eight deterministic synthetic trace-analysis tasks shaped around the public genai-otel-instrument semantic conventions. Each row has a task prompt, synthetic span fixture, canonical interpretation, evidence span path, and reward definition. No production telemetry or private environment content is included.

The fixtures teach interpretation of GenAI usage and cost provenance, model deprecation, streaming latency availability, degradation events, multimodal capture metadata, and embedding operations. Attribute names and conventions follow the public SDK documentation; all trace IDs, values, span trees, and scenario narratives are synthetic. Private environments informed only the general design goal of evidence-grounded diagnosis; no private traces, prompts, task wording, outputs, or implementation details were copied.

The environment gives 0.5 for the exact normalized interpretation label and 0.5 for the exact ordered evidence span IDs. Inspection actions are nonterminal and unshaped. Fixtures are mirrored in the environment image; runtime does not download this dataset.

## Challenge reference

Built for the [OpenEnv Arena challenge Space](https://huggingface.co/spaces/openenvarena/arena) and its [live board](https://openenvarena-arena.hf.space/). Arena submissions reference a public linux/amd64 OpenEnv server image on Docker Hub or GHCR and include the server schema, task IDs, and example actions. This dataset is a companion collection of synthetic scenarios; the environment image embeds its fixtures and does not download this dataset at runtime.

The tested public environment image is [kshitij190/trace-path-lab:0.1.0](https://hub.docker.com/r/kshitij190/trace-path-lab). It serves /health and /schema and passed the pinned OpenEnv validator.

The public challenge artifacts are grouped in the [OpenEnv Arena: GenAI OTel Trace Lab collection](https://huggingface.co/collections/kshitijthakkar/openenv-arena-genai-otel-trace-lab).

Public schema reference: [genai-otel-instrument semantic conventions](https://mandark-droid.github.io/genai_otel_instrument/reference/semantic-conventions/).