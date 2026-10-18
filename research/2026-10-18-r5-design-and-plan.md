# R5: the design space and a 10-day experiment plan (2026-10-18)

Research agent 5 of 5. Sources:
- our 8 runs and `landscape/runs.csv` (110 scored runs, 30 users, snapshot 2026-10-18 08:56)
- `reference/arena-AGENTS.md` (the arena's own instructions)
- the workbench code and submission files

Statistics below are computed from runs.csv; inferences are marked.

## 1. Facts from the arena docs that change how we design

- **The arena parses strictly.** Quoting the docs: "Each reply must be exactly one JSON object and nothing else … Any other reply ends the episode, and your environment still scores it (through `finish_action`)."
  - Our "lenient" calibration (36%) is therefore *not* what training sees. The strict number is: **15% for v4** and 17% for v7.
  - Most of our training episodes end on a format break.
- **Steps go round-robin over tasks.** Each optimizer step takes *one* training task in turn and plays 5 episodes. The first 4 valid ones train.
  - With about 110 steps and 9 tasks, each task gets about 12 steps (about 48 episodes). Task count therefore controls the *dose per task*.
- **The run is time-boxed**: 14,400 s on one H200. Shorter episodes mean more steps.
- **Per-task limits we've never used:**
  - `completion_tokens` / `context_tokens` up to 32,768
  - `tool_calls_total` up to 1,024
  - `memory_gib` up to 16, `workspace_gib` up to 44
  - `rollout_wall_s` up to 3,600
  - per-task `image` (up to 50 images), `split`, `server_port`
- **Fixed by the arena, not ours to set:** Qwen3.8-27B, GRPO, group size 5, learning rate, KL, thinking off, the eval harness and decoding.

## 2. The levers we control

| lever | options | what we have tried |
|---|---|---|
| Interface / schema | run_bash+submit; tbench2 (exec/write_file/evaluate); JSON-answer (single turn); file tools (ls/read/grep/write); SQL; calculator | run_bash (v2–v5, v8), tbench2 (v6, v7), calculator (v1) |
| Domain mix | 8 domains, or one domain only | broad mix; software-heavy (v5); finance (v8) |
| File types | CSV/MD/JSON (ours), XLSX, PDF, DOCX, images, logs, code repos | CSV/MD/JSON + Python repos only |
| Number of tasks (dose per task) | 1–50 | 8–11 |
| Difficulty / solve rate | strict solve 0–100% | strict 10–17% (format-dominated) |
| Reward shape | binary, partial, partial + all-pass, protected zero, success-gated efficiency, format reward | partial+all (v2–v5), binary (v6, v7), protected (v8) |
| Budgets | 4k–32k tokens, tool calls up to 1,024 | 12k/16k with 14 calls; 4k/8k with 32 calls |
| Episode length | 1 turn to many turns | 12 (or 20) actions |
| Instruction style | long/caveat-laden vs short; worked JSON examples; "N actions left" warnings | long + examples |
| Observation shape | truncated / untruncated, instruction repeated | 3k head+tail; tbench2 untruncated |
| Curriculum | fixed mix vs easy→hard levels (no ordering control: round-robin) | none |
| Images | one image vs per-task images | one |

## 3. What the landscape says about the levers (110 runs)

- **The per-run total:** mean 2.75, SD 1.17.
  - Distribution: {0: 4, 1: 11, 2: 29, 3: 36, 4: 24, 5: 6}.
  - The best single run is 5; 6 of 110 runs exceed the untrained 4/40.
- **No measurable lever.**
  - Score vs task count: ρ −0.09 (p 0.39).
  - Score vs training steps: ρ −0.09 (p 0.34).
  - Score vs card length: ρ −0.05.
  - Every interface and reward tag differs by ≤0.4 points (file-tools 3.06 vs 2.70 is the largest, n = 16; after about 15 comparisons this is noise).
- **No measurable user (skill) effect.** Within-user SD is 1.16, about the same as the total SD. ICC is 0.06, and a permutation test of user labels gives p 0.21. Inference: entrants' different designs do not produce different expected scores.
- **The eval drifts over time:**
  - Score vs date: ρ −0.20 (p 0.04).
  - Office vs date: ρ −0.26 (p 0.006).
  - Before 2026-10-14 01:00: 30/55 runs had office ≥2, mean 3.05.
  - After: 14/55, mean 2.45.

  So sequential comparisons are confounded. **Arms must be interleaved.**
- **Domain base rates (P>0 per run):**

  | office | industrial | software | finance | science | media | math | security |
  |---|---|---|---|---|---|---|---|
  | 0.93 | 0.77 | 0.18 | 0.09 | 0.03 | 0.03 | 0.009 | 0.009 |

- **The eval does respond to training, but only downward so far:**
  - no-update controls score 0–2 (mean ≈1.25)
  - collapse controls score 0 (rca-umb, and our v6)
  - trained runs score ≈2.97

  The +1.7 "generic gain" over no-update is the only training effect anyone has shown. Inference, untested: since replies are strict JSON, much of that gain may be **format discipline**.

## 4. Statistical power

The noise is SD ≈ 1.16 per run (within-user). Identical replicate pairs were (4, 3), (4, 2), (3, 3) and (1, 0), which gives an SD of about 0.9.

Minimum detectable effects on the **total** (80% power, α 0.05 two-sided):

| design | detectable effect |
|---|---|
| 1 arm × 5 runs vs field mean (2.75) | ±1.45 points |
| 1 arm × 10 runs vs field mean | ±1.03 points |
| A/B, 5 vs 5, interleaved | ±2.05 points |
| A/B, 3 vs 3 | ≈2.6 points (useless) |

**A rare-domain hit rate is far more powerful than the total.** Testing one domain's P(>0) against its base rate p0, one-sided α 0.05:

| domain base rate p0 | runs | hits needed | power if p1 = 0.4 | p1 = 0.5 |
|---|---|---|---|---|
| software 0.18 | 10 | ≥5 | 0.37 | 0.62 |
| finance 0.09 | 10 | ≥4 | 0.62 | 0.83 |
| science / media 0.03 | 5 | ≥2 | 0.66 | 0.81 |
| science / media 0.03 | 10 | ≥2 | 0.95 | 0.99 |

- **Conclusion:** a targeted environment for a domain with a *very low* base rate (science, media, math, security) is the only design where 3–5 runs can give real evidence. Two science hits in five runs would happen by chance with probability ≈ 0.008.
- **Lottery value for the row:** for us each extra run adds about 0.34 expected new domain points, mostly software at 0.18. A targeted environment that reaches p ≈ 0.4 in its domain is worth more than that, *and* is informative.
- **Training-dashboard metrics are secondary readouts only.** dnakhla found no curve feature predicts the score (best ρ 0.23). They are still essential for *validity*: did steps happen, what share of groups had zero variance, completion lengths, and step retries (dropped episodes). Read them via the Trackio API (`get_metric_values`).

## 5. Designs considered

- **A/B alternation on totals:** with 10 runs it only detects ≥2-point effects, which nobody has shown exist. Low learning value.
- **Kill test (a deliberately harmful arm):** largely done by the field already (collapse 0, no-update 0–2). Repeating it adds little. A **format-only arm** is the more useful "mechanism test": trivial tasks whose only lesson is strict one-JSON replies over long episodes. If it reaches the trained band (~3), the generic gain is format. If it stays at the floor, the gain comes from task content.
- **Dose-response:** steps and task count show no association (ρ ≈ −0.09). One dose probe that *concentrates* on 1–3 tasks (≈35–110 steps each) is the untested extreme. Every run so far, ours and the field's, spread 8–50 tasks thinly.
- **Rare-domain targeting with replication:** the strongest test per run, and it also feeds the row.

## 6. Three 10-day plans

**Plan A: rare-domain targeting (recommended).** Build one science environment shaped like SkillsBench: real-format files, a long rule-heavy instruction, an exact output file, many checks. Strict-JSON calibrated to 30–70%. Concentrate on few tasks; replicate; add one mechanism probe.
- Row expectation: +1 if science hits at least once, plus the lottery in other domains.
- Learning: a powered answer to "can a targeted environment move a rare domain?"

**Plan B: mechanism decomposition.** Run 1 format-only, 2 Workbench v4 (control), 3 concentrated pyrepo (3 tasks), 4 a 32k-budget long-horizon version, 5 a single-turn JSON-answer version, then replicates of whatever stands out.
- Learning: what the +1.7 generic gain is made of.
- Row: lottery only, about 0.34 points per run.

**Plan C: lottery (resubmissions).** About 3.4 expected new points over 10 runs, with the most likely gain software +1. Near-zero learning. The user has rejected this.

## 7. Recommended plan (A, with B's best probe folded in)

Decision rules are fixed in advance. "Hit" means that domain scores > 0.

| day | submission | question it answers | decision it informs |
|---|---|---|---|
| 1 | **Science-v1**: 3–4 science task families (kinetics/stoichiometry CSV, spectra/peak files, lab-protocol unit conversions), few tasks, strict-calibrated to 30–70% | Can a targeted environment hit science (base 0.03)? | Hit → replicate unchanged on day 3. Miss → still replicate once (power needs n ≥ 3) |
| 2 | **Format-only probe**: trivial tasks, long episodes, strict JSON is the only lesson | Is the generic +1.7 gain just format? | Total ≥3 → format is the generic gain: add format pressure to every later environment. ≤1 → content matters |
| 3 | Science-v1, **identical replicate** | Science hit rate, n = 2 | 2/2 or 1/2 → continue. 0/2 → look at the dashboard, revise to v2 |
| 4 | **Concentrated software**: pyrepo only, 3 tasks (~35 steps each) | Does dose concentration move software (base 0.18)? | Hit → replicate on day 6. Miss → drop concentration as a lever |
| 5 | Science-v1 (or v2 if day 3 failed) | Science hit rate, n = 3 | ≥2/3 → evidence (p ≈ 0.003). Write it up |
| 6 | Concentrated software, replicate | Software, n = 2 | 2/2 → evidence; 0/2 → stop software |
| 7 | **Best combination**: the science winner plus format pressure (and software if it worked), interleaved arms | Does combining dilute the targeted effect? | Pick the final design |
| 8 | Science-v1 replicate (interleaved with day 7's arm) | Science, n = 4 | Final science verdict |
| 9 | Day 7 design, replicate | Combination, n = 2 | Choose the design for any future days |
| 10 | Best design, final replicate, plus the write-up | Consolidate the evidence | Public post: what moved, what didn't, with pre-registrations |

**Guardrails for every day:**
- Pre-register before each submission.
- Strict-JSON calibration.
- Interleave arms because of the drift.
- Read the Trackio validity metrics (zero-variance share, retries) before interpreting the score.
- Count only pre-registered domain hits as evidence.
