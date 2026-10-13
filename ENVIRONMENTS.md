# The three environments, explained

One section per submission: the bet we made, the environment as pseudocode, and one example episode. Scores are on the hidden heldout-v2 set (40 tasks). The untrained Qwen3.8-27B scores 4/40.

| | v1 Stepwise Math | v2 Workbench | v3 Workbench v2 |
|---|---|---|---|
| **Bet** | Teach a *skill* (math) | Teach *habits* through the hidden test's likely interface | Habits + *do no harm* + code repair |
| **Interface** | Custom `calc`/`submit` | `run_bash`/`submit` | Same |
| **What the model does** | Arithmetic | Explore, grep, catch caveats, write an exact JSON | + fix code to a spec |
| **Grading** | Right or wrong number | 6–8 checks on an output file | + hidden tests |
| **Score** | 2/40 | 3/40 | **4/40, including the first math point of any run** |

---

## v1: Stepwise Math → 2/40

**Hypothesis.** Math was 0 for everyone, and its answers can be verified exactly. Multi-step problems with a calculator should teach stepwise reasoning.

**What we didn't know yet:** the hidden "math" is operations research and planning, not arithmetic.

```python
class StepwiseMath(Environment):
    tools = {"calc": exact_calculator,      # fractions stay exact; exponents <= 64
             "submit": final_answer}

    def reset(task_id):                     # e.g. "probability-hard"
        question, self.answer = GENERATORS[task_id](random_seed)
        self.moves_left = 20
        return question + " Use calc / submit"

    def step(action):
        self.moves_left -= 1
        if action.command == "calc":
            return calc(action.text)        # "12*11/2 = 66"
        if action.command == "submit":
            return done(reward=1 if value(action.text) == self.answer else 0)
        if self.moves_left == 0:
            return done(reward=0)
```

```
ENV   : Bag has 8 red, 5 blue, 7 green. Draw 2 without replacement. P(same colour)?
MODEL : {"command": "calc", "text": "(8*7 + 5*4 + 7*6) / (20*19)"}
ENV   : = 59/190
MODEL : {"command": "submit", "text": "59/190"}
ENV   : Correct. reward 1
```

**Outcome.** The model practised a narrow protocol that doesn't appear in the hidden test. It lost both industrial tasks the untrained model solves.

---

## v2: Workbench → 3/40

**Hypothesis.** The hidden test is SkillsBench-style:
- a sandbox full of files
- a long instruction full of rules
- an exact output file and strict checks
- a `run_bash` tool

The model already knows the domain. It fails on **habits**: it stops at the first plausible answer, misses amendments, does maths in its head, and floods its own context window. So we train those habits through that interface.

```python
class Workbench(Environment):
    tools = {"run_bash": sandboxed_shell,   # agent user, /app only, 8k-char output, 120 s, no network
             "submit": grade_output_files}

    def reset(task_id):                     # e.g. "downtime-hard"
        wipe("/app")
        self.verify = FAMILIES[family].generate(random_seed, level)
        # writes big data files, a long handbook and an amendments folder with hidden caveats;
        # the answer key stays in server memory and never touches disk
        self.steps_left = 20
        return read("/app/TASK.md")

    def step(action):
        self.steps_left -= 1
        if action.type == "submit" or self.steps_left == 0:
            checks = self.verify("/app/output/*.json")          # 6-8 checks
            return done(reward=0.5 * share_passed(checks) + 0.5 * all_passed(checks))
        return truncate(run_as_agent(action.command, cwd="/app"), 8192)
```

Example (`downtime-hard`):
```
WORKSPACE
  data/sensor_log.csv        52,000 rows (too big to read)
  handbook/manual.md         600 lines; "limit: 45 min" buried at line 312
  handbook/amendments/
     2026-01  micro-stops < 8 min don't count
     2026-07  micro-stops < 5 min don't count     <- supersedes January
     2026-08  limit 45 -> 35                      <- applies
     2026-10  limit 35 -> 80                      <- future, must be ignored
     + 3 unrelated amendments
TASK  unplanned downtime per machine, NIGHT shift of 2026-09-10 -> output/downtime.json

GOOD EPISODE
  run_bash  ls -R /app; wc -l data/*.csv
  run_bash  grep -rn -i "downtime|limit|micro" handbook/
  run_bash  cat data/shifts.csv          -> night = 22:00 to 06:00 next day
  run_bash  python3 script.py            -> group DOWN runs, drop stops < 5 min, limit 35
  submit                                 -> 7/7 checks, reward 1.0
TYPICAL MISTAKE  limit 45 or micro-stops counted -> 4/7 checks, reward 0.29
```

**Outcome.** Only 104 training steps, because long multi-turn episodes are slow. Rewards ran high early (about 0.8), so many steps taught nothing. Industrial recovered from 0 to 1.

---

## v3: Workbench v2 → 4/40, with the first math point of any run

**Hypothesis.** All three 5/40 runs **kept the untrained model's 4 tasks and added one**, using realistic code or log work. So: do less harm, with shorter episodes and harder tasks so more steps teach something. And add **software repair**, the style the top runs share.

**Changes from v2:** 12 commands instead of 20; two caveats at the medium level; a 4th family:

```python
class RepairFamily:
    def generate(seed, level):
        pkg  = billing_package(["money", "pricing", "invoices", "dates", "fees", "units", "reports"])
        bugs = inject(pick(CATALOGUE, n={"easy": 1, "medium": 2, "hard": 3}[level]))
        # CATALOGUE: half-up -> floor rounding, ">=" -> ">", tax / 1000 instead of / 10000,
        #            coupon applied after tax, "2026-3" instead of "2026-03",
        #            floor instead of ceil periods, case-sensitive units, unstable tie-break
        write("docs/SPEC.md", "docs/CHANGELOG.md")   # hard: the changelog overrides the spec
        write("tests/test_basic.py")                 # visible tests catch ONLY one bug
        if level == "hard":
            keep_decoy("days_between +1")            # looks like a bug; the spec says inclusive
        self.cases, self.expected = hidden_cases(), reference(hidden_cases())   # server memory only

    def verify():
        results = run_as_agent("python3 harness.py")  # calls every function on hidden inputs
        return [imports_ok] + [fixed(b) for b in bugs] + [no_regressions] + [decoy_kept]
```

Example (`repair-hard`):
```
TASK  customers report wrong amounts; make the package match SPEC + CHANGELOG
GOOD EPISODE
  run_bash  cd project && python3 -m pytest -q    -> 1 failing test: parse_qty("3 Dozen") KeyError
  run_bash  cat docs/SPEC.md docs/CHANGELOG.md     -> units case-insensitive; 2.5.0: discount threshold now >=
  run_bash  grep -n "THRESHOLD\|def " src/*/*.py   -> finds `if subtotal > THRESHOLD`
  run_bash  sed -i ...                             -> fixes .lower(), >=, zero-padded month
                                                      (leaves days_between +1 alone: specified)
  run_bash  python3 -m pytest -q                   -> visible tests pass
  submit    -> hidden tests: 3 bugs fixed, no regressions, decoy kept -> 6/6, reward 1.0
TYPICAL MISTAKES  fixes only the visible bug -> 3/6;  "fixes" the decoy -> loses a check
```

### The 11 submitted tasks
| task | domain | the job | hidden caveats |
|---|---|---|---|
| downtime-easy | industrial | Downtime per machine for one shift (6 machines, 2 days) | none |
| downtime-medium | industrial | 9 machines, 3 days, 360-line handbook | micro-stop exclusion + revised limit |
| downtime-hard | industrial | 12 machines, 52k rows, 600-line handbook | micro-stop rule + superseded rule, revised limit + future-dated rule |
| expenses-easy | office / finance | Audit a department-month against the travel policy (EUR only) | none |
| expenses-medium | office / finance | Multi-currency, about 1,400 claims | 2 of: mid-month cap change, city tier change, FX correction |
| expenses-hard | office / finance | About 3,000 claims | mid-month cap + superseded cap, tier change, 2 FX corrections, future-dated rule |
| routing-medium | math (optimisation) | Two-van routes, 8 orders, capacity + time windows, within 5% of optimum | 2 dispatch notes |
| routing-hard | math (optimisation) | 9 orders | 3 dispatch notes (forbidden van, closed road, cancelled order) |
| repair-easy | software | Fix a 7-module billing package (1 bug) | the visible test reveals it |
| repair-medium | software | 2 bugs | 1 visible, 1 only findable from the spec |
| repair-hard | software | 3 bugs | the changelog overrides the spec; a decoy that looks off-by-one |

`routing-easy` is in the code but wasn't submitted: the model solved it 7/8 times.

**Outcome.** 4/40: office 2, industrial 1, **math 1**. Of 45 scored runs so far, this is the only one with a math point. The likeliest source is the routing family, the only optimisation-style task we know of in any run. It is one hidden task with one attempt, so it may be noise. Shorter episodes didn't buy more steps (109).
