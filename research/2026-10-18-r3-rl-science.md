# R3: the RL science. What can about 100 GRPO steps change in Qwen3.8-27B?

Research agent 3 of 5, 2026-10-18. Read-only. Facts carry sources. Lines marked **(inference)** are ours.

## 1. What the arena's recipe actually is
- **From the arena's AGENTS.md** ([openenvarena-arena.hf.space/AGENTS.md](https://openenvarena-arena.hf.space/AGENTS.md)):
  - GRPO on Qwen3.8-27B, one H200, at most 14,400 s.
  - Each optimizer step takes **one** training task and plays **5 episodes**. "The first four that end with a valid reward train the policy."
  - The score is the share of 40 private tasks solved, **one attempt each**.
  - Not published: LoRA vs full, learning rate, KL, temperature, thinking mode, the eval harness, and how the untrained reference was computed.
- Participants also report that the trainer template and the effective thinking config are unknown ([ruvnet PR #383](https://github.com/ruvnet/metaharness/pull/383)).
- **(inference) The scale is tiny.** About 100–120 steps × 4 graded episodes ≈ **400–500 episodes per run.** River used 400 steps × 32 prompts × 8 samples ≈ 100k episodes ([2608.22631](https://arxiv.org/html/2608.22631v1), App. A.2). The arena is about **200× smaller**.
- **(inference) Episodes that fail to end with a valid reward are dropped, not scored 0.** So budget-overflow or crash behaviour is never directly penalised; it just shrinks the group.

## 2. What short RL can and can't change
- **RL sharpens, it doesn't add.** RLVR raises pass@1 but lowers pass@k at large k. The solutions it reinforces are already in the base model's distribution ([Yue et al., 2504.13837](https://arxiv.org/abs/2504.13837); NeurIPS 2025 runner-up).
- **Very little information per episode.** A policy gradient carries about 1 bit per episode. LoRA at rank 1 already has more capacity than RL needs ([Thinking Machines, LoRA Without Regret](https://thinkingmachines.ai/blog/lora/); formalised at [richardli.xyz](https://richardli.xyz/post/information-bandwidth-rl/)).
  - **(inference)** About 400 episodes ≈ a few hundred bits. That's enough to shift a handful of high-prior behaviours, such as format, stopping and length, but not to teach skills.
- **Spurious rewards still "work" on Qwen.** Random rewards gave +21 pp on MATH-500 for Qwen2.5-Math-7B, and a format-only reward gave up to +50 pp on Qwen2.5-1.5B. Llama and OLMo don't show this. The cause is a GRPO clipping bias amplifying an existing prior ([Spurious Rewards, 2506.10947](https://arxiv.org/abs/2506.10947)).
  - **(inference)** On Qwen, any GRPO run moves behaviour *somewhere*. Some of the field's "trained vs no-update" gain may be content-free sharpening.
- **One example can be enough.** A single well-chosen example matched a 1.2k-example dataset (MATH-500: 36 → 73.6%). The best examples were picked by **high reward variance** during training ([One-shot RLVR, 2504.20571](https://arxiv.org/abs/2504.20571)).
  - **(inference)** Task *selection* for variance matters more than task count.
- **Entropy collapses within a few steps,** and performance plateaus when it does: R = −a·e^H + b ([Cui et al., 2505.22617](https://arxiv.org/abs/2505.22617)).
  - **(inference)** At 100 steps we may already be in the collapsed regime. Low-diversity outputs can hurt a one-attempt eval on unfamiliar tasks.

## 3. Failure modes specific to multi-turn GRPO
- **Turn collapse:** in a coding agent, turns fell 9 → 1 between steps 17 and 25, with commands moving into prose, reward down 10×, and KL up 150× ([LEGO-RL, 2608.17393](https://arxiv.org/pdf/2608.17393)).
- **Format deadlock:** if every member of a group breaks format, all get the same reward, the advantage is 0 and nothing is learned ([CIGPO, 2607.16244](https://arxiv.org/pdf/2607.16244)).
- **Template collapse:** fluent output that ignores the input; output length falls 5–66% ([RAGEN-2](https://ragen-ai.github.io/)).
- **Stopping too early:** baselines terminate incorrectly after a failed tool call, where RTPO keeps going ([2608.18682](https://www.alphaxiv.org/abs/2608.18682)).
- **Reading the signs:** fewer turns with rising reward is efficiency. Fewer turns with falling reward and rising KL is collapse.

## 4. Which behaviours transfer, with evidence
| behaviour | evidence | strength |
|---|---|---|
| Verifying completion | Appears after RL in base-vs-trained trajectories ([2608.00181](https://arxiv.org/abs/2608.00181)); verify-before-done predicts success, but **rewarding it directly didn't help** ([River](https://arxiv.org/html/2608.22631v1)) | correlational |
| Not repeating yourself | River's only useful process term: −0.05 per repetitive turn (Jaccard > 0.8 on command and observation). It raised gains by 106% on TB-Lite and 30% on TB 2.1 | **causal, ablated** |
| Goal formation, keeping state, goal stability | Non-coding MCP RL gave +2.8 to +9.6 pp on 5 external benchmarks, including SWE and Terminal, with no SWE training ([2608.00181](https://arxiv.org/abs/2608.00181)) | correlational |
| Not breaking things, deriving tests from the requirement | Kimi K2.7 with LoRA r32 and reward = share of checks, zeroed on pass-to-pass failure: TB 2.1 67 → 82, with 24–35% fewer steps ([2610.00890](https://arxiv.org/abs/2610.00890)) | strong, but 1,700 tasks and a 1T model |
| Cross-domain transfer | River trained on 2 domains; untrained domains gained +18.5 and +12.1 | causal |
| Skills/procedures in context | SkillsBench: curated Skills +16.6 pp; **self-generated Skills −1.3 pp** ([2602.12670](https://arxiv.org/abs/2602.12670)) | about the eval itself |

- **Schema overfitting:** agents overfit to standard JSON keys and degrade when the schema changes ([2607.01084](https://arxiv.org/html/2607.01084)). Randomising tool and parameter names during RL reduces it ([ToolRL](https://papers.nips.cc/paper_files/paper/2025/file/97c5b2707228e7e3fb67e4ecc2e0e607-Paper-Conference.pdf)).

## 5. The harness matters more than RL
- **Harness swings dwarf training gains:**
  - The eval harness moved the mean solve rate 4.3× (2.1 → 9.3%). The RL rule's effect was +0.25 pp, CI [−0.48, +1.02], which is smaller than seed variation ([2609.04518](https://arxiv.org/abs/2609.04518)).
  - Scaffold-only swings: TB2 69.7 → 77.0%, and up to 15 pp on SWE-bench Verified ([2605.23950](https://arxiv.org/html/2605.23950v1)).
- **Our own data:** strict vs lenient JSON parsing alone doubled the solve rate (15% → 36%, v8 calibration).
- **(inference)** The eval's parser and harness are unknown. Under that uncertainty, format robustness, meaning one clean JSON action and no prose or tags, is probably the biggest lever we have.

## 6. Why trained runs score below the "untrained 4/40"
Field: trained runs mean **2.75**, SD 1.17, n = 110. No-update controls: **0–2, mean ≈1.25**. Reference: **4**.

Testable explanations, ranked **(inference)**:
1. **Pipeline offset, not learning.** A zero-update run should equal the reference but scores about 1.25. So about −2.75 comes from the train→serve path: adapter merge, precision, template, thinking flag, or a different decoding path. BF16 training/inference mismatch is a known source of policy drift ([2510.26788](https://arxiv.org/abs/2510.26788)).
   - *Reframe:* trained runs gain about **+1.5 over the true floor**. Ours average 2.5, about +1.25.
   - *Test:* ask the organisers whether the reference was scored through the same serving path. Compare more no-update controls.
2. **The reference is one noisy draw.** With SD ≈1.2 per run, a single 4 is plausible from a true mean of about 2.5–3.
3. **Format and schema drift.** Training on one action schema (ours: `run_bash`; T-Desk: `action_type`) can conflict with the eval's schema. v6 (tbench2 schema, tight budget) scored 0.
4. **Entropy collapse and length change.** Shorter, more confident outputs can hurt unfamiliar tasks with one attempt.
5. **Dropped invalid episodes.** These bias training toward behaviour that only works within our budgets and limits.

## 7. Statistical power: why single runs can't teach us
- Run-to-run SD is about 1.17, so one run per arm gives an SE of the difference of about **1.66**.
- 5 runs per arm give about **0.74**; 10 runs per arm about **0.53**.
- **(inference)** To detect a +1 effect we need about 5–10 runs per arm. A 10-day plan can test **one** contrast well, or two weakly.

## 8. What maximises expected hidden pass@1 with our levers (inference)
Our levers: environment, tasks, reward, budgets, per-task limits.
- **Train generic, high-prior behaviours, not domain skills:**
  - one clean JSON action per turn
  - don't repeat commands
  - always write the output file before the budget ends
  - verify, then stop
- **Pick tasks for reward variance** (30–70% solve, one-shot RLVR style). Cut tasks that never or always solve: they produce zero-advantage groups and wasted steps.
- **Penalise repetition** (River's −0.05 per turn). It's the only process reward with causal evidence. A verification bonus doesn't help directly.
- **Make the schema robust:** vary or randomise action wording and observation formats across tasks, so the model learns the behaviour rather than our keys.
- **Don't let failures escape the reward:** design so episodes end with a valid reward (a graded finish_action) rather than crashing. Otherwise bad behaviour is dropped instead of penalised.
- **Keep the protected-check reward.** v8's total of 3 sits in the trained band, so it's not harmful, and Kimi's evidence favours it.

## Most actionable for the next 10 submissions
1. **A paired design, one contrast, five runs per arm.** For example, "format-robust plus repetition-penalty env" vs our v8 baseline, alternating days. Judge on the pooled mean with its CI, not on any single run.
2. **Build the "behaviour env":** high-variance, short tasks across domains. Reward = protected share of checks − 0.05 per repeated turn. Randomise action and observation phrasing. Make sure every episode ends in a valid reward.
3. **Quantify the pipeline offset:** post on the board asking how the 4/40 reference was served. Treat about 1.25 as the floor in every comparison.
