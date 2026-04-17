# History Dedup Design

**Goal:** Skip papers already included in the last 7 days' reports, so each daily digest only contains new research.

**Approach:** Title-based matching using the existing `normalize_title_text()` function. Scan recent JSON reports, collect their `items[].title` values, and exclude matches before ranking.

## Architecture

### New module: `src/history_dedup.py`

```
load_recent_report_titles(report_dir, report_date, days=7) -> set[str]
```

- List `*.json` in `report_dir` where the filename stem is a date within `(report_date - days, report_date)`
- Parse each JSON file, extract `items[].title`
- Normalize each title with `normalize_title_text()` and return as a set

### Pipeline integration

- `run_daily_pipeline()` gains parameter `exclude_titles: set[str] | None = None`
- After `deduplicate_papers()`, before `rank_top_papers()`, filter out papers whose normalized title is in `exclude_titles`
- `pipeline.main()` gains parameter `report_dir: str | None = None`
  - If provided, calls `load_recent_report_titles()` and passes result to `run_daily_pipeline()`

### CLI integration

- `src/main.py` calls `load_recent_report_titles(output_dir, report_date)` and passes result to `pipeline.main()`

## What does NOT change

- `report_generator.py` — JSON structure unchanged
- `deduplication.py` — same-session dedup still runs first
- `ranker.py` — scoring unchanged
- Existing tests — all pass unchanged

## Edge cases

- No prior reports exist → empty exclude set → all papers eligible
- Malformed JSON file → skip it gracefully
- Date in filename is not parseable → skip it
- `days=0` → no history scanned → all papers eligible

## Testing

- Unit tests for `load_recent_report_titles()` with temp report directory
- Unit tests for pipeline filtering with exclude_titles
- Integration test: prior report exists → same title paper excluded
