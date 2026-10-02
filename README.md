# Chart Rules and the Streaming Era

Research project for the *Journal of Cultural Economics*: how Billboard's December 2014 decision to count streams on the Billboard 200 album chart affected (1) what artists produce and (2) which albums the chart rewards.

- **Research context and results:** `PROJECT_CONTEXT.md`
- **Working rules for contributors and AI agents:** `CLAUDE.md`
- **Frozen analysis plan:** `docs/analysis_plan.md`; detailed history: `docs/devlog.md`
- **Genre classification rule and its reasoning:** `docs/genre_classification.md`

## Layout

```
data/raw/        Kaggle + Spotify inputs (read-only, not in git)
data/external/   MusicBrainz caches and collected tables (not in git)
data/interim/    roster, artist matches, identity audits
data/final/      analysis-ready samples
code/            paths.py, shared helpers, numbered pipeline scripts 01-23, run_pipeline.py
results/         part1_album_length/, part2_incumbency/, part2b_genre_staying_power/
docs/            analysis plans, devlog, LLM-use log, genre rule, cleanup records
archive/         superseded first-round code and results
```

## Reproducing the results

Requires Python 3.10 with pandas, numpy, statsmodels and scipy, plus the raw data in `data/raw/` and the MusicBrainz caches in `data/external/`.

```
py -3.10 code/run_pipeline.py            # full pipeline from cached data, about 5 minutes
py -3.10 code/run_pipeline.py --from 16  # rerun from a given step
```

The pipeline never calls the MusicBrainz API unless `--allow-api` is passed; a missing cache entry stops the run instead.
