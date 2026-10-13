# RL environment research (2026), applied to OpenEnv Arena

Three parallel research passes (Sonnet), each briefed with our learnings from v1–v3:
1. Environment and reward design
2. Transfer and evaluation noise
3. Multi-turn GRPO practice

The agents worked from search summaries, so verify any number before relying on it. Inferences are marked.

## What the literature says

**Breadth and environment quality**
- More distinct environments beat depth. In Agent World Model, 10 environments degraded held-out results, 100 helped, and 526 helped more ([2602.10090](https://arxiv.org/html/2602.10090v2)).
- Quality beats count. River found more than 60% of 15K synthetic terminal environments had defects ([2608.22631](https://arxiv.org/html/2608.22631v1)).
- **Skill2Env** is closest to us. It turned 3.4k agent skills into 8k terminal environments and reports +9 points on Terminal-Bench 2.1 for Qwen-3.8 27B after 150 RL steps ([alphaxiv](https://www.alphaxiv.org/abs/2609.reinforcing-agents-collective-skills)). That is our model and our budget.
- Procedural terminal tasks transfer only weakly. Endless Terminals improved in-distribution 10.7% → 53.3%, but only 1.1% → 6.7% on Terminal-Bench 2.0 ([2601.16443](https://arxiv.org/abs/2601.16443)).

**Difficulty and learning signal**
- The signal peaks at a 50% pass rate. With groups of 5 (inference): p=0.5 gives about 94% informative groups, p=0.2 about 67%, p=0.1 about 41% ([2605.05112](https://arxiv.org/html/2605.05112v3)).
- Zero-variance groups are about 40% of all groups ([2605.05802](https://arxiv.org/html/2605.05802)).
- "Template collapse" can happen while entropy looks stable (RAGEN-2, [site](https://ragen-ai.github.io/)).

**Format and multi-turn behaviour**
- Multi-step tool-use RL often fails on *format drift*, not capability ([2606.26027](https://arxiv.org/html/2606.26027v1)).
- Graded or capped format penalties beat harsh ones. Penalties alone teach inaction (RLVP, [2607.07435](https://arxiv.org/html/2607.07435v1)).
- Truncated episodes are often secretly successful: SWE-Master saw about 24% of truncated runs had already solved the task ([2602.03411](https://arxiv.org/html/2602.03411)).

**Reward hacking**
- RL agents stubbed tests and no-op'd filters ([Tmax](https://arxiv.org/pdf/2606.23321)).
- 25–28.5% of SWE tasks have tests that wrong patches pass ([2606.16062](https://arxiv.org/html/2606.16062v1)).
- Partial credit on gameable verifiers raised in-distribution scores and *lowered* held-out ones (River).

**Forgetting**
- On-policy RL forgets little by itself, and KL is a weak guard ([RL's Razor](https://arxiv.org/pdf/2509.04259), [2607.04364](https://arxiv.org/html/2607.04364)).
- Our lost industrial tasks may be mostly noise.

**Evaluation noise**
- Single-run pass@1 varies by 2–6 points ([2602.07150](https://arxiv.org/html/2602.07150)).
- Our arithmetic:
  - At 4/40, one run has an SD of about 1.9 tasks, so its 95% range is roughly 0–8.
  - Two independent runs need a gap of about **5 tasks** to differ clearly.
  - The null control (zero learning → 1/40) is about 1 SD of noise.
  - **Our 2 → 3 → 4 is not distinguishable from noise or from the untrained 4.**

## What does *not* apply to us (arena constraints)
- **We can't make JSON format errors recoverable.** The arena's trainer parses replies and ends the episode on an invalid one. We only see actions that parsed.
- **We can't track pass rates across resets.** Each episode runs in a fresh sandbox, so adaptive difficulty can't be learned online. Difficulty has to be set per task ID.
- **We can't evaluate trained checkpoints ourselves.** We never receive the weights, so "paired local evaluation of the trained model" is impossible. The only repeat measurement is another submission.

## Implications for v4 (our synthesis)
1. **Judge versions by training curves, not one leaderboard score.** Track the fraction of informative steps (`frac_reward_zero_std` low), the reward trend, and completion length. Use the leaderboard as a noisy draw, with replication when a result matters (e.g. the math point).
2. **Calibrate for the arena, not OpenRouter.** v2's arena reward (~0.8) far exceeded its offline calibration. Raise difficulty until offline full-solve is about 25–40%, which should land the arena near 50%.
3. **Go broader.** Move from 4 families to about 8, one or two levels each, about 12–16 tasks, all skill-shaped: long rules, data files, compute with code, exact output.
   - Priority: operations research and planning (math signal), industrial (protect the base skill), science (empty everywhere), finance.
4. **Make the interface easier to get right**, since we can't forgive bad JSON:
   - two worked JSON examples in the first observation
   - output cap reduced from 8,192 to about 3,000 characters (protects the 16k context; several episodes ran out)
   - a "2 actions left" warning
   - grading the files at the limit (already done)
5. **Partial credit only from objective checks**: values recomputed from the generator, never from files the agent can tamper with. Keep the all-pass bonus. Fuzz the verifier (empty, stub, partial outputs).
6. **No "verify before submit" bonus for now.** It is easy to game unless gated, and River's evidence warns against soft rewards.
