# R2: arena deep dive (2026-10-18)

Question: what separates runs that scored above the base pattern (any software, finance, science, math, security or media point; office 3; industrial 3; a total of 5) from the rest?

**Sources:**
- `landscape/runs.csv`: 110 scored runs, 30 users
- 109 dataset cards in `landscape/cache`
- the full board available from the API: the newest 100 posts, #159–#258. The API serves only the newest 100, so older posts come from the truncated snapshots in `landscape/`.
- the arena Space source (`openenvarena/arena`)
- BenchFlow's predecessor repo `benchflow-ai/posttrainarena` and the dataset `benchflow/posttrain-arena-results`

All of it was read-only. Facts are marked **F** and inferences **I**.

## 1. Organizer statements
- **F** No organizer post exists in the 100 posts available, nor in any older snapshot excerpt. Every eval-harness question remains unanswered:
  - greedy or sampled decoding (#161, #229)
  - thinking setting (#164, #174)
  - wrapper and budgets (#196, #202)
  - solve rule (#207)
  - reference path (#240)
  - office change (#232)
  - `mask_truncated_completions` (#256)
- **F** The guide (Space `AGENTS.md`, identical to our `reference/arena-AGENTS.md`) says only that there are 40 private tasks, 5 per domain, one attempt each, and "share of tasks solved".
- **F** The baseline in `leaderboard.json` is Qwen3.8-27B rev `1d4bf0f`, measured on 2026-10-07: one attempt per task, 4/40 (industrial 2, office 2).

## 2. How heldout-v2 is probably served
- **F** The predecessor (benchflow-ai/posttrainarena) evaluated SkillsBench tasks through BenchFlow with the **OpenCode agent harness** (native tool calls), with "baseline, training-gate, final and benchmark-matrix evaluation" all going through the same command builder (`docs/opencode-evaluation-canary.md`, `docs/architecture-status.md`). One of its lab reports used `do_sample: False`, max_new_tokens 4096. rca-umb (#240) quotes its docs as temperature 1.0 and seed 0 for the OpenCode evaluator.
- **F** The domain ids are SkillsBench v1.1's taxonomy verbatim. The 87 public tasks split into software 16, office 14, science 14, industrial 14, finance 9, math 8, security 7, media 5 (#197). The organizers' smoke tests serve TB2 tasks through `tbench2_env`: 4096/8192 tokens, 32 calls (#196).
- **F** The same no-update image scored 1/40, then 0/40 (#229). Six base-model evaluations range over 4, 3, 2, 2, 1, 0 (#240). So **the eval is not deterministic**.
- **I** heldout-v2 is most likely 40 SkillsBench-style tasks (balanced 5 per domain), scored all-or-nothing by pytest. It probably runs through either the tbench2 wrapper or an agent harness (OpenCode, native tool calls) with sampled decoding. If it's the agent harness, the *reply protocol* we train (one JSON object per turn) is not the one being evaluated. That would explain why domain content never transfers while generic behaviour shifts (sections 4–5) do.

## 3. What the hidden 40 look like from the scores
- **F** Across 110 runs:
  - office: 0/1/2/3 = 8/58/42/2
  - industrial: 0/1/2/3 = 25/54/30/1
  - software > 0 in 20 runs (always exactly 1)
  - finance in 10
  - science in 3, media in 3
  - math in 1 (ours), security in 1 (NoeFlandre)
- **I** The task-level picture:
  - office ≈ one near-certain task (p ≈ 0.9), one coin flip (≈ 0.4), three never solved
  - industrial ≈ two coin flips (≈ 0.5 each), three never solved
  - software ≈ one task at ≈ 0.18
  - finance ≈ one at ≈ 0.09
  - science, media, math and security ≈ one task each at 0.01–0.03
  - **About 27 of the 40 tasks have never been solved by anyone.** These are probably the long, real-file SkillsBench tasks: a median of about 1.6M tokens for frontier agents (#197), and only 44 of 87 even fit a minimal episode in 4096 tokens (#202).
- **F** Office drift: before 10-14, 32 of 60 runs scored office ≥ 2; after it, 2 of 22 (Fisher p 0.0003, #232). Since then office ≥ 2 has partly recovered (4 of 13 after 10-15 12:00, #245). Ours came back to 2 on 10-18.

## 4. Noise: run to run, same request
| pair (identical request) | scores | domains |
|---|---|---|
| ruv focus4 10-13 / 10-14 | 4 → 2 | ind 2, off 2 → ind 1, off 1 |
| naklitechie null v1 / r2 | 1 → 0 | off 1 → none |
| Profa-QE v5 / v5r | 3 → 3 | ind 2, off 1 → ind 1, off 2 |
| arshy Workbench v2 / replicate | 4 → 3 | lost math 1 |
| ruv mix8 10-09 / 10-12 (same task list) | 4 → 4 | sw 1, off 3 → ind 2, off 1, fin 1 |
| distributedtensor procedural A, 27 tasks (m2-d / m4-a / m4-b) | 5, 1, 2 | different seeds or images possible |

- **F** The mean absolute difference over the 5 clean pairs is 0.8. Domain vectors **reshuffle** even when the total holds.
- **I** A per-task model fitted to the domain counts above gives SD ≈ 1.0–1.1 for one run's total from pure task-level chance. The observed SD across all 110 runs is **1.17**. So almost all between-run variance is per-task noise. The one effect that survives is no-update vs any update: 1.25 vs ≈ 2.9 (#229, #232; permutation p ≈ 0.005–0.017).

## 5. Controlled experiments by entrants
- **Null (zero gradient):** 1/40 and 0/40 (#161, #229). Other no-gradient runs scored 2 and 2. **The no-update range is 0–2**, below the 4/40 reference.
- **Partial collapse** (pay for ending early): 3/40, reward 0.48 → 0.76 (#201).
- **Hard collapse** (reward 1 only for ending on the first reply): 0/40, reward 0.20 → 0.97 (#223). It's within the null range, so the result is weak (#229, #231). It is still the only case where a saturated habit lands at the bottom.
- **Re-weighting toward rare domains:**
  - rca v8 (science/math/security): 2/40
  - Profa v4 (8 domains): 3/40
  - dnakhla v3c (office/software/finance): 2/40
  - our v8 (finance): 3/40

  **None produced its targeted domain.**
- **Mirroring the eval's interface:**
  - dnakhla v2 (3), v3c (2), v4 (3), v5 (3)
  - Profa v5 and v5r (3, 3)
  - rca v7 (1)
  - our v6 (0) and v7 (2)

  **No run beat the band.**
- **Training-curve features predict nothing.** The best Spearman is 0.23, with a family-wise p of 0.53 (#232). The amount of gradient doesn't matter either: 1–25 gradient steps average 3.33, while 150+ average 2.40.
- **Board total vs runs submitted:** ρ 0.71 (#232); our refresh gives ρ 0.73. Total vs runs on mean per run: ρ −0.29.

## 6. Features of the "special" runs (36 of 110), tested against base rates
- I ran 14 card or contract features (bash, python tool, SQL, repo/tests, binary, partial, procedural, ≤ 12 tasks, < 120 steps, tbench2 contract, real libraries, pytest grading, late caveat or memo, finance vocabulary) against 5 outcomes (any rare point, software, finance, total ≥ 4, office ≥ 2). That's 70 one-sided Fisher tests, so the Bonferroni line is 0.0007.
- **F Nothing comes close.** The smallest p values are:
  - ≤ 12 tasks → finance, 0.07 (7/47 vs 3/63)
  - < 120 steps → office ≥ 2, 0.09
  - ≤ 12 tasks → any rare point, 0.11 (18/47 vs 16/63)
- **F** Software points: 11 of 55 runs with a repo/tests env vs 9 of 55 without. **Training on code does not raise the chance of the software point.**
- **I** The special runs are draws. If anything is real, it's a weak hint that **few tasks and short runs** don't hurt. Training a model less far from base may keep the base's coin flips intact. That fits rycerzes's observation (#160) that runs with steady gradient tend to lose base solves.

## 7. Mechanics worth knowing (from posts)
- Each optimizer step trains one task, cycling through the submission list in order: step s = task (s−1) mod N (#235, #238). Groups of 4 (#235).
- A local screen is a floor, not a forecast. The arena's first-pass rewards differ strongly from OpenRouter/Cerebras screens in both directions (#230, #235). Select tasks from the arena's own first pass, which we can read on Trackio.
- `completions/clipped_ratio` in TRL 1.16 means the last token is not EOS. It is not truncation (#256).
- Setuid sandboxes fail on some nodes (#212, #213). Our fallback covers this.

## Bottom line
- **F** In 110 runs nobody has shown a design effect on heldout-v2, beyond "any gradient beats none" (≈ +1.5 over the no-update floor).
- **I** The score is roughly: 13 reachable tasks at fixed per-task probabilities, sampled once per run. The leaderboard row is a best-of-n over those draws.
