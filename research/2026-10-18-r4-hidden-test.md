# R4: Reconstructing the hidden test (heldout-v2), 2026-10-18

Research agent 4 of 5. Read-only research; nothing was submitted or published. **F** = fact (with source); **I** = inference.

## 1. How the arena scores, from primary sources
- **F. There is a pre-launch protocol for the public twin of the suite.** The arena Space's commit `d432332` ("feat: add measured baseline", 2026-10-07) published `baseline.json` for **`skillsbench-balanced40-v2`**, a public SkillsBench 40-task, 5-per-domain suite:
  - `temperature 0.7`, `context_tokens 16384`, `completion_tokens 8192`
  - `max_tool_calls 128`, `enable_thinking false`, `skill_mode "no-skill"`
  - `completion_budget_includes_observations true`, `attempts_per_task 1`

  Source: https://huggingface.co/spaces/openenvarena/arena (git history, commit d432332 `baseline.json`).
- **F. Base-model outcomes on that suite.** Qwen3.5-9B scored **0/40**. Outcome counts:
  - **"model emitted an invalid JSON action" 20**
  - **"observation exceeds token budget" 15**
  - "finished" 5

  So 35/40 episodes died before an answer was graded.
- **F. The selector also offered "Private tasks · heldout-v1".** The README says: "The benchmark selector separates this public no-skill evaluation from private held-out results." It was later reverted (`33b21f9`): the baseline became the untrained Qwen3.8-27B on the private suite, now heldout-v2 (4/40: industrial 2, office 2).
- **F. The arena guide's reply rule:**
  - *"Each reply must be exactly one JSON object and nothing else … Any other reply ends the episode."*
  - *"completion_tokens covers the model's tokens and every observation after the first … An observation that no longer fits ends the episode."*

  Source: https://openenvarena-arena.hf.space AGENTS.md, "How the model sees your environment".
- **F. The organizers' adapter for serving BenchFlow tasks over OpenEnv:**
  - actions are `type ∈ {run_bash, submit, finalize}` with `command` / `answer`
  - observations are `output`, `task_id`, `rollout_dir`, `last_returncode`
  - the reset message is *"Use run_bash to inspect and solve the task. Call submit with only the final answer."*
  - output is cut to **max_output_chars 8192, head only**, with the marker `[benchflow output truncated]`
  - `submit` writes the answer to `/workdir/answer.txt`, then runs the task's verifier for the reward
  - the sandbox user defaults to `agent`

  Sources: github.com/benchflow-ai/posttrainarena `pipelines/benchflow-task-posttrain/src/posttrainarena/benchflow_pipeline/openenv/models.py` and `openenv_service.py`; github.com/benchflow-ai/benchflow `src/benchflow/integrations/trl/spec.py`.
- **F. The previous PostTrain Arena evaluator ran OpenCode** with native tool calls at temperature 1.0 (rca-umb #240, citing posttrainarena docs). The architecture doc says competition recipes swap the eval list for "the organizer's sealed internal tasks". Source: posttrainarena `docs/architecture-status.md`.
- **F. No organizer has answered** the board questions:
  - #196/#197/#202/#240: harness, whether tasks are public or unreleased, `/root` vs shared sandbox, decoding
  - #kshitij: the solve rule
- **I. The most likely heldout-v2 setup:**
  - **unreleased SkillsBench-format tasks**, 5 per domain
  - served one-JSON-per-reply with `run_bash`/`submit`
  - 8,192 completion tokens (observations included), 16,384 context
  - output cut at 8,192 characters, keeping the head
  - binary pytest grading, no skills
  - task images with their own libraries

  Unknowns: whether the tasks are drawn from public v1.1 (unlikely, since "private"); the exact harness (it could be OpenCode).

## 2. What SkillsBench tasks look like (101 public packages: 87 in v1.1 plus 14 in tasks-extra)
Source: https://github.com/benchflow-ai/skillsbench (`tasks/*/task.md`, `environment/Dockerfile`, `verifier/test_outputs.py`).
- **F. Package shape.** Each task has:
  - a `task.md` with YAML metadata (category, difficulty, modality, interface, required_skills) and a prose instruction
  - its **own Docker image** with the needed libraries pre-installed (for example openpyxl 3.1.5, pandas, pdfplumber)
  - inputs under **`/root`**, outputs to absolute `/root/...` paths
  - a verifier `test.sh` that pip-installs pytest and runs `test_outputs.py`, giving **reward 1 only if every test passes**
  - an agent timeout of 900–1800 s
- **F. Instruction length:** median **177 words** (p25 124, p75 274; max 1,417). Median **6 tests** per task.
- **F. Category counts** (101 packages): software 21, office 17, science 15, industrial 14, media 10, finance 9, math 8, security 7.
- **F. Most common input formats:** json 28, source code 24, csv 20, time-series 15, **spreadsheet 15**, **pdf 13**, scientific data 11, video 8, document 7, audio 5, 3D model 4, image 3, presentation 3.
- **F. Libraries baked into the task images:**
  - pandas 30, numpy 28, **openpyxl 18**, scipy 17, **libreoffice 11**, npm 9, **ffmpeg 9**
  - pypdf/pdfplumber 12, torch 5, opencv 4, java+maven 4, python-pptx 3, whisper 3, tesseract 2
  - 24/101 need office/PDF libraries; 9 need media tools; 18 need non-Python toolchains (java, node, go, erlang, scala, lean)
- **F. Our Workbench image has none of openpyxl, python-docx, python-pptx, pdfplumber/pypdf, libreoffice or ffmpeg** (pandas 2.2.3, numpy, pytest only). Source: workbench `server/Dockerfile`.

### Concrete tasks per domain (public v1.1), with frontier no-skill pass rate
The pass rate is from `selected_runs.jsonl`: Opus 4.8, MiniMax M3 and Gemini 3.5 Flash, 3 trials each, no skills. Source: https://huggingface.co/datasets/benchflow/skillsbench-leaderboard `analysis/skillsbench/v1.1/official-selected/selected_runs.jsonl`.

| domain | easy for frontier agents (≥ 4/6) | hard (0–1/6) |
|---|---|---|
| office | citation-check 7/7 (bib/json), pdf-excel-diff 6/6 (pdf + xlsx → json), powerlifting-coef-calc 6/6 (xlsx formulas), offer-letter-generator 4/6 (docx template), pptx-reference-formatting 4/6 (pptx) | sales-pivot-analysis 0 (pdf + xlsx → pivot tables), jpg-ocr-stat 0, organize-messy-files 0, enterprise-information-search 0, latex-formula-extraction 1 |
| industrial | 3d-scan-calc 6/6 (STL binary → json), hvac-control 4/6 (time-series control → json) | manufacturing-* 0 (codebook, maintenance, FJSP), drone 0, egomotion video 0, energy-* 1/6 |
| finance | econ-detrending-correlation 5/6 (xlsx time series) | weighted-gdp-calc 0 (27 tests), xlsx-recover-data 0, reserves-at-risk 0, shock-analysis-supply 0, sec-financial-report 0, financial-modeling-qa 1 |
| software | fix-build-agentops 6/6 (npm), spring-boot-jakarta-migration 6/6 (maven), jax-computing-basics 6/6, parallel-tfidf-search 4/6, fix-visual-stability 4/6 | debug-trl-grpo 0, data-to-d3 0, flink-query 0, llm-prefix-cache-replay 0, simpo 0, azure-bgp 0 |
| science | glm-lake-mendota 6/6, seismic-phase-picking 6/6, mars-clouds-clustering 5/6, grav-wave 5/7, exoplanet 4/6 | lab-unit-harmonization 0, flood-risk 0, protein-expression (xlsx) 0, quantum-sim 0 |
| math / OR | exam-block-sequencing 3/3, lean4-proof 4/4, pddl-tpp 5/6 | bike-rebalance 0, civ6 0 |
| security | fix-druid-loophole-cve 5/6 (java), syzkaller 5/6 | dapt-intrusion 0, suricata 0, dependency-audit 0, setup-fuzzing 0 |
| media | threejs-to-obj 4/6 | mario-coin-counting (video) 0, video-silence-remover 0, threejs-structure-parser 0 |

- **F. Public no-skill scores of frontier agents:** 8.8% (Haiku 4.5) to 51.5% (GPT-5.5/OpenHands). Source: `leaderboard/skillsbench/v1.1/official.csv`.
- **F. Measured under the arena contract** (dnakhla #202):
  - The median public task's instruction is 1,212 characters, so one observation costs a median of 633 tokens in an instruction-repeating wrapper.
  - A minimal write-run-evaluate episode fits 4,096 tokens in only 44/87 tasks.
  - The untrained Qwen3.8-27B solved 3/50 episodes; 46 of 47 losses ended **before any answer was graded**:
    - prose before the JSON 10, JSON escaping 5, `<tool_call>` tags 3, empty reply 3
    - script cut off by the reply cap 13
    - `cat` of an input, then out of budget 12
- **F. rca-umb #182:** *"A strict 'exactly one JSON object' rule fits the per-task arena rewards much better"* than lenient parsing. *"The model seems to break format exactly when a task makes it reason about code."*

## 3. Which hidden tasks the untrained 27B likely solves, and what blocks the rest
- **I. The 4 base solves (industrial 2, office 2)** are almost certainly the shortest, plainest tasks of the "read a few files, compute in Python, write one json or xlsx" kind. In the public set the analogues are citation-check, powerlifting-coef-calc, pdf-excel-diff, 3d-scan-calc and hvac-control. These need few actions, small observations, and no unusual toolchain.
- **F (board statistics).** Across about 110 runs, industrial behaves like two coin-flip tasks, office like one sure task plus one coin flip, software 1 in about 18–29% of runs, finance about 9–11%. Science, math, security and media are almost never solved. Six base-model evaluations ranged 4, 3, 2, 2, 1, 0 (#240), so the reference itself is noisy.
- **I. What blocks the others, in likely order:**
  1. **Format breaks:** prose, escaping, tool_call tags. These kill about half of episodes, more on code-reasoning tasks.
  2. **The observation and budget wall:** one `cat` of an 8,192-character head costs about 2k tokens of an 8,192-token budget that includes observations. Long scripts in a reply also get cut.
  3. **File-format skill:** xlsx with formulas or pivots, docx, pptx, pdf extraction, video/audio via ffmpeg or whisper. The libraries exist in the task image, but the model must know to use openpyxl, pdfplumber, python-pptx and ffmpeg correctly, without reading docs.
  4. **Exactness:** all-or-nothing across about 6 tests (sheet names, column order, rounding).
  5. **Long-horizon domain work:** OR, control, signal processing, multi-step builds in java or npm.

  Items 1 and 2 are habit and interface problems that RL can address. Item 3 is a knowledge problem that RL can partly address, by practising with the libraries. Items 4 and 5 are mostly capability problems.

## 4. Library-use as a trainable habit
- **F.** The eval task images carry their libraries; our training image lacks every office, PDF and media library. Training sandboxes have outbound internet (AGENTS.md: "outbound internet"). Network access in eval sandboxes is not documented.
- **I. "Discover then use the right library" is trainable, and our environment never practises it.** The habit is: check `python3 -c "import openpyxl"` or `pip list | grep -i`; read xlsx and pdf with code, never `cat`; write xlsx with openpyxl, keeping sheet names and formulas. Our tasks are all CSV or Markdown, so the model never touches binary office formats during training. Of the SkillsBench formats, spreadsheet plus pdf plus document plus presentation appear in about 38 of 101 tasks, and in most office and finance tasks.

## 5. Could we get the exact 40?
- **F.** No public list exists. The baseline.json for the public balanced40-v2 deliberately omits task identities ("task identities and mappings are not included"). heldout-v2 is described only as private. BenchFlow's Kaggle "Agent Skill Lift" scored on a similarly private "bench-mix of held-out tasks" (https://www.kaggle.com/competitions/skill-lift). That suggests BenchFlow keeps an unreleased pool in SkillsBench format.
- **I.** The best stand-in is a balanced 5-per-domain draw from public v1.1 tasks, run under the arena protocol: no skills, 8k/16k budget, one JSON per reply, 8,192-character head truncation. It serves as a **local proxy eval**.

## 6. Three most actionable ideas for the next 10 submissions
1. **Train under the eval's real contract, not ours.**
   - 8,192 completion tokens counting observations, 16,384 context, strict one-JSON parsing
   - output truncated at 8,192 characters, head only (no tail)
   - work in `/root`, `submit` with a short final answer
   - reward the habits that kill episodes today: valid JSON every turn, bounded observations (`head`, `wc`, targeted `grep`, never `cat` a big file), and a short script per reply

   Our Workbench used 12,288 tokens, 3,000-character head-plus-tail truncation and `/app`, which is milder than the eval.
2. **Add binary office formats to the training image and tasks:** openpyxl, python-docx, python-pptx, pdfplumber/pypdf, LibreOffice headless, ffmpeg. Generate procedural xlsx/pdf/docx/pptx inputs and outputs (pivot sheets, filled forms, slide edits, pdf-to-table reconciliations) with exact-schema pytest checks. These formats cover most office and finance hidden tasks.
3. **Build a local proxy eval before spending slots.**
   - Run untrained Qwen3.8-27B (OpenRouter, thinking off, temperature 0.7) on a balanced 5×8 sample of public SkillsBench v1.1 task images, under the arena protocol above.
   - Measure where episodes die: format, budget, or wrong answer.
   - Use it to choose and pre-register each daily submission's single change.

   One arena run (40 tasks, one attempt, noise ±2) can't separate designs. A 40–80-episode proxy eval with failure-mode counts can show whether a design fixes the dominant failure modes before submitting.
