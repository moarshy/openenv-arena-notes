# Two research streams (2026-10-16): latest RL-env research and the competition

Written after v6 T-Desk scored 0/40. Agents gathered the sources; numbers come from abstracts and board posts, and inferences are marked.

## Stream 1: arXiv and labs, Aug–Oct 2026
- **Verifier quality beats environment count.** River filters out low-quality environments and adds process-level regularisation. It uses under 30% of the TMax environments, with +106% RL gains on TB-Lite and +30% on TB 2.1 across 2B–27B models ([2608.22631](https://arxiv.org/abs/2608.22631)).
- **Gains that don't transfer usually mean reward hacking.** Policies exploit environment-specific tool schemas, grader parsing and task templates ([2608.00181](https://arxiv.org/abs/2608.00181)).
- **Transfer is linked to behaviours.** The same paper ties it to goal formation, keeping working state and verifying completion. 363 non-coding MCP tasks still gave +2.8 to +9.6 pp across tool, SWE and terminal benchmarks.
- **Large gains need a strong base and a shaped reward.** Kimi K2.7 Code reached TB 2.1 67.4 → 82.0 with reward = fraction of checks passed, **zeroed if any pass-to-pass check fails**. Steps per task fell 24–35% without any length penalty ([2610.00890](https://arxiv.org/abs/2610.00890)).
- **Difficulty that grows with the model helps.** Environment evolution gave +14–18 pp on TB 2.1 for Qwen3.6 models ([2609.04128](https://arxiv.org/abs/2609.04128)).
- **Efficiency rewards should only pay on success.** FrogNano uses a success-gated length penalty ([2609.07925](https://arxiv.org/abs/2609.07925)). HERO warns that blanket token penalties suppress turns the model needs ([2609.38885](https://arxiv.org/abs/2609.38885)).
- **Harness differences can swamp RL gains.** One study found a 7.1 pp spread between harnesses, against +0.5–0.8 pp from RL, and identical reruns flipped about 6% of tasks ([2609.04518](https://arxiv.org/abs/2609.04518)).
- **The platform's own warning.** posttrain.com says "a small change from a single run is not evidence of improvement". It lists a different setting (Qwen3.5-9B, 2,400 steps, lr 1e-6, KL 1e-3), possibly another challenge.

## Stream 2: the competition (83 runs, 30 users)
- **Top rows:** ruv 8; rca-umb and distributedtensor 7; akseljoonas, bochencs, NoeFlandre, Profa-QE and jjmachan 6; **arshy 5**. The best single run is still 5/40.
- **The best recent run is not a terminal clone.** distributedtensor scored 5/40 with procedural JSON-tool workspaces across all 8 domains:
  - families: late_caveat, false_premise, budget, spec_artifact, compute, repair
  - reward: 0.6 × share of parts + 0.4 × all correct
- **tbench2-shaped runs** scored 3, 2, 2 and **0 (ours)**.
- **Controls:**
  - no-update runs score 0–2 (mean ≈1.25); trained runs average ≈2.97
  - identical recipes: ruv 4 then 2, and ours 4 then 3
  - hard collapse: 0
- **dnakhla's analysis of all 82 runs' training logs:**
  - no curve feature predicts the score (best Spearman 0.23, p 0.53)
  - the total tracks *runs submitted* (ρ 0.71)
  - expected best-per-domain after 1–5 runs: 2.86, 3.90, 4.56, 5.02, 5.37
- **Office drift.** 32/60 runs kept office ≥2 before about 10-14 01:00 UTC, but only 2/22 after (Fisher p 0.0003). That may be a change on the eval side. It is unanswered by organizers, and our office also dropped (2 → 1).
- **Domains:**
  - software 1 in about 29% of runs, never 2
  - finance in about 11%
  - first science point: dnakhla v2 (CSV kinetics and stoichiometry), not repeated
  - math (ours) and security (NoeFlandre) once each
- **No organizer statements.** Questions about the eval's interface, decoding and solve rule remain open.

## Synthesis
1. **The interface experiment answered its question.** Copying the smoke-test interface does not help. Four runs tried it, and none beat the field.
2. **What the research says transfers is behaviour plus clean verification:** verify completion, keep state, don't break what works, and reward the fraction of checks with a zero-out for regressions. Env-specific schemas and templates invite hacking that doesn't transfer. T-Desk's rising training reward with a 0 score fits that.
3. **Our Workbench is the right family.** It is the closest to the best recent run (distributedtensor) and gave our best score (v3, 4/40).
4. **Volume matters for the row.** Under a draw model, more distinct non-harmful runs raise the best-per-domain total. Our 5 after 7 runs is on that curve.

## Recommended next step: Workbench v4
- Back to `run_bash`/`submit` with a tolerant schema.
- Breadth across domains, with families like distributedtensor's: late caveat, false premise, budget, spec artifact, compute.
- Lean toward the reachable new domains, **software and finance**.
- **Reward:** fraction of checks, **zeroed if protected checks fail** (a valid output schema, inputs untouched), plus a small *success-gated* efficiency bonus.
- **Calibrate** strictly toward 30–70% per task.
- **Submit daily** and treat each run as a draw. Replicate before claiming any effect.
