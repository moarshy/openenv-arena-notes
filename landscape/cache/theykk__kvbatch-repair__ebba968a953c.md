# KV-Batch Repair Lab

Two offline code-repair tasks for RL training, adapted from MiMo-V2.6-RL-oss terminal-bench tasks
(dataset revision `639865fd3374018d6cb29b9fb82dd531406fcf5f`, Apache-2.0):

- `kv-cache-scatter` (from `candidate-0758-ml-inference`): repair the vendored ONNX TensorScatter
  operator so circular-mode KV-cache writes wrap only the sequence coordinate. Verifier recomputes
  public + hidden scatter cases and checks the source fix in both the Python operator and the C++
  operator text.
- `effective-batch-smoothing` (from `candidate-0803-ml-training`): repair effective-batch
  normalization in the vendored Transformers label-smoothing path so gradient-accumulation
  microbatches with different active-token counts normalize by the effective batch size.
  Verifier independently recomputes the loss terms and checks the Trainer forwarding contract.

## How the reward works

Each episode resets to one `task_id` with a fresh workspace copy of the buggy sources. The agent
uses `read` / `edit` / `run` actions to inspect files, patch them, and execute the task's
documented check command, then `submit` to score. Reward is binary: `1.0` for a fully verified
repair (source fix + runner output matching independent recomputation, including hidden cases),
otherwise `0.0`. `finish` or budget exhaustion ends with `0.0`. No partial credit, no model judge,
no network needed at runtime.

## Files

- `tasks.jsonl`: one row per task with the goal text, fixtures/cases, editable file list, and
  check command. Hidden KV scatter cases are included for transparency.
- Source tasks: https://huggingface.co/datasets/XiaomiMiMo/MiMo-V2.6-RL-oss
- Image: `docker.io/theykk/kvbatch-repair:v1`
