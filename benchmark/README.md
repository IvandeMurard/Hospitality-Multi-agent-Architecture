# Real-data forecast benchmark

The benchmark behind the README's forecasting claim: does Prophet, run exactly as configured in
Aetherix's prediction engine, beat a naive baseline on real restaurant visitor data? Full
methodology is in the script's own docstring — this file is just "how to actually run it."

**Published result** (`recruit_results.json`, seed 42, 30 restaurants, 1,193 scored points):

| | MAPE (mean, all leads) | MdAPE (median, all leads) |
|---|---:|---:|
| Naive (last-4-same-weekday) | 55.86% | 27.57% |
| **Prophet** (Aetherix config) | **49.71%** | **27.01%** |
| LightGBM (global, lag features) | 52.41% | 25.56% |

Prophet beats the naive baseline by 6.15 points on mean MAPE (passes the pre-registered ≥5pt
decision rule) but only 0.56 points on the median — and a plain LightGBM model beats Prophet on
the median. Both readings are published because only reporting the mean would be the flattering
half of the same result.

## Reproduce it

1. Get the data: Kaggle's [*Recruit Restaurant Visitor Forecasting*](https://www.kaggle.com/competitions/recruit-restaurant-visitor-forecasting/data)
   competition (free Kaggle account required — the data isn't redistributed here). You need
   `air_visit_data.csv` and `date_info.csv` from that download; extract them into one directory.
2. Install the three dependencies the script imports: `pandas`, `numpy`, `prophet`, `lightgbm`.
3. Run it:

   ```bash
   python benchmark/benchmark_recruit.py \
       --data-dir /path/to/extracted/kaggle/data \
       --out benchmark/recruit_results.json
   ```

Deterministic by construction: fixed seed (42), fixed rolling-origin schedule per store (no
random sampling), so a rerun on the same data reproduces the published numbers exactly. No
network calls, no LLM in the loop — this is a pure forecasting benchmark.

## What this does and doesn't prove

It's a benchmark of the forecasting model in isolation, on public data from Japanese restaurants —
not a claim about accuracy on any specific hotel or market, and not a claim about the rest of the
system (the outcome-capture loop, the guardrails, the memory). See [`../VISION.md`](../VISION.md)
and [`../COGNITION.md`](../COGNITION.md) for why the forecast being commoditized is the expected,
unsurprising part of this project rather than a problem to hide.
