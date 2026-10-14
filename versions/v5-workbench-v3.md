# v5: Workbench v3, "Software + Industrial"

| | |
|---|---|
| Submission ID | `workbench-v3` (drafted: `workbench/submission/v3.json`) |
| Submitted | 2026-10-14 20:57 (+08) by the backup scheduler (the in-session job died with the session); run `440e6b0af5fd9120581da5c7`, 121 steps |
| Image | `ghcr.io/moarshy/workbench:v3` (`sha256:a2425f8b…905c`, public) |
| Arena result | **3/40** (Δ −1): **industrial 2**, office 1, software 0 |

## Hypothesis
**From the landscape (55 runs):**
- Software is the most commonly *gained* domain (15/55 runs), and we have never scored it.
- Industrial: the base model solves 2 of 5, but every one of our runs kept at most 1.
- Both would lift the row from 4/40 to 6/40.

**From the research:**
- The hidden software tasks are "fix or complete an unfamiliar multi-file project under strict hidden tests".
- The 5/40 runs used real libraries.
- The base-solved industrial tasks are probably "short handbook + data + formula + exact JSON".
- Narrow single-family training erodes other habits, so mix and replay.

## Design
**Interface fixes:**
- Two worked JSON examples in the first observation.
- Output capped at 3,000 characters, keeping the head *and the tail* (errors usually come last).
- A "2 actions left" warning.

**pyrepo (software), on real libraries:** toolz, boltons, tabulate, inflection (BSD/MIT), vendored with their own test suites.
- A catalogue of **103 validated bugs and blankable functions**, built by running the real suites about 1,000 times. Each entry breaks 1–12 test functions.
- Levels:
  - `bug1`: one bug, with a named failing test.
  - `bug2`: two bugs. The second is hidden from the visible tests and reported as a user issue.
  - `implement`: a function body is blanked, its tests are hidden, and the docstring is the spec.
- Grading: only the agent's edits to upstream library files are copied into a pristine copy, and the complete suite runs there as the sandbox user. Test edits, `conftest.py` and `pytest.ini` changes are ignored.
- 75/75 generated tasks verified: broken at the start, fixed by the upstream code.

**reflow (industrial): reflow-oven audit.**
- A 40–120 line handbook plus a few hundred thermocouple rows.
- The model computes preheat ramp, time above liquidus (with interpolation) and peak, then checks compliance.
- Traps: a handbook revision lowering the ramp limit, a run logged in °F, a thermocouple-selection rule, and a run with no data (null).
- Reference solver: 80/80. Every instance has both passing and failing runs.

**plant (industrial): heater-zone identification and PI tuning.**
- The simulator's parameters are sealed, so the model has to run a step test.
- `identify`: K, tau and theta.
- `tune`: also PI gains by the SPEC's lambda rule. The grader re-simulates the closed loop with hidden noise and checks overshoot ≤ 5% and settling.
- The rule-derived gains meet the spec on 60/60 sampled processes.

**Replay:** downtime-medium, expenses-easy and routing-medium, plus the synthetic repair family, so no single family dominates.

## Calibration
Qwen3.8-27B via OpenRouter, thinking off, lenient parsing, 8 episodes per task. Empty provider replies are now retried. Full solves:

| task | full | decision |
|---|---|---|
| pyrepo-bug1 | 5/8 | kept |
| pyrepo-bug2 | 4/8 | kept |
| pyrepo-implement | 1/8 | kept |
| repair-medium | 5/8 | kept |
| repair-hard | 5/8 | kept |
| reflow-easy | 6/7 | dropped: too easy |
| reflow-hard | 3/8 | kept |
| plant-identify | 2/8 | kept |
| plant-tune | 4/8 | kept |
| downtime-medium | 6/8 | kept (replay) |
| expenses-easy | 5/8 | kept (replay) |
| routing-medium | 7/8 | dropped: too easy |

**Calibration caught a task flaw.** Reflow first scored 0/8 on both levels: the cool-down passes back through the preheat temperature window, so the model reasonably used |change| and flagged every run. The handbook now defines preheat as the heating phase before the board first exceeds the upper temperature. After the fix, easy scored 6/7 and hard 3/8.

**The worst format failure seen:** a multi-line Python script inside an unescaped JSON string, wrapped in `<tool_call>`, which then degenerated into repeated `</parameter></invoke>`.

## Submission contract
- **10 tasks:** pyrepo-bug1, pyrepo-bug2, pyrepo-implement, repair-medium, repair-hard, reflow-hard, plant-identify, plant-tune, downtime-medium, expenses-easy.
- **Per task:** verifier 300 s (pyrepo runs a full library test suite), 14 tool calls, completion 12288, context 16384, 4 GiB memory, 2 vCPU.
- **Before submitting:** anonymous pull of the public image, `openenv validate` PASS, schema match, and 43/43 container checks.
## Training (arena dashboard)
- 121 steps.

## Result
| domain | untrained | v3 | v4 (rep) | **v5** |
|---|---|---|---|---|
| industrial | 2 | 1 | 1 | **2** |
| office | 2 | 2 | 2 | **1** |
| software | 0 | 0 | 0 | **0** |
| math | 0 | 1 | 0 | 0 |
| total | 4 | 4 | 3 | **3** |

The leaderboard row (best per domain) is now **office 2, industrial 2, math 1 = 5/40 (12.5%)**, up from 10%.

## Lessons
- **Industrial 2 for the first time in five runs.** That is consistent with the industrial families (reflow, plant, downtime) protecting the base skill, but it is one run. Office dropped to 1 in the same run; the only office task was expenses-easy.
- **No software point**, despite 5 software tasks (3 on real libraries). The hidden software tasks may be the non-Python or toolchain-heavy kind (Java or Maven migrations, JS performance, Scala translation), which our Python repair can't reach. Or single-run noise hid a small gain.
- **Pattern across our 5 runs:** the total moves between 2 and 4 regardless of design. What *does* move is *which* base task survives: industrial and office trade places. That fits the ±2 noise model and the "do no harm" picture: the env mostly shifts which of the four base solves survive.

## Next
- A replicate would show whether industrial 2 is real.
- To protect office, add an office replay at the same weight as industrial.
- Software needs either a non-Python family or acceptance that the hidden software tasks are out of reach in about 12 actions.
