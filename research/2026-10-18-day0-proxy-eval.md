# Day 0: local proxy of the hidden test (2026-10-18)

**Setup:**
- **Tasks:** 23 public SkillsBench v1.1 tasks, about 3 per domain (security 2), favouring tasks frontier agents solve.
- **Images:** built from the tasks' own Dockerfiles with skills removed. Every task's oracle solution scores 1 under its own verifier (syzkaller dropped: its oracle fails on arm64).
- **Model:** untrained Qwen3.8-27B via OpenRouter, thinking off, temperature 0.7.
- **Protocol:** the arena's published baseline (`skillsbench-balanced40-v2`):
  - actions `run_bash`/`submit`/`finalize`
  - strict one-JSON replies
  - 8,192 completion budget counting observations, 16,384 context, 128 tool calls
  - output cut to its first 8,192 characters
  - the verifier grades the sandbox however the episode ends
- **Runs:** 4 episodes per task, 91 episodes in total.
- **Code:** `competitions/openenv-arena/proxy-eval/` (`build.sh`, `oracle_check.sh`, `run_proxy.py`, results/).
- **Known leniency:** our budget check runs once per reply, so a few episodes ran up to about 9.7k.

## Results
**9/91 solved (10%).**

| domain | solved |
|---|---|
| office | 4/12 |
| industrial | 4/12 |
| science | 1/12 |
| finance | 0/12 |
| software | 0/11 |
| math | 0/12 |
| security | 0/8 |
| media | 0/12 |

**The proxy reproduces the arena's base pattern.** Office and industrial are reachable and nearly everything else is 0. That matches the untrained reference (industrial 2, office 2) and the field's per-domain base rates. This is the first evidence that the proxy is faithful.
- The solves were pdf-excel-diff 4/4, 3d-scan-calc 3/4, hvac-control 1/4 and mars-clouds-clustering 1/4.

## Where episodes died
- **No episode ever called `submit`** (0/91).
  - 48 ended on an invalid reply:
    - prose before the JSON: 21
    - reply cut off by the remaining budget, mostly long heredoc scripts: 15
    - broken JSON escaping (`echo "---"` inside the string, raw newlines): 10
    - `<tool_call>` tags: 2
  - 35 ran out of budget.
  - 7 called finalize, and 1 filled the context.
- **All 9 solves came from files written before the episode died.** Typically the model writes the output and then breaks format while summarising, e.g. "All targets are met… {".
- **Observations used 76% of all characters.** The mean budget used was 7,168 of 8,192, and 36/91 episodes `cat` a whole file within their first 3 actions.
- **There were 27 near misses** (some verifier tests passed). The other 55 failures passed no test.

## What this means for the design
1. **The binding constraints are format and budget, not knowledge.** Every episode ended by dying, never by finishing. A model that keeps the format, reads selectively and writes compact scripts would reach the answer-checking stage far more often.
2. **The highest-value habits:**
   - one clean JSON object every turn, including the last
   - escaping-safe commands: single quotes, heredocs written properly
   - small observations: `head`, `wc`, targeted `grep`, never a bare `cat` of a data file
   - short scripts that fit the remaining budget
   - write the output early, then `submit` cleanly
3. **File formats matter.** pdf-excel-diff, an xlsx/pdf task, was solved 4/4 because the image had the libraries. Finance's 0/12 is mostly cut-off scripts and budget, not missing tools.
4. **The proxy gives a 91-episode readout of a design's *habits* in about 25 minutes.** It cannot evaluate a trained model; we can't train 27B locally. But it can check that the habits we plan to train are the ones that kill episodes, and re-measure them on any model we can serve.
