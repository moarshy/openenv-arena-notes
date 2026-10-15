# OpenEnv Arena notes

A public lab notebook from competing in [OpenEnv Arena](https://openenvarena-arena.hf.space/), by [arshy](https://huggingface.co/arshy).

In the arena, you build an RL *environment*. The arena trains Qwen3.8-27B on it with a fixed GRPO recipe for about 4 hours, then scores the trained model on 40 hidden tasks across 8 domains. This repo records what we built, why, what the arena said, and what everyone else is doing.

## Results

| version | idea | score (untrained: 4/40) |
|---|---|---|
| [v1 Stepwise Math](versions/v1-stepwise-math.md) | Exact-answer math with a calculator tool | 2/40 |
| [v2 Workbench](versions/v2-workbench.md) | Workspace habits via `run_bash`: grep big workspaces, catch hidden caveats, write exact output files | 3/40 |
| [v3 Workbench v2](versions/v3-workbench-v2.md) | + code repair (hidden tests), 12-action episodes, harder caveats | 4/40, incl. a math point (the first of any run) |
| [v4 replicate of v3](versions/v4-replicate.md) | Identical resubmission to test noise | 3/40, math back to 0: the math point didn't replicate |
| [v5 Workbench v3](versions/v5-workbench-v3.md) | Software on real libraries + industrial (reflow audit, plant tuning) | 3/40: industrial kept at 2 for the first time; no software point |
| [v6 T-Desk](versions/v6-tdesk.md) (**pre-registered**) | Same tasks, but the organizers' `tbench2_env` interface and budget: tests whether the interface mismatch is why nothing moves | **0/40**: against the hypothesis; at the no-update floor even though training reward rose |

Details: [RESULTS.md](RESULTS.md).

## Findings so far
- **The hidden test looks SkillsBench-shaped.**
  - An earlier commit of the arena Space named its reference benchmark `skillsbench-balanced40-v2`.
  - [SkillsBench](https://github.com/benchflow-ai/skillsbench)'s taxonomy matches the arena's 8 domain IDs exactly.
  - The organizers' OpenEnv adapter uses `run_bash` + `submit`.

  In SkillsBench, "math" means operations research, planning and Lean, solved in a sandbox. That is not arithmetic, which explains why arithmetic environments (including our v1) don't move the math column. See the [v2 record](versions/v2-workbench.md).
- **Format, not reasoning, is the main failure with thinking off.**
  - In our calibration, most failed episodes were a sentence of prose before the JSON action, unescaped quotes from shell commands inside JSON, or the model's native `<tool_call>` format leaking out.
  - Under strict parsing, medium and hard solve rates dropped from about 5/8 to about 2/8.
- **Learning signal is necessary but not sufficient.** Several runs (ours included) had healthy mixed reward groups and still didn't move the hidden score.
- **Long multi-turn episodes cost training budget.** v2 got 104 optimizer steps; v1 got 257.
- **Across 35 scored runs, only 3 beat the untrained model, and none by more than 1 task.** See [landscape/](landscape/).

## Research
- [2026 RL environment research, applied to the arena](research/2026-10-13-rl-env-research.md)
- [Where everyone stands (2026-10-14)](landscape/analysis-2026-10-14.md)
- [Can an environment move the score at all? (2026-10-15)](landscape/analysis-2026-10-15.md)

## The environments
What each version tried, as pseudocode with example episodes: [ENVIRONMENTS.md](ENVIRONMENTS.md).

## How this repo works
- `versions/`: one record per submission, from [TEMPLATE.md](versions/TEMPLATE.md) (hypothesis → design → calibration → contract → training → result → lessons → next).
- `landscape/`: dated snapshots of every scored run and board post, plus `runs.csv`. Regenerate with `python3 scripts/study_board.py` (stdlib only; it reads the arena's public APIs and dataset cards).
- **Routine:** study the board before designing, record the version at submission, and complete the record when the score lands.

## Code
- [moarshy/stepwise-math](https://github.com/moarshy/stepwise-math) (v1)
- [moarshy/workbench](https://github.com/moarshy/workbench) (v2)
