# v3: Workbench v2 ("do no harm, gain one")

| | |
|---|---|
| Submission ID | `workbench-v2` (planned) |
| Submitted | not yet |
| Run | |
| Image | `ghcr.io/moarshy/workbench:v2` (`sha256:66dab881…341d`) |
| Dataset / source | [arshy/workbench](https://huggingface.co/datasets/arshy/workbench) · [github.com/moarshy/workbench](https://github.com/moarshy/workbench) |
| Arena result | |

## Hypothesis
- **Fact:** all three 5/40 runs kept the untrained model's 4 (industrial 2 + office 2) and gained exactly one task. They used 12 tasks of realistic code or log work.
- **Fact:** both of our runs lost industrial tasks.
- **Fact:** v2 got only 104 steps, and its rewards were high early (about 0.8, with several all-correct groups).
- **Bet:** more *useful* optimizer steps, plus software-style repair work, keeps the base skills and may add one task.
  - Shorter episodes → more steps.
  - Harder tasks → fewer all-correct groups.

## Design changes from v2
- `MAX_STEPS` 20 → **12**. 12 steps kept 39/43 successful calibration episodes.
- **Medium levels get two caveats:**
  - downtime: micro-stop + limit
  - expenses: 2 of cap / tier / FX
  - routing: 2 dispatch notes
- **New family `repair` (software):**
  - Fix a 7-module Python billing package to match SPEC.md and CHANGELOG.md.
  - Bug catalogue: half-up vs floor, `>` vs `>=`, tax scale, coupon/tax order, inclusive dates, zero padding, ceil vs floor periods, case-insensitive units, tie-break.
  - Visible tests catch exactly one bug.
  - Hard: the changelog overrides the spec, plus a decoy (an inclusive `+1` that looks like a bug).
  - Hidden-test grading: cases run in a subprocess as the agent user. Expected values stay server-side, and a nonce frames the results.
- **Planned task list:** 12, likely dropping downtime-easy (7/8, too easy) and keeping the rest. To be finalised after calibration.

## Calibration
Qwen3.8-27B via OpenRouter, thinking off, lenient parsing, 12 actions, 8 episodes per task. About 2.2M tokens, roughly $0.7.

| family | easy | medium | hard |
|---|---|---|---|
| downtime | 4/8 | 3/8 | 5/8 |
| expenses | 4/8 | 1/8 | 1/8 |
| routing | 7/8 (dropped) | 5/8 | 4/8 |
| repair | 2/8 | 2/8 | 4/8 |

**Of 45 invalid replies:**
- 15 were broken JSON (mostly unescaped quotes)
- **11 were empty provider responses** (not the model)
- 9 were prose only
- 6 had raw newlines (a lenient parser accepts these)
- 4 were `<tool_call>` wrappers

So calibration understates success. v2's arena training reward (about 0.8) was well above its calibration too.

## Submission contract
- **11 tasks:** all except routing-easy.
- **Per task:**
  - reset 180 s; rollout 900 s; verifier 120 s; tool 120 s
  - **14 tool calls** (the environment allows 12 actions)
  - completion 12288, context 16384
  - 4 GiB memory, 2 vCPU
- Example actions: `ls /app`, then `submit`. Finish action: an empty `submit`.
- Before submitting: an anonymous pull of the public image, `openenv validate` PASS, schema match, and all 29 container checks passed.
## Training (arena dashboard)
## Result
## Lessons
## Next
