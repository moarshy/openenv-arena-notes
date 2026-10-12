# v1: Stepwise Math

| | |
|---|---|
| Submission ID | `stepwise-math-v1` |
| Submitted | 2026-10-10 12:48 (+08); validated 12:49; no GPU queue |
| Run | `5ac25542966872f3c530648e` ([dashboard](https://openenvarena-training.hf.space/?project=arshy&runs=5ac25542966872f3c530648e)) |
| Image | `ghcr.io/moarshy/stepwise-math@sha256:13ee4c2aa251548a12c6b9221e0150031ed4c6442193e6730deeb45fda63602c` |
| Dataset / source | [arshy/stepwise-math](https://huggingface.co/datasets/arshy/stepwise-math) · [github.com/moarshy/stepwise-math](https://github.com/moarshy/stepwise-math) |
| Arena result | **2/40** (Δ −2): office 2, everything else 0 |

## Hypothesis
- Math was at 0 for every entrant, so even +1 there would be a visible first.
- Math has exact verifiers, so rewards are clean.
- Multi-step problems that need a calculator should teach stepwise reasoning.
- What we did **not** know then: what the hidden "math" tasks look like.

## Design
- **Actions:** `{"command": "calc"|"submit", "text": ...}`.
  - The calculator is exact (fractions), with exponents capped at 64 so big powers must be reduced by reasoning.
- **Families:** 7 procedural families × medium/hard: word problems, fractions, counting, modular, sequences, algebra, probability. Every reset draws a fresh instance.
- **Reward:** binary, exact value match. 20 moves (raised from 10 after calibration).
- **Answer keys:** checked by independent brute-force tests.

## Calibration
Qwen3.8-27B via OpenRouter, thinking off, **strict** JSON parsing, 5 episodes per task. Total cost about $0.15.

| round | change | result |
|---|---|---|
| 1 | 14 tasks | 7 tasks at 5/5 (too easy: the calculator did all the work); 4 useful; 3 at 0/5 |
| 2 | Harder families, fractions dropped, move limit 10 → 20 | 6 useful; word problems still 5/5 |
| 3 | Divisibility, series sums, easier algebra | 8 useful |

- Failures were planning slips, not arithmetic. The model packed whole solutions into one invented formula.
- 5 episodes is noisy: counting-medium went 1/5 → 4/5 with an identical generator.

## Submission contract
- 8 tasks: counting, modular, sequences, probability × medium/hard.
- Limits: completion 4096, context 16384, 40 tool calls.
- Example actions: `calc 2+2`, `submit 0`.

## Training (dashboard screenshots)
- 257 steps.
- Smoothed reward about 0.4–0.6, no clear upward trend.
- `frac_reward_zero_std` about 0.3–0.6 (better than most runs).
- Entropy fell from 0.10 to 0.05: the model became more deterministic.

## Result
| domain | untrained | v1 |
|---|---|---|
| office | 2 | 2 |
| industrial | 2 | **0** |
| math | 0 | 0 |
| others | 0 | 0 |
| **total** | **4** | **2** |

## Lessons
- **Fact:** 8 of 19 runs at the time scored exactly 2. The result is within noise (one attempt per hidden task).
- **Fact:** a learning signal (mixed groups) was present, but the hidden score didn't move. rca-umb saw the same.
- **Inference, later strongly supported:** the hidden tasks are SkillsBench-style.
  - "Math" there means operations research, planning and Lean proofs, done in a sandbox, writing a solver and an exact output file.
  - Arithmetic puzzles behind a custom `calc` tool don't transfer to that.
- **Inference:** narrow training made the model more confident in our protocol, and it cost the two industrial tasks the base model solves (a common pattern across runs).

## Next
→ v2 Workbench: train workspace *habits* through a `run_bash` interface (the organizers' adapter shape), with hidden caveats and exact output files.
