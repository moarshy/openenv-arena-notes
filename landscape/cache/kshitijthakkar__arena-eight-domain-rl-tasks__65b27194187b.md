---
license: cc-by-4.0
language:
  - en
task_categories:
  - text-generation
size_categories:
  - n<1K
tags:
  - reinforcement-learning
  - grpo
  - synthetic-data
  - deterministic-rewards
  - openenv-arena
configs:
  - config_name: default
    data_files:
      - split: train
        path: train.jsonl
      - split: validation
        path: validation.jsonl
  - config_name: leaderboard_focus
    data_files:
      - split: train
        path: train_focus.jsonl
      - split: validation
        path: validation_focus.jsonl
  - config_name: arena_domain_lab
    data_files:
      - split: train
        path: arena_domain_lab_tasks.jsonl
---

# Eight-Domain Synthetic RL Task Bank

This dataset contains 200 authored synthetic tasks for small, reproducible GRPO
experiments across software debugging, industrial operations, science, office
workflows, finance, math, defensive cybersecurity, and media understanding. It contains
no captured production records, private traces, or model-generated reference answers.

## Splits

| Split | Rows | Tasks per domain | Purpose |
| --- | ---: | ---: | --- |
| `train` | 160 | 20 | Prompts used for training rollouts |
| `validation` | 40 | 5 | Same-task baseline versus trained-policy diagnostics |

The `leaderboard_focus` configuration provides a matched six-domain curriculum for
science, office, finance, math, defensive cybersecurity, and media: 120 training tasks
(20/domain) plus 30 held-out diagnostic tasks (5/domain). Its validation file is separate
from the default configuration's 40-row validation split. These rows are synthetic and
public; they are not the Arena's private evaluation tasks. The focus files are subsets of
the full configuration and should not be added to its row counts.

The validation split and its expected answers are public. Treat it as a diagnostic split,
not a hidden benchmark or a secret leaderboard evaluation. Training files contain the
grader targets required by deterministic reward functions; reference completions are not
included.

## Row fields

- `prompt`: task instructions and synthetic evidence.
- `answer`: grader target values, serialized as JSON.
- `task_type`: one of the eight domains listed above.
- `allowed_evidence`: evidence identifiers the response may cite.
- `scenario_id`: stable unique task identifier.
- `source`: `synthetic_authored` for every row.

The task prompts request one compact JSON answer. Rewards are deterministic and use
domain-specific weighted criteria: supported facts or accepted terms, exact numeric
checks with per-criterion tolerances, structured object checks, boolean checks, and
evidence-set overlap. Unsafe recommendations in the industrial and cyber domains receive
zero. The grader does not call an LLM judge.

| Domain | Weighted criteria |
| --- | --- |
| Software | diagnosis 0.30, tests 0.25, fix 0.25, evidence 0.20 |
| Industrial | decision 0.30, limit check 0.25, action 0.20, evidence 0.25 |
| Science | conclusion 0.25, result 0.25, unit 0.15, uncertainty 0.15, evidence 0.20 |
| Office | fields 0.35, workflow 0.25, action 0.20, evidence 0.20 |
| Finance | amount 0.25, currency 0.10, status 0.25, reconciliation 0.20, evidence 0.20 |
| Math | answer 0.45, method 0.30, domain check 0.10, verification 0.15 |
| Cyber | finding 0.20, severity 0.15, indicators 0.20, response 0.25, evidence 0.20 |
| Media | content facts 0.35, labels 0.20, factuality 0.20, style constraints 0.10, evidence 0.15 |

## Challenge and related artifacts

This contribution is associated with the [OpenEnv Arena challenge Space](https://openenvarena-arena.hf.space/)
and its live leaderboard. The public [Arena Domain Lab image](https://hub.docker.com/r/kshitij190/arena-domain-lab)
uses the 50-task `arena_domain_lab` configuration and includes its environment source under
`arena_domain_lab/source/` for inspection and reproduction.

The GRPO and verifiable-reward design references the public
[RL+LLM Wiki knowledge base](https://github.com/rl-llm-wiki/rl-wiki). This task bank is
independently authored and does not include wiki datasets or copied Arena competitor task
content. Its procedural list/read/submit interaction takes inspiration from public Arena
message-board approaches Five Desks and Reconcile Lab; credit is limited to that general
multi-step workspace pattern. The tasks, graders, and implementation are independently
authored. The focused curriculum is intended for local model screening; it has not yet shown
that training improves held-out scores or the Arena leaderboard.

The `arena_domain_lab` configuration contains the exact 50-task slice served by the image,
including its workspace files, allowed evidence IDs, and deterministic grader targets. Its
domain allocation is 7 tasks each for science, finance, math, cybersecurity, and media, and
5 each for software, industrial operations, and office workflows. It is a training slice;
the public validation split remains separate and is not Arena's private evaluation set.
The image slice was screened with five rollouts per task through the complete workspace
interaction. Cases with identical rewards across all five local rollouts were replaced by
unused training cases with observed within-task reward variation. This screening checks for
possible GRPO signal; it does not demonstrate policy improvement or leaderboard transfer.

## Limitations

This is a small development dataset with 20 training tasks and 5 public diagnostic tasks
per domain. It is intended for controlled training experiments and grader development; it
does not establish broad domain competence, model improvement, an Arena evaluation score,
or a leaderboard result. Compare policies on the same held-out prompts and report training
reward separately from held-out evaluation results.
