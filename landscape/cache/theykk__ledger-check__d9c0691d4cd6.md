---
license: mit
task_categories: [question-answering]
pretty_name: Ledger Check
---
# Ledger Check (OpenEnv)
Single-step ledger reconciliation tasks: given a short CSV ledger (id,account,amount), compute a closing balance, an account total, net flow, or identify a duplicate / largest-expense / unknown-account entry.

- `tasks.jsonl`: 1,200 tasks (6 kinds x 200), each with ledger, question and answer. The server accepts any `<kind>-<n>` task id and regenerates the same ledger from a seeded RNG, so the pool is unbounded. The Arena submission lists 50 of them (its maximum).
- Action: `{"answer": "<number or entry id>"}`. Numbers are accepted within 0.005; ids are case-insensitive.
- Reward: 1.0 for the exact correct answer, otherwise 0.0; the episode ends after one step.
- The image is the source of truth.
