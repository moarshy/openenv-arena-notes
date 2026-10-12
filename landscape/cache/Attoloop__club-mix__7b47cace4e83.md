---
license: apache-2.0
pretty_name: Club Mix
tags:
  - rl-environment
  - openenv
  - openenv-arena
task_categories:
  - reinforcement-learning
size_categories:
  - n<1K
---

# Club Mix

50 agentic tasks for the [OpenEnv Arena](https://openenvarena-arena.hf.space/), 10 from each of five
[Attoloop](https://huggingface.co/Attoloop) environments. Every task is a real working environment: the
model acts with shell commands inside the task's own container and is graded by the task's own verifier.

| Environment | Domain | What the model must do |
|---|---|---|
| cut-forge | Math & formal reasoning | Write a VeriPB proof that bounds the optimum of a pseudo-Boolean minimisation instance from both sides |
| table-press | Software engineering | Encode an HTTP/3 header trace in QPACK so two independent decoders reproduce it, in as few bytes as possible |
| sdtm-restoration-forge | Natural science | Find and restore destroyed cells of a clinical SDTM data pack using the CDISC CORE engine and cross-domain redundancy |
| shape-restore | Media & content production | Rebuild a font's damaged OpenType layout tables so HarfBuzz reproduces thousands of shaping records |
| dialect-recon | Software engineering | Write an interpreter for a hidden dialect of a language from its spec, examples and a metered probe |

The skills are general ones: read a specification, inspect the environment, write and run code, check the
result against the tools provided, and keep improving it.

## Interface

One episode is one task in a fresh container. The model replies with one JSON object per turn:

- `{"op": "run", "command": "<bash>"}` runs a command in the task's working directory (a fresh shell each
  time, at most 110 s, output cut to 2,000 characters) as the task's unprivileged user.
- `{"op": "submit"}` ends the episode. The task's verifier then runs as root, exactly as the task's
  Harbor verifier does, and the episode's reward is returned.

The first observation is the task's instruction.

## Reward

Each verifier reports a raw score in the task's own units: a proof's bound gap, an encoding's bytes,
cells still wrong, shaping mismatches or hidden programs matched. Many of these have no fixed ceiling, so
the raw score is mapped into [0, 1] with a hyperbolic calibration between two anchors per task:

- `worst`: the weakest submission that passes the task's gates (for example the shipped greedy proof,
  or a ledger that fixes nothing). It and anything below it scores 0; a submission that fails a gate
  always scores below it.
- `best`: the result of a frontier coding agent (gpt-6.1-sol, one attempt) on that task. It scores 0.4.

Between the anchors the reward rises linearly from 0 to 0.4. Above `best` it keeps rising toward 1.0
(0.8 at `best` + 3 × the gap between the anchors), so beating the frontier agents still pays.
`tasks.jsonl` lists every task's anchors, metric direction and image.

## Provenance

Tasks come unchanged from the environments' published Harbor datasets (task content, instruction and
verifier). Each image is the task's own environment image with its separate verifier's files added,
readable by root only until grading, plus the OpenEnv adapter at `/opt/club`.

## Limitations

- The original tasks are sealed offline. The arena sandbox has outbound internet that an unprivileged
  process cannot be denied; the adapter only points the usual proxy variables at a closed port. Some
  answers have public origins (for example the fonts and the clinical source data).
- One frontier attempt sets `best`, so anchors are approximate.

## Licences

Club Mix's tasks and verifiers are released under the Apache License 2.0 (`LICENSE`).
Third-party material in the tasks keeps its own licence; the notices are in `licenses/<environment>/`
and inside each image.
