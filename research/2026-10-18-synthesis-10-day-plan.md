# Synthesis of five research streams, and a 10-day plan (2026-10-18)

Sources: r1 past competitions, r2 arena deep-dive, r3 RL science, r4 hidden test, r5 design and power (files in this folder).

## What the five agree on
1. **The eval is strict, and most episodes die before any answer is graded.**
   - The arena guide says a reply must be exactly one JSON object; anything else ends the episode (r4, r5).
   - The published baseline protocol (`skillsbench-balanced40-v2`, r4):
     - 8,192 completion tokens, counting observations; 16,384 context; 128 tool calls
     - temperature 0.7, thinking off
     - the organizers' adapter is `run_bash`/`submit`, truncating output to the first 8,192 characters
   - Under it, 35/40 base episodes ended on format or budget.
   - dnakhla: 46/47 untrained losses ended before an answer.
2. **Content doesn't transfer, but training does help a little.**
   - Every domain-targeting run missed its domain: ours, rca, Profa, dnakhla (r2).
   - The only robust effect: any training (≈2.9) beats no updates (≈1.25). The amount of training doesn't matter (r2, r3).
3. **About 100 GRPO steps shift habits, not skills.**
   - Learning is about 1 bit per episode, over about 450 episodes.
   - RL sharpens what the base already does.
   - On Qwen even random rewards help (r1, r3).
   - So the target is the habits that block solves: format, budget economy, file-format handling (r4).
4. **Our training never matched the eval's rules.** We used 12k tokens, 3,000-character head-and-tail truncation, `/app`, and CSV/Markdown only. The eval likely uses 8k counting observations, head-only 8,192 characters, `/root`, and xlsx/docx/pdf with openpyxl, pdfplumber and LibreOffice (r4).
5. **Noise dominates.**
   - Per-run SD is about 1.2–1.7.
   - The eval drifts down over time.
   - Single runs can't separate designs. Use replicates, and compare against the **same-day field runs**, about 10 per day, as a free control that has drifted the same way (r2, r3, r5).
6. **Winners measured locally** (r1). We can't train a 27B locally, but a local proxy (public SkillsBench tasks under the eval rules, untrained Qwen via OpenRouter) shows *where* episodes die, so we can choose what to train.

## Decision
One direction: **"Eval-rules desk" (v9)**. Train under the eval's real rules, on short near-miss tasks including binary office formats, with a reward that pays for staying alive and economical.

**v9 compared with v6** (the tight-budget failure):
- The interface is the organizers' `run_bash`/`submit` (Workbench's shape), not tbench2.
- The budget is 8k counting observations, not 4k.
- Every episode ends with a valid reward, so failures are scored 0 rather than dropped.

## 10-day plan
- **Odd days:** identical v9 replicates, giving 5 runs. Compared with the same-day field mean, that detects about +1.5.
- **Even days:** single-factor probes. Each probe is a lottery ticket for the row and gives a mechanism readout from the training dashboard.

| day | submission | question | decision it feeds |
|---|---|---|---|
| 0 (no slot) | Local proxy: about 24 public SkillsBench tasks × 4 episodes under the eval rules, untrained Qwen | Where do base episodes die (format / budget / file format / wrong answer)? | Which v9 habits and tasks to build; the per-task near-miss list |
| 1 | v9 core | Does it train cleanly under the eval rules (mixed groups, few drops)? | Go/fix before replicating |
| 2 | Probe: format and economy only (trivial tasks, strict JSON, tiny observations) | Is the generic gain just format? | If ≥ v9, simplify toward format; if ≤1, content matters |
| 3 | v9 core, replicate | — | pooled n=2 |
| 4 | Probe: binary formats only (xlsx/docx/pdf tasks) | Do office/finance move? | Keep or drop binary tasks in v9 |
| 5 | v9 core, replicate | — | pooled n=3; interim look |
| 6 | Probe: concentration (3 tasks, about 35 steps each) | Does dose per task matter? | Task count for v9 |
| 7 | v9 core, replicate | — | pooled n=4 |
| 8 | Probe: repeat-turn penalty plus randomised tool wording (anti-overfit) | Does the transfer-oriented reward help? | Reward default |
| 9 | v9 core, replicate | — | **pooled n=5: verdict vs same-day field** |
| 10 | Best combination, plus a public write-up | — | What to carry forward |

**Verdict rule (pre-registered at day 1):** v9 is better than the field if its 5-run mean beats the same-day field mean by ≥ 1.5. Probes are read on their pre-registered domain or behaviour, and are not claimed from a single run.
