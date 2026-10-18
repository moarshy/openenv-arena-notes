# R1: past and parallel competitions — what actually scored (2026-10-18)

Research agent 1 of 5. The question: in competitions where entrants contribute data, environments or recipes and the organizers train a fixed model, what did winners do, and by how much did they beat the baseline and the noise? Facts carry sources; inferences are marked.

## Facts

### NeurIPS 2023 LLM Efficiency Challenge ("1 LLM + 1 GPU + 1 day")
- **Setup:** fine-tune within 24 h on one GPU. The score was weighted 1/3 open tasks, 2/3 closed (hidden) tasks, to reward generalization ([leaderboard](https://llm-efficiency-challenge.github.io/leaderboard.html), [retrospective](https://arxiv.org/abs/2503.13507)).
- **What winners did:** both track winners first profiled base models and datasets, filtered contamination and non-English data, and **validated each data-mixture combination against the open evaluation**. They used stock libraries (LLaMA-Factory, QLoRA) and no custom training code ([retrospective](https://arxiv.org/abs/2503.13507)). In short, the work went into data curation plus a local proxy eval.
- **4090 winner (Birbal, Mistral-7B):** about 200–700k curated examples from 6 sources, with a reported 35% margin over the second-best submission ([Birbal paper](https://arxiv.org/abs/2403.02247)).
- **Common failure:** overfitting to the public tasks. The organizers concluded that benchmark-based evaluation of generative models is fragile ([retrospective](https://arxiv.org/abs/2503.13507)).
- **Routing:** some top entries routed task types (detected with a regex) to specialized models.

### Kaggle AIMO Progress Prizes 1 and 2
- **AIMO-1 (NuminaMath 7B TIR):** 29/50 on the private set ([HF blog](https://huggingface.co/blog/winning-aimo-progress-prize)).
  - Two-stage SFT: chain-of-thought first, then tool-integrated reasoning (TIR) matched to the eval's style of answer.
  - Self-consistency decoding with code execution.
  - **Four internal validation sets** (AMC, AIME, MATH) to choose models instead of trusting the public leaderboard ([repo](https://github.com/project-numina/aimo-progress-prize)).
- **AIMO-2 (NVIDIA NemoSkills):** 34/50. It used 540k problems with 3.2M long solutions, plus a merge of the CoT and TIR checkpoints ([Kaggle writeup](https://www.kaggle.com/competitions/ai-mathematical-olympiad-progress-prize-2/writeups/nemoskills-1st-place-solution-nemoskills), [paper](https://arxiv.org/abs/2504.16891)).

### Konwinski Prize (SWE-bench on issues collected after the freeze)
- **The winner scored 7.5%**, with a small open model and "smart strategies", and credited **context management** above all ([TechCrunch](https://techcrunch.com/2025/07/23/a-new-ai-coding-challenge-just-published-its-first-results-and-they-arent-pretty/)).
- **Leaderboard churn:** one team placed 4th on the public leaderboard and 15th on the private one ([writeup](https://www.kaggle.com/competitions/konwinski-prize/writeups/graphninjas-public-4th-place-private-15th-place-so)). With small, noisy hidden sets, rankings reshuffle.

### DataComp, DCLM and DataPerf (data-centric, fixed training recipe)
- **DataComp (fixed CLIP training, 38 tasks):**
  - Smaller, stringently filtered pools beat bigger ones.
  - Medium-scale average: 0.258 unfiltered vs 0.328 with CLIP-score filtering.
  - Top entries won with better *scorers* for filtering (DFN, BLIP-2 similarity, FLYT, which filters "like you test") ([DataComp](https://arxiv.org/abs/2304.14108), [FLYT](https://arxiv.org/abs/2503.08805)).
- **DCLM:** a model-based quality classifier gave +6.6 MMLU over the previous open-data state of the art at 40% less compute ([DCLM review](https://www.emergentmind.com/papers/2406.11794)).
- **DataComp-VLM (2026) is a counterexample:** no quality filter beat no-filter by more than about +0.8 pp; the *mixture* mattered more ([paper](https://arxiv.org/html/2606.28551v2)).
- **Data-Centric AI Challenge (precursor to DataPerf):** entrants raised accuracy from 64.4% to 85.8% by editing data alone. **Automated selection and augmentation beat manual label fixing**, contrary to what the organizers expected ([DataPerf](https://arxiv.org/abs/2207.10062)).

### BabyLM (three editions)
- **What won:** architecture and objective changes (LTG-BERT/ELC-BERT, distillation, diffusion masked LM) and more epochs.
- **What didn't:** curriculum learning was the *most popular* strategy every year, and repeatedly gave little ([findings 2023](https://aclanthology.org/2023.conll-babylm.1.pdf), [2024](https://arxiv.org/abs/2412.05149), [2025](https://www.researchgate.net/publication/397422593_Findings_of_the_Third_BabyLM_Challenge_Accelerating_Language_Modeling_Research_with_Cognitively_Plausible_Data)).

### Environment programs (no ranked contest)
- **Prime Intellect Environments Hub:**
  - Bounties are paid per environment, $100–5,000+; it has 400+ environments, then 1,000+ ([blog](https://www.primeintellect.ai/blog/scaling-environments-program)).
  - INTELLECT-3 trained and evaluated entirely on Hub environments ([report](https://arxiv.org/abs/2512.16144)).
  - There is no public "which environment moved the score" ranking.
- **OpenEnv hackathons (SF and India, 2026):** judged on demos and themes. The confirmed SF winner was a CUDA-kernel environment with real performance feedback ([Northeastern](https://siliconvalley.northeastern.edu/small-collab-leads-to-big-win-at-2026-openenv-hackathon-san-francisco/)). There's no hidden-test scoring comparable to the arena's.

### SkillsBench (the likely source of the arena's hidden test; BenchFlow)
- **Setup:** 87 tasks, 8 domains, binary deterministic verifiers ([paper](https://arxiv.org/abs/2602.12670), [repo](https://github.com/benchflow-ai/skillsbench)).
- **Curated Skills** (procedural packages in context) raise the pass rate from 33.9% to 50.5%.
- **Focused skills (≤3 modules) beat comprehensive documentation.**
- **Self-generated skills give about −1.3 pp.**
- **Software engineering gains the least** from skills (+4.5 pp), and 16 of 84 tasks get worse.
- **Harness matters:** gains differ by harness, with native skills integration giving the largest.

### What short RL on Qwen actually does
- **One-shot RLVR:** a single example took Qwen2.5-Math-1.5B on MATH500 from 36.0% to 73.6%, much of it format and elicitation ([paper](https://arxiv.org/abs/2504.20571)).
- **Spurious rewards:** **random** rewards gave +21.4 points vs +29.1 with true rewards on Qwen2.5-Math-7B, through GRPO clipping bias amplifying behaviours the model already prefers (code reasoning rose from 65% to over 90%). The effect is Qwen-specific ([paper](https://arxiv.org/abs/2506.10947)). Contamination is part of that story ([critique](https://arxiv.org/abs/2507.10532)).

### Measuring under noise
- **Signal and Noise (AI2):** decisions are reliable only when signal/noise is high. Remedies are selecting high-SNR subtasks, checkpoint averaging and continuous metrics ([paper](https://arxiv.org/abs/2508.13144)).
- **DataDecide:** two recipes can only be told apart when their gap exceeds the combined run-to-run noise ([paper](https://arxiv.org/abs/2504.11393)).

## Inferences for OpenEnv Arena (ours, not from the sources)
1. **The winning pattern everywhere is a local proxy eval close to the hidden test, plus selection against it.** Where winners are known (NeurIPS, AIMO, DataComp), nobody used the competition's own leaderboard as their main signal. We have been using the arena itself as our eval, at one noisy draw a day.
2. **Noise floor:** with 40 binary tasks at about 7–10% solve rate, one run's standard deviation is about √(40·0.08·0.92) ≈ 1.7 tasks. So a design must shift the expected score by about 3 or more to be visible in one run. Nobody has, and the field's run-to-run spread is consistent with pure noise.
3. **About 100 GRPO steps on Qwen mostly *amplifies existing behaviours*** (spurious-rewards and one-shot results). We can't teach a new skill in 100 steps. We can shift *which* behaviours the model uses on the hidden harness: verifying, writing the file, using code, format compliance.
4. **Binary hidden scoring rewards flipping near-miss tasks.** The only tasks a short run can flip are ones where the base model is near the boundary, with per-attempt p around 0.3–0.6. Tasks at p≈0 won't move. Targeting is about finding *those* task types.
5. **Domain or interface fidelity matters more than domain labels.** SkillsBench tasks involve real files (xlsx, pdf, docx, media) and rule-heavy instructions. Our Workbench uses CSV/MD, which may explain finance 0 despite a "finance" family.
6. **Curriculum-style tweaks have a poor record** (BabyLM), and so do tiny reward reshapes (DataComp-VLM null). Expect our reward variants to be null too.
7. **Leaderboard rows grow with draws** (Konwinski churn is the analogue). Without a proxy eval, extra runs only add lottery tickets.

## Three actionable ideas for the next 10 submissions
1. **Build a SkillsBench-shaped proxy eval before submitting anything.**
   - Use the public SkillsBench tasks and verifiers: run Qwen3.8-27B (thinking off) via OpenRouter, several attempts per task.
   - Measure per-task base p, and find the near-boundary tasks (p 0.2–0.6) by domain.
   - Use this proxy to pick designs offline. Spend arena slots only on designs that win the proxy by a clear margin.
2. **One behaviour per run, chosen from proxy failure analysis.**
   - Examples: "verify the output file against the stated schema before finishing", "compute with code, never by hand", "read every instruction file", "handle xlsx/pdf inputs with the right library".
   - Build training tasks that are file-type and harness siblings of the near-boundary proxy tasks, not of our CSV workbench.
   - Pre-register the expected domain flips.
3. **Plan for noise explicitly.**
   - Pair each new design with a replicate only when the proxy predicts a gain of 3 or more tasks.
   - Otherwise use slots for distinct behaviours, which gives more chances to collect rare-domain points honestly.
   - Report results against the 1.7-task SD, not raw totals.
