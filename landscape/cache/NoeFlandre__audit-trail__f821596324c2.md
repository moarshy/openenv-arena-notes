---
license: apache-2.0
language:
  - en
pretty_name: Audit Trail tasks
tags:
  - openenv
  - log-analysis
  - cybersecurity
  - finance
  - reinforcement-learning
size_categories:
  - n<1K
---

# Audit Trail tasks

This dataset lists the tasks of the Audit Trail OpenEnv environment. The environment code is in the [GitHub repository](https://github.com/NoeFlandre/openenv-arena).

## What the environment teaches

The agent gets one log and a question. The question states a rule. The agent searches the log with `grep` and gives one answer. The rule has two steps: find the right lines, then compare them. The logs come from three families:

| Family | Domain | Rule |
| --- | --- | --- |
| `auth` | Cybersecurity | The earliest successful login from a source IP that had at least K failed logins before it. Answer: the user name. |
| `ledger` | Finance | The earliest debit that repeats an earlier debit with the same account and amount, 1 to 90 seconds before it, where the earlier debit was never reversed. Answer: the txn id. |
| `sensor` | Natural science | Among stations whose first reading at or after 06:00 of 30.0 C or more is followed by another reading of 30.0 C or more, the station with the earliest such reading. Answer: the station name. |

Each task has a level from 0 to 7. Levels 0 to 2 are easy, 3 to 5 medium and 6 to 7 hard. Harder levels have longer logs, more decoys and a higher K.

## Files

| File | Contents |
| --- | --- |
| `tasks.jsonl` | One task for each line: `task_id`, `split`, `family`, `level` and the accepted `seed`. |

The dataset does not contain the logs. The server builds each log from its seed, so the same seed always gives the same log and answer. If a seed does not give a log that passes the checks, the server tries the seed plus 100, then plus 200, and so on. The accepted seed is in `tasks.jsonl`.

## Reward

- `1.0`: the answer is correct. Case does not matter.
- `0.0`: the answer is wrong, or the agent uses all 10 steps.

## Splits

All 24 tasks are in the `train` split.

## Limits

- The logs are synthetic. They do not come from a real system.
- A grep returns at most 10 matching lines.
- Each episode has 10 steps.

## License

Apache License 2.0.
