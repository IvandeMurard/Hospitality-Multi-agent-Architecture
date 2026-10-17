"""Record why each forecast came out the way it did -> forecast_drivers.json.

Reruns closed_loop_demo.py unchanged and keeps Prophet's breakdown of every
forecast (baseline trend, day of week, time of year, holidays, and the
occupancy / weather / event regressors). Prophet.predict is wrapped, not
re-called, so random-number use is identical and the run must reproduce the
committed ledger exactly — the script refuses to write otherwise.

The demo imports the private Aetherix backend: point --aetherix at a checkout
of it (backend/ + scripts/ops/, the version recorded in closed_loop_demo.json
under protocol) and run with that backend's venv:

    <aetherix>/backend/.venv/Scripts/python demo/closed-loop/capture_drivers.py --aetherix <dir>
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEDGER = HERE / "closed_loop_demo.json"
OUT = HERE / "forecast_drivers.json"
# Prophet output columns that are sums of other columns, not drivers of their own.
SUMS = {"additive_terms", "extra_regressors_additive", "multiplicative_terms", "holidays"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--aetherix", type=Path, required=True)
    args = ap.parse_args()
    os.environ["AETHERIX_ROOT"] = str(args.aetherix)
    sys.path.insert(0, str(HERE))  # this folder's closed_loop_demo.py, not the backend's

    import closed_loop_demo as demo
    from prophet import Prophet

    frames: list[dict] = []
    predict = Prophet.predict

    def recording_predict(self, df=None, *a, **k):
        out = predict(self, df, *a, **k)
        if df is not None and len(df) == 1:
            frames.append(out.iloc[0].to_dict())
        return out

    Prophet.predict = recording_predict

    with tempfile.TemporaryDirectory() as tmp:
        report = asyncio.run(demo.run(30, Path(tmp) / "closed_loop_demo.json"))
    committed = json.loads(LEDGER.read_text(encoding="utf-8"))
    if report["ledger"] != committed["ledger"]:
        print("Rerun diverged from the committed ledger — nothing written.", file=sys.stderr)
        return 1

    # The simulated manager's guess: mean of the last 4 same weekdays in the
    # history the loop had built by that day (quarantined outcomes excluded).
    history = demo.generate(2025, seed=demo.SEED)
    future = demo.generate(2026, seed=demo.SEED + 1)[:30]
    for i, row in enumerate(future, start=1):
        if i >= demo.SHIFT_DAY:
            row["y"] = round(row["y"] * demo.SHIFT_FACTOR)

    days = []
    for i, (frame, row, entry) in enumerate(zip(frames, future, committed["ledger"]), start=1):
        target = demo.date.fromisoformat(row["ds"])
        same = [r["y"] for r in history if demo.date.fromisoformat(r["ds"]).weekday() == target.weekday()][-4:]
        components = {
            k: float(v) for k, v in frame.items()
            if k not in SUMS and k not in ("ds", "yhat") and not k.endswith(("_lower", "_upper"))
            and float(v) != 0.0
        }
        days.append({
            "index": i,
            "day": row["ds"],
            "signals": {k: row[k] for k in ("occupancy", "weather_score", "event_impact")},
            "baseline": components.pop("trend"),
            "components": components,
            "yhat": float(frame["yhat"]),
            "manager_last_same_weekdays": same,
        })
        if entry["bounds"] == "ok":
            history.append(row)

    OUT.write_text(json.dumps({"days": days}, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8", newline="\n")
    print(f"Ledger reproduced; wrote {OUT.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
