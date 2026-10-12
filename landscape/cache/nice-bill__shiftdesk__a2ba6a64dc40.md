---
license: apache-2.0
pretty_name: ShiftDesk
tags: [openenv, reinforcement-learning, agents, tool-use]
---
# ShiftDesk

An OpenEnv environment for OpenEnv Arena. 24 tasks: 8 families (one per arena domain) x 3 levels.
Every reset generates a fresh instance (files, question, answer) from a seeded generator, so there are no
fixed answer keys and this dataset holds none.

| Domain | Family | What the agent does |
|---|---|---|
| Software engineering | module-repair | Fix 1 to 3 seeded bugs in utils.py; submit the whole file as a JSON string; hidden randomized tests against the docstring spec |
| Industrial & physical | line-oee | Availability and OEE from a machine state-change log, production counts and breaks |
| Natural science | kinetics-lab | Rate constant, half-life and reaction order from noisy concentration data with QC-failed rows and unit changes |
| Office & white-collar | expense-policy | Reimbursable total under a written policy: caps, receipts, currencies, duplicates |
| Finance & economics | loan-desk | Annuity payment, balance after k payments, interest with extra payments |
| Math & formal reasoning | exact-count | Inclusion-exclusion counts, lattice paths on a blocked grid, digit DP modulo 1e9+7 |
| Cybersecurity | auth-hunt | Find the brute-force that succeeded in an sshd log; decoys; /24 rotation at level 3 |
| Media & content | subtitle-qc | SRT on-screen time, edit notes with shifts and cuts, reading-speed violations |

## What it teaches

- **Read the tool list, don't memorize it.** Tool names and argument names are drawn per instance
  (for example `exec_code` with `code`, or `sandbox` with `program`; `final_answer` with `value`). The reset text
  lists them with one example call each. An unknown tool costs a call and returns the valid names.
- **One valid JSON object per turn, including code.** The Python tool takes source as a normal JSON string, and the
  software task needs a whole file as the answer, so the policy has to escape newlines and quotes correctly.
- **Use tools for data, not eyes.** Reads are capped at 2,500 characters; logs run to ~10,000, so the policy has to
  compute in Python.

## Reward

1.0 for a correct final answer (numeric tolerance stated per family, exact match for ids, sets and timestamps),
otherwise 0.0. No answer, running out of calls, or an invalid reply scores 0.0.

## Same instance for a group

Rollouts that reset the same task within the same 5-minute window get the same instance (seeded from a
secret in the image), so the five parallel rollouts of an optimizer step are compared on one problem.

## Checks

Reference answers score 1 and plausible wrong answers score 0 on hundreds of seeds per task; independent
solvers that read only the files reproduce the labels for the log, OEE and subtitle families; every bug
mutation is detectable by the hidden tests; `openenv validate` passes; every task replays to a terminal
reward over WebSocket. Policy code runs as `nobody` with CPU, memory and process limits.

Source: https://github.com/nice-bills/shiftdesk
