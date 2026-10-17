# RL environment landscape (as of October 2026)

These environments are grouped by **type of task**. Some are **benchmarks** (used for testing), some are **training environments**, and many are used for both. Our own two are listed last for comparison.

> Compiled from general knowledge plus our research passes. It is not a fresh survey. Check exact versions and numbers on each project's own page before citing.

## 1. Single-turn, verifiable answers (the simplest RL)
| Name | What the model does | How reward works | Typical use |
|---|---|---|---|
| **GSM8K / MATH / AIME** | Solve a maths problem in one reply | Final answer matches the key | The classic first RL task (our Mac run used GSM8K) |
| **Countdown / "make 24"** | Combine numbers to hit a target | Check the arithmetic | TinyZero-style reasoning RL demos |
| **Reasoning Gym** | 100+ generated puzzles (logic, graphs, arithmetic…) | Built-in verifier per task, partial credit | Cheap, endless procedural training data |
| **LiveCodeBench / code contests** | Write a program | Run hidden test cases | Code-reasoning RL |

## 2. Software engineering agents
| Name | What the model does | How reward works | Typical use |
|---|---|---|---|
| **SWE-bench (Verified, Pro)** | Fix a real GitHub issue in a real repo | Repo's tests pass after the patch | **The** headline coding-agent benchmark |
| **SWE-Gym / R2E-Gym / SWE-smith** | Same shape, thousands of generated or real bugs | Hidden tests | **Training** environments for SWE agents |
| **MLE-bench** | Do a Kaggle-style ML task end to end | Competition metric | ML-engineering agents |
| **Mutation / repo-repair envs** | Fix injected bugs in real libraries | Library's own test suite | What our `pyrepo` and several arena entrants did |

## 3. Terminal and computer-environment agents
| Name | What the model does | How reward works | Typical use |
|---|---|---|---|
| **Terminal-Bench (2.x)** ("t-bench") | Solve tasks in a Linux shell (build, debug, configure, data work) | `tests/test.sh` (pytest) → pass/fail | Leading benchmark for terminal agents; the `tbench2_env` we copied |
| **SkillsBench** | Real files (PDF, XLSX, video, data) plus long rule-heavy instructions, produce an exact output file | Many pytest checks, all-or-nothing | **What the arena's hidden test most resembles** |
| **Endless Terminals / TMax / Skill2Env** | Procedurally generated terminal tasks | Generated test per task | **Training** environments for terminal agents |
| **OSWorld** | Use a real desktop OS (GUI: clicks, apps) | Checker scripts on the final state | Computer-use agents |

## 4. Tool use and conversation with users
| Name | What the model does | How reward works | Typical use |
|---|---|---|---|
| **τ-bench / τ²-bench** | Act as an airline or retail agent with tools and a simulated customer | Final database state + policy compliance | Customer-service agents |
| **BFCL** (Berkeley Function Calling) | Call functions/APIs with correct arguments | Exact match on the calls | Function-calling accuracy |
| **AppWorld / Toolathlon** | Multi-app tasks (email, calendar, payments…) via APIs | State checks | Everyday-assistant agents |
| **MCP-based task suites** | Use MCP tool servers | Task-specific checks | Newer generalist tool training |

## 5. Web browsing and research
| Name | What the model does | How reward works | Typical use |
|---|---|---|---|
| **WebArena / VisualWebArena** | Complete tasks on self-hosted websites (shop, forum, GitLab) | Checks on the site's state | Web-navigation agents |
| **BrowseComp** | Find hard-to-locate facts on the live web | Exact answer | Deep-research agents |
| **GAIA** | General assistant questions needing tools and browsing | Exact answer | Generalist agents |
| **Search-R1-style envs** | Interleave search calls and reasoning | Final answer only | Training search habits with RL |

## 6. Realistic work and professional tasks
| Name | What the model does | How reward works | Typical use |
|---|---|---|---|
| **GDPval** | Real professional deliverables across many occupations | Expert grading | Economic-value measurement |
| **TheAgentCompany** | Act as an employee in a simulated company (code, docs, chat) | Checkpoint scoring | Workplace agents |
| **Cybench / CTF suites** | Capture-the-flag security challenges | Flag found or not | Cybersecurity agents |

## 7. Games and interactive worlds
| Name | What the model does | How reward works | Typical use |
|---|---|---|---|
| **TextArena / OpenSpiel** | Play games (Wordle, chess, tic-tac-toe, negotiation) | Win/lose/draw | Multi-turn RL, self-play |
| **ALFWorld / BabyAI / Crafter** | Act in text or grid worlds to reach goals | Goal reached | Classic agent-RL research |

## 8. Long context and memory
| Name | What the model does | How reward works | Typical use |
|---|---|---|---|
| **RLM-style environments** (Recursive Language Models) | Process huge inputs by searching and slicing them in a REPL | Final answer | Training "grep instead of read" habits |
| **OOLONG / BrowseComp-Plus** | Answer from very long document collections | Exact answer | Long-context benchmarks |

## 9. Frameworks and hubs for building RL environments
| Name | What it is |
|---|---|
| **OpenEnv** (Meta / Hugging Face) | Standard `reset` / `step` server interface; OpenEnv Arena uses it |
| **Prime Intellect `verifiers` + Environments Hub** | Library and marketplace of RL environments with built-in rubrics |
| **TRL** (Hugging Face) | Trainer library with GRPO, which can train against OpenEnv environments |
| **BenchFlow** | Runs benchmarks like SkillsBench as containerised tasks; the organizer of OpenEnv Arena |

## Ours, for comparison
| Name | Type | Notes |
|---|---|---|
| **Workbench** | Workspace tasks (category 3 style) via `run_bash` / `submit` | Real-library repair, industrial and office audits with hidden caveats. Our best design: 3–4/40 |
| **T-Desk** | The same tasks behind a `tbench2_env` clone | Tight budget: 0/40. Roomy budget: 2/40 |

## How to read this
Most of the field has moved from category 1 (single answers) toward **categories 2–6: multi-step agents in realistic environments, graded by automated checks.** That's the direction the arena (SkillsBench-style) and our Workbench sit in.
