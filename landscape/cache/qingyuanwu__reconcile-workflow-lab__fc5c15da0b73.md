---
license: mit
language:
- en
tags:
- openenv
- reinforcement-learning
- agentic-workflows
- grpo
pretty_name: Reconcile Workflow Lab — Eight Domains
---

# Reconcile Workflow Lab

A self-contained OpenEnv environment with 48 original synthetic tasks: six per domain, covering all three difficulty levels. Each frozen identifier selects the same case across fresh Arena containers and repeated rollouts. Selection happens offline using training-only base-model trials. The runtime needs no external controller, credentials, downloads or additional configuration.

| Domain | Agent work | Verified outcome |
| --- | --- | --- |
| Software engineering | Inspect a small repository, repair code, run regression tests | Executed repaired behavior on independent regression cases; fresh test result |
| Industrial and physical systems | Diagnose sensor evidence, adjust controls, simulate | Stable recovery while respecting physical and operating constraints |
| Natural science | Implement a reproducible analysis or design controlled kinetics experiments | Analysis agrees with records, or hypothesis predicts evidence after controls and repeated assays |
| Office and white-collar work | Combine dependencies, calendars and resources; dispatch work | Executed workflow satisfies resource, ordering and deadline constraints |
| Finance and economics | Investigate revisions, currencies and exceptions; reconcile records | Reconciliation and executed calculations agree with underlying transactions |
| Math and formal reasoning | Transform equations or construct an exact feasible solution and dual certificate | Executable exact checks establish the required mathematical claim |
| Cybersecurity | Diagnose a deliberately flawed sandbox policy, repair it, rerun access checks | Legitimate access works and prohibited access fails under regression checks |
| Media and content production | Edit a cut list and captions, assemble and render an asset | Rendered content, timing, format and technical constraints all pass |

Agents use `inspect`, `patch` and task-specific `run` tools, then `commit`. Reward is **1 only when every behavioral requirement passes and the verified process result is fresh**; otherwise 0. Existence of an artifact is insufficient. Modifying work after verification invalidates that verification. `finish` ends the episode with zero reward.

## Learnability and diversity measurements

`standalone-bank-selection.json` reports training-only reward balance, same-case variation, format and budget failures, and a balanced sampling comparison. Four independent model responses per case distinguish variation within a case from variation between cases. Selection preserves a domain mean in [0.375, 0.625] when reachable, jointly targets the global mean closest to 0.5, then favors clean within-case reward-pair contribution per charged token (pairs involving format or budget failure contribute zero, while every charged token counts as cost). This is a sampling heuristic, not a measurement of gradient magnitude or training gain.

`standalone-bank-validation.json`, when present, reports fresh independent model decodings on the frozen selection and baseline. Independent structural holdout cases are reported separately and never determine selection. Equal domain quotas, all levels, skill coverage and observed workflow variation are diversity proxies. They do not establish transfer to Arena's private evaluation. No local GRPO gain or private-evaluation improvement is claimed.

## Release

- Image: `ghcr.io/qingyuanwunothing/openenv-reconcile-lab@sha256:1c6bccf895a91bea68de8c47ce216340a1bdd03794931e70f97703bfb44a5176`
- Source: https://github.com/QingyuanWuNothing/openenv-reconcile-lab/tree/37bb03829d7e47b953e06086fcbc598b37b83735
- Runtime and bank revision: `332d6340e931db752db95a7cbc8e1175cf626c3325b8db29c1622db63a0f9028`
- SDK: OpenEnv `86a180ede21e044f7929b9a7783ad83aa67d83a3`
- Calibration model: Qwen/Qwen3.8-27B, revision `1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0`, thinking disabled, temperature 1.0
- Episode limits: 32 actions, 8,192 generated plus post-reset observation tokens, 16,384 context tokens

The user authorized publication of runtime generator and verifier code. The trusted server owns protected files; restricted agent programs execute as UID/GID 10001 and cannot use files, imports or networking. The image excludes reference solutions, author policies, tests, grading fixtures, model traces and credentials. This dataset exports only task metadata, information visible through the agent's tools, provenance and aggregate measurements.

The environment uses simplified synthetic workflows. Actual cross-domain generalization is assessed by Arena after an official run; preparation checks are not evaluation scores.
