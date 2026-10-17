"""Build homepage-loop.json — a citable 3-day excerpt of the closed-loop demo.

Sources, all committed in this folder:
  closed_loop_demo.json   the ledger (forecast, range, staffing, replies, actuals)
  whatsapp_transcript.md  the French messages the run produced (cross-checked)
  forecast_drivers.json   Prophet's breakdown of each forecast (capture_drivers.py)

Raw values are copied as stored. A few values are derived from them, each with
its formula below: the range width as a % of the forecast, the manager's error
(same formula as the ledger's ape_pct), whether the actual fell inside the
range, and the drivers rounded to 0.1 cover. The English text is written from
these values; the original receipts are French ("translated": true).

Emojis are replaced by a typed `signal`:
    reply   — accepted -> go · modified (counter-proposal) -> warn
    morning — outcome -> go · drift -> warn · quarantine -> stop

Stdlib only. Usage:
    python demo/closed-loop/build_homepage_loop.py          # writes the file
    python demo/closed-loop/build_homepage_loop.py --check  # exit 1 if stale
"""
from __future__ import annotations

import json
import math
import re
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEDGER = HERE / "closed_loop_demo.json"
TRANSCRIPT = HERE / "whatsapp_transcript.md"
DRIVERS = HERE / "forecast_drivers.json"
OUT = HERE / "homepage-loop.json"

DAYS = (1, 10, 17)
PROVENANCE = {
    "repo": "IvandeMurard/Hospitality-Multi-agent-Architecture",
    # Commit that holds the ledger + transcript this file is built from.
    "commit": "096509806333661409ab682b7d9e498ca7a67bcd",
    "path": "demo/closed-loop/",
    "seed": 42,
    "data": "synthetic sandbox",
    "hotel": "sandbox_hotel.json: a synthetic hotel with its own staffing rules",
    "services": "real PredictionEngine, StaffingService, feedback_guard",
    "drivers": "forecast_drivers.json: Prophet's own breakdown of each forecast, captured by rerunning the demo (ledger reproduced exactly)",
    "signals": "hotel occupancy, weather, local events (synthetic in this run), French public holidays, past covers",
    "translated": True,
}

# Staffing roles in the ledger -> (English plural noun stem, singular in a ratio).
# Headcount = ceil(covers / the hotel's ratio); the ratios themselves are read
# from the ledger (staffing.rules), and the test checks they reproduce it.
ROLES = ("servers", "hosts", "runners", "kitchen")
ROLE_EN = {"servers": ("server", "server"), "hosts": ("host", "host"),
           "runners": ("runner", "runner"), "kitchen": ("kitchen staff", "kitchen staff member")}
ROLE_FR = {"servers": "serveurs", "hosts": "hôtes", "runners": "runners", "kitchen": "cuisine"}
# PredictionEngine._compute_confidence: rating from range width / forecast.
CONFIDENCE_BANDS = ((0.20, 0.90), (0.30, 0.80), (0.40, 0.70), (0.50, 0.60))
CONFIDENCE_LABEL = {0.9: "High", 0.8: "Good", 0.7: "Fair", 0.6: "Low", 0.5: "Very low"}
INTERVAL_WIDTH = 0.80  # Prophet interval_width in PredictionEngine.train

FORECAST = re.compile(r"Couverts attendus : (\d+) \(fourchette (\d+)–(\d+), confiance (\d+)%\)")
STAFFING = re.compile(r"Effectif : (.+) \((règles de l'hôtel|règles par défaut)\)")
OCCUPANCY = re.compile(r"🏨 Hôtel à (\d+) % d'occupation — pression forte attendue sur le restaurant\.")
REPLY_OK = re.compile(r"OK 👍")
REPLY_COUNTER = re.compile(r"Je dirais plutôt (\d+) couverts\.")
ACTUAL = re.compile(r"Réel constaté : (\d+) couverts \(prévu (\d+), (dans la fourchette|écart ([+-]\d+) %)\)\.")
QUARANTINE = re.compile(
    r"⚠️ La donnée POS d'hier \((\d+) couverts\) est implausible \((\w+)\) — écartée, "
    r"elle n'alimentera pas l'apprentissage\. Pouvez-vous vérifier l'export caisse \?"
)
DRIFT = re.compile(r"📈 Troisième sous-estimation consécutive — .*")


def _day_blocks(transcript: str) -> dict[int, dict[str, list[str]]]:
    """Split the transcript into {day: {speaker-slot: [quoted lines]}}."""
    blocks: dict[int, dict[str, list[str]]] = {}
    day, slot = None, None
    for line in transcript.splitlines():
        if m := re.match(r"### J(\d+) — ", line):
            day, slot = int(m.group(1)), None
            blocks[day] = {}
        elif day is None:
            continue
        elif line.startswith("**Aetherix** (la veille"):
            slot = "evening"
        elif line.startswith("**Manager**"):
            slot = "reply"
        elif line.startswith("**Aetherix** (lendemain matin)"):
            slot = "morning"
        elif line.startswith("**Aetherix** (dimanche soir)"):
            slot = "recalibration"
        elif line.startswith("> ") and slot:
            blocks[day].setdefault(slot, []).append(line[2:])
    return blocks


def _expect(cond: bool, msg: str) -> None:
    if not cond:
        raise ValueError(msg)


def _match(pattern: re.Pattern, lines: list[str]) -> re.Match | None:
    return next((m for l in lines if (m := pattern.fullmatch(l))), None)


def staff_counts(lines: list[str]) -> dict[str, int]:
    """Role headcounts from the French receipt line ("Effectif : 7 serveurs · …")."""
    m = _match(STAFFING, lines)
    _expect(m is not None, "receipt has no staffing line")
    by_fr = {fr: role for role, fr in ROLE_FR.items()}
    out = {}
    for part in m.group(1).split(" · "):
        n, fr = part.split(" ", 1)
        out[by_fr[fr]] = int(n)
    return out


def _num(x: float) -> str:
    return str(int(x)) if float(x).is_integer() else str(x)


def _plural(n: int, word: str) -> str:
    return f"{n} {word}" + ("" if n == 1 else "s")


def _driver_label(key: str, d: dict, weekday: str) -> str:
    s = d["signals"]
    if key == "occupancy":
        return f"Hotel {round(s['occupancy'] * 100)}% full"
    if key == "weather_score":
        # weather_score is "seasonal weather pleasantness [0, 1]" in the generator.
        w = s["weather_score"]
        return "Poor weather" if w <= 0.3 else "Good weather" if w >= 0.7 else "Average weather"
    if key == "event_impact":
        e = s["event_impact"]
        return f"Local event (+{round(e * 100)}%)" if e else "No local event"
    if key == "weekly":
        return weekday
    if key == "yearly":
        return "Season"
    return key  # a named public holiday, e.g. "New Year's Day"


def _signed(x: float) -> str:
    return f"+{x}" if x > 0 else f"−{abs(x)}"


def _round_to_total(values: list[float], total: int) -> list[int]:
    """Whole numbers that add up to `total` (largest-remainder rounding).

    Each result is the value rounded down or up, never further than 1 away.
    """
    floors = [math.floor(v) for v in values]
    extra = total - sum(floors)
    order = sorted(range(len(values)), key=lambda i: values[i] - floors[i], reverse=True)
    for i in order[:extra]:
        floors[i] += 1
    return floors


def _evening(e: dict, d: dict, lines: list[str], weekday: str) -> dict:
    i = e["index"]
    forecast = _match(FORECAST, lines)
    _expect(forecast and [int(g) for g in forecast.groups()[:3]] == [e["predicted"], *e["range"]]
            and int(forecast.group(4)) == int(e["confidence"] * 100), f"J{i}: forecast line disagrees with ledger")
    occ = _match(OCCUPANCY, lines)
    _expect(occ is None or int(occ.group(1)) == round(d["signals"]["occupancy"] * 100),
            f"J{i}: occupancy line disagrees with drivers")
    _expect(round(d["yhat"]) == e["predicted"], f"J{i}: drivers do not add up to the forecast")

    lo, hi = e["range"]
    width = hi - lo
    width_pct = round(100 * width / e["predicted"])
    label = CONFIDENCE_LABEL[e["confidence"]]
    top_band = CONFIDENCE_BANDS[0]
    nights = round(INTERVAL_WIDTH * 5)
    confidence_text = f"{label} confidence: {lo}–{hi} covers on {nights} nights out of 5."
    confidence_detail = (
        f"The range is the model's {round(INTERVAL_WIDTH * 100)}% interval. It is {width} covers wide, "
        f"{width_pct}% of the forecast. "
        + (f"Under {round(top_band[0] * 100)}% earns the engine's top rating, {top_band[1]}. "
           if e["confidence"] == top_band[1] else
           f"The engine rates it {e['confidence']} on a scale from 0.5 (wide range) to 0.9 (under 20%). ")
        + "The rating measures how tight the range is; it is not a probability."
    )

    # Whole covers, rounded so the breakdown adds up exactly to the forecast.
    # baseline = Prophet's trend: the restaurant's usual level before
    # day-of-week, season, holiday and regressor effects.
    keys = list(d["components"])
    whole = _round_to_total([d["baseline"], *(d["components"][k] for k in keys)], e["predicted"])
    baseline, effects = whole[0], whole[1:]
    drivers = sorted(
        ({"label": _driver_label(k, d, weekday), "covers": c} for k, c in zip(keys, effects) if c),
        key=lambda x: -abs(x["covers"]),
    )
    keep_case = {weekday, *(k for k in keys if k not in ("occupancy", "weather_score", "event_impact", "weekly", "yearly"))}
    top = ", ".join(f"{x['label'] if x['label'] in keep_case else x['label'][0].lower() + x['label'][1:]} "
                    f"{_signed(x['covers'])}" for x in drivers[:3])
    why = f"Why {e['predicted']}: usual level {baseline}, then {top}."

    # Staffing: the rules the service used are in the ledger, with their source.
    s = e["staffing"]
    staffed = [r for r in ROLES if s["rules"][r]["covers_per"] is not None]
    counts = {r: s[r] for r in staffed}
    usual = {r: s["rules"][r]["usual"] for r in staffed}
    sources = {s["rules"][r]["covers_per_source"] for r in staffed}
    _expect(staff_counts(lines) == counts, f"J{i}: staffing line disagrees with ledger")
    team = ", ".join(_plural(counts[r], ROLE_EN[r][0]) if r != "kitchen" else f"{counts[r]} kitchen staff"
                     for r in staffed)
    on_rules = ("on the hotel's own rules" if sources == {"hotel"}
                else "on the hotel's rules where set, defaults elsewhere" if "hotel" in sources
                else "on default rules")
    staffing_text = f"{team}, {on_rules} (usual night: {', '.join(str(usual[r]) for r in staffed)})."
    owner = "The hotel's own rules" if sources == {"hotel"} else "Rules (hotel where set, defaults elsewhere)"
    ratios = ", ".join(f"1 {ROLE_EN[r][1]} per {_num(s['rules'][r]['covers_per'])} covers" for r in staffed)
    basis = f"{owner}: {ratios}, rounded up."

    return {
        "predicted": e["predicted"],
        "range": e["range"],
        "range_width_pct": width_pct,  # (hi - lo) / predicted
        "confidence": e["confidence"],
        "confidence_label": label.lower(),
        "confidence_text": confidence_text,
        "confidence_detail": confidence_detail,
        "baseline": baseline,
        "drivers": drivers,
        "why": why,
        "staffing": {
            **counts,
            "usual": usual,
            "source": "hotel" if sources == {"hotel"} else "mixed" if "hotel" in sources else "default",
            "text": staffing_text,
            "basis": basis,
        },
    }


def _reply(e: dict, d: dict, lines: list[str], weekday: str) -> dict:
    (line,) = lines
    i = e["index"]
    if REPLY_OK.fullmatch(line):
        _expect(e["manager_feedback"] == "accepted", f"J{i}: reply disagrees with ledger")
        return {"kind": "accepted", "signal": "go", "text": "OK", "counter": e["manager_counter"]}
    m = REPLY_COUNTER.fullmatch(line)
    _expect(bool(m) and e["manager_feedback"] == "modified" and int(m.group(1)) == e["manager_counter"],
            f"J{i}: reply disagrees with ledger")
    last = d["manager_last_same_weekdays"]
    _expect(round(sum(last) / len(last)) == e["manager_counter"], f"J{i}: manager basis disagrees with ledger")
    return {
        "kind": "modified", "signal": "warn",
        "text": f"I'd say {m.group(1)} covers instead.", "counter": e["manager_counter"],
        "basis": (f"The simulated manager averages the last {len(last)} {weekday}s: "
                  f"{', '.join(map(str, last[:-1]))} and {last[-1]}."),
    }


def _morning(e: dict, lines: list[str], reply: dict) -> dict:
    i = e["index"]
    if m := QUARANTINE.fullmatch(lines[0]):
        _expect(e["bounds"] == "reject" and float(m.group(1)) == e["actual_reported"]
                and m.group(2) == e["bounds_reason"], f"J{i}: quarantine disagrees with ledger")
        return {"kind": "quarantine", "signal": "stop",
                "text": (f"Yesterday's POS figure ({m.group(1)} covers) is implausible. "
                         "It was discarded and will not feed learning. Could you check the till export?"),
                "actual": e["actual_reported"], "ape_pct": e["ape_pct"], "reason": e["bounds_reason"]}
    m = ACTUAL.fullmatch(lines[0])
    _expect(bool(m) and float(m.group(1)) == e["actual_reported"] and int(m.group(2)) == e["predicted"],
            f"J{i}: outcome line disagrees with ledger")
    actual, (lo, hi) = e["actual_reported"], e["range"]
    in_range = lo <= actual <= hi
    # Text shows whole percentages; the fields keep the ledger's 0.1 precision.
    text = (f"Actual: {m.group(1)} covers. Forecast {e['predicted']}: {round(e['ape_pct'])}% off, "
            f"{'inside' if in_range else 'outside'} the {lo}–{hi} range.")
    out = {"actual": actual, "ape_pct": e["ape_pct"], "in_range": in_range}
    if reply["kind"] == "modified":
        # Same formula as the ledger's ape_pct: |actual - estimate| / actual.
        manager_ape = round(100 * abs(actual - reply["counter"]) / actual, 1)
        text += f" Your estimate {reply['counter']}: {round(manager_ape)}% off."
        out["manager_ape_pct"] = manager_ape
    drift = any(DRIFT.fullmatch(l) for l in lines[1:])
    if drift:
        # The French message also promises wider ranges meanwhile; the demo
        # code never widens them, so that clause is left out.
        text += (" That is the third under-estimate in a row: demand seems to be shifting "
                 "(a new contract? a recurring group?). The weekly recalibration will take it into account.")
    return {"kind": "drift" if drift else "outcome", "signal": "warn" if drift else "go", "text": text, **out}


def build() -> dict:
    report = json.loads(LEDGER.read_text(encoding="utf-8"))
    ledger = {e["index"]: e for e in report["ledger"]}
    drivers = {d["index"]: d for d in json.loads(DRIVERS.read_text(encoding="utf-8"))["days"]}
    blocks = _day_blocks(TRANSCRIPT.read_text(encoding="utf-8"))
    days = []
    for i in DAYS:
        e, d, b = ledger[i], drivers[i], blocks[i]
        _expect(d["day"] == e["day"], f"J{i}: drivers and ledger dates differ")
        weekday = date.fromisoformat(e["day"]).strftime("%A")
        reply = _reply(e, d, b["reply"], weekday)
        days.append({
            "day": i,
            "date": e["day"],
            "weekday": weekday,
            "evening": _evening(e, d, b["evening"], weekday),
            "reply": reply,
            "morning": _morning(e, b["morning"], reply),
        })
    protocol = report["protocol"]
    provenance = {**PROVENANCE, "backend_commit": protocol.get("backend_commit"),
                  "staffing_rules_version": protocol.get("hotel", {}).get("rules_version")}
    return {"provenance": provenance, "days": days}


def render(data: dict) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    text = render(build())
    if "--check" in sys.argv:
        if OUT.read_text(encoding="utf-8") != text:
            print(f"{OUT.name} is stale — rerun build_homepage_loop.py", file=sys.stderr)
            return 1
        return 0
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print(text, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
