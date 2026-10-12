# OpenEnv Arena log (arshy)

What we built, why, what the arena said, and what everyone else is doing.

- [RESULTS.md](RESULTS.md): one table across our versions
- [versions/](versions/): one record per submission, from [TEMPLATE.md](versions/TEMPLATE.md)
  (hypothesis → design → calibration → contract → training → result → lessons → next)
- [landscape/](landscape/): dated snapshots of all scored runs and board posts, plus `runs.csv`

## Routine
1. **Before designing a version:** run `python3 scripts/study_board.py` and read the new snapshot.
2. **When submitting:** copy `versions/TEMPLATE.md` and fill in everything up to "Submission contract".
3. **After the result:** fill in training, result, lessons and next. Add a row to RESULTS.md and run the study again.
