---
license: cc0-1.0
language:
  - en
pretty_name: FormulaGym (OpenEnv Arena environment)
tags:
  - openenv
  - reinforcement-learning
  - spreadsheets
  - excel
  - tool-use
  - office
  - finance
size_categories:
  - n<1K
---

# FormulaGym for OpenEnv Arena

An OpenEnv environment where an agent repairs formulas in **real business spreadsheets** from the public Enron
corpus. It practises what office and finance work needs from a spreadsheet: read a workbook with tools, find the
rows and columns that matter, and write one Excel formula that is right for every row it is copied to.

This dataset describes the 50 tasks submitted to [OpenEnv Arena](https://openenvarena-arena.hf.space/). What runs is
the Docker image named in the submission; this card and `tasks.jsonl` say what is in it and how it was chosen.

## Task types

Each task is one **formula block** (a run of cells sharing one formula shape, e.g. a column of row totals) in one
workbook. The same block can be posed three ways:

| Type | task_id | What the agent sees | What it submits |
|---|---|---|---|
| rebuild | `fg-…` | the block's cells are empty | the formula for the top-left cell |
| repair | `fg-….repair` | the block holds a **wrong** formula (a shifted row, a dropped term, a range end off by one, a swapped sign, a wrong lookup column) and the wrong values it gives | the correct formula |
| pasted | `fg-….pasted` | one cell of the block holds its typed-in value instead of its formula; only the sheet is named | the cell **and** its formula |

## Tools and budget

One JSON object per turn: `list_sheets`, `read_range` (≤ 400 cells, shown as `ADDRESS=value [=FORMULA]`), `find`
(text search), `try_formula` (the value a formula gives right now; it does not say whether it is right) and
`submit`. 16 actions in all; the last must be `submit`. Observations are capped at 3,000 characters.

## Reward (deterministic, no LLM)

LibreOffice recalculates the workbook with the submitted formula filled across the block, on the real inputs **and**
on perturbed copies of them (random changes, one input at a time, and edge values such as 0 and large values of the
other sign). The reward is **1** if the outputs match the original formula's outputs on every copy, else **0**.

- A typed-in number fails, because the outputs move when the inputs move.
- Any equivalent formula passes (`=A1+A2+A3` and `=SUM(A1:A3)` alike).
- An answer identical to the original (ignoring spaces, `$` and a leading `+`) scores 1 without recalculation.
- Repair: submitting the given wrong formula scores 0. Pasted: the right formula in the wrong cell scores 0.

## How the 50 tasks were chosen

| Step | Count |
|---|---|
| Formula tasks built from 20,872 Enron `.xls` files (filters for errors, volatile functions, trivial formulas, personal data, near-duplicate workbooks) | 15,921 tasks, 2,742 workbooks |
| Pool: the training splits only (never the held-out test/eval workbooks or their near-copies) | 12,223 |
| Dropped: the same formula shape visible on another sheet (1,541), workbook data over 1 MB (1,488), a strong model failed it (266), uses a named range (175) | 8,753 eligible |
| Seeded draw (seed 7): family quotas tilted to lookups, conditional sums and finance; a mix of tiers; ≤ 1 task per workbook (≤ 2 for rare families) | 330 tasks |
| Checks inside the image, per type: answer hidden; original → 1; typed number, given wrong formula, wrong cell, empty submit → 0; the checker rejects generated wrong formulas; grading under 60 s | 725 of 769 task ids pass |
| Screening: Qwen/Qwen3.8-27B (revision `1d4bf0f`, the arena's base model), thinking off, the arena's one-JSON-object protocol, 4–5 tries per task id (3,132 tries) | 46% of tries solved; 29% ended on a reply that was not a single JSON object |
| Chosen: 45 tasks solved in some tries but not all, with at least one failure that was a wrong answer (not only a format failure), ranked by how mixed the results were; plus 5 the 27B never solved but a stronger model did. One task per workbook, ≤ 8 per formula family | **50** |

The 50: 26 rebuild, 14 repair, 10 pasted · aggregate 8, arithmetic 8, cross-sheet 8, logic 8, lookup 6, conditional
sums 5, finance 4, dates 3 · tier (by functions used) hard 20, medium 24, easy 6 · mean screening solve rate 0.46.

The screening run went on after the choice; `tasks.jsonl` reports each task's solved/tries from the fuller results
(5–6 tries per task). With them, all 45 mixed tasks are still mixed (2/5 to 5/6), and the 5 hard ones have 0 or 1
solves.

## Files

- `tasks.jsonl`: one line per task: `task_id`, `type`, `family`, `tier`, `screen_solved`, `screen_tries`,
  `workbook` (path in the [SheetJS/enron_xls](https://github.com/SheetJS/enron_xls) mirror), `sheet`, and for rebuild
  and repair the `target` range. Answers (the original formulas, the pasted cell) are not included.
- `source/`: the environment and checker code (OpenEnv server, task types, checks, screening and selection scripts).

## Limits

- The checker perturbs numeric inputs only. Formulas that differ only in how they treat text or blank cells, or
  in rows the workbook leaves empty, can pass; tasks where the checker rejected none of the generated wrong
  formulas were dropped, but this is a test on generated mistakes, not a proof.
- Grading uses LibreOffice, not Excel; a few functions differ in edge cases.
- Screening used 4–5 tries per task, so solve rates are rough. Our server and prompt may differ from the arena's
  harness (its system prompt and sampling settings are not published).
- Personal data was filtered with keyword rules, a model check and manual review of samples; names of Enron
  employees in work roles were kept. Report anything you find and it will be removed.

## Source and license

Spreadsheets: the Enron corpus as mirrored by [SheetJS/enron_xls](https://github.com/SheetJS/enron_xls) (CC0 1.0),
made public during the FERC investigation. This dataset: CC0 1.0. The code in `source/`: Apache-2.0.
