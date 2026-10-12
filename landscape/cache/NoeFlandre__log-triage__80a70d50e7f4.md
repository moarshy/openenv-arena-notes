---
license: apache-2.0
language:
  - en
pretty_name: Log Triage tasks
tags:
  - openenv
  - log-analysis
  - reinforcement-learning
size_categories:
  - n<1K
---

# Log Triage tasks

This dataset lists the tasks of the Log Triage OpenEnv environment. The environment code is in the [GitHub repository](https://github.com/NoeFlandre/openenv-arena).

## What the environment teaches

The agent reads a service log. The agent must find the first service that returned an HTTP 5xx after a deploy. The agent searches the log with `grep` and gives one answer.

## Files

| File | Contents |
| --- | --- |
| `tasks.jsonl` | One task for each line. Each task has a `task_id`, a `split` and a `seed`. |

The server builds each log from its seed. The dataset does not contain the logs. The server and the seeds give the same logs every time.

## Reward

- `1.0`: the answer is correct.
- `0.0`: the answer is wrong, or the agent uses all 10 steps.

## Splits

All 12 tasks are in the `train` split.

## Limits

- The logs are synthetic. They do not come from a real system.
- A random guess gives a correct answer about one time in six.
- The tasks test one skill: reading time order in a log.

## License

Apache License 2.0.
