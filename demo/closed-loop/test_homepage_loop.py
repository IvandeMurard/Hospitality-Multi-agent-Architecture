"""homepage-loop.json must be exactly what the ledger + transcript + drivers produce.

    python -m unittest discover -s demo/closed-loop
"""
import json
import math
import unittest

import build_homepage_loop as b


def _load(path):
    return json.loads(path.read_text(encoding="utf-8"))


class HomepageLoopTest(unittest.TestCase):
    def setUp(self):
        self.out = _load(b.OUT)
        self.ledger = {e["index"]: e for e in _load(b.LEDGER)["ledger"]}
        self.drivers = {d["index"]: d for d in _load(b.DRIVERS)["days"]}

    def test_committed_file_matches_sources(self):
        self.assertEqual(self.out, b.build())

    def test_raw_numbers_are_ledger_values(self):
        for d in self.out["days"]:
            e = self.ledger[d["day"]]
            self.assertEqual(d["date"], e["day"])
            self.assertEqual(d["evening"]["predicted"], e["predicted"])
            self.assertEqual(d["evening"]["range"], e["range"])
            self.assertEqual(d["evening"]["confidence"], e["confidence"])
            for role in b.ROLES:
                if e["staffing"]["rules"][role]["covers_per"] is not None:
                    self.assertEqual(d["evening"]["staffing"][role], e["staffing"][role])
                    self.assertEqual(d["evening"]["staffing"]["usual"][role], e["staffing"]["rules"][role]["usual"])
            self.assertEqual(d["reply"]["kind"], e["manager_feedback"])
            self.assertEqual(d["reply"]["counter"], e["manager_counter"])
            self.assertEqual(d["morning"]["actual"], e["actual_reported"])
            self.assertEqual(d["morning"]["ape_pct"], e["ape_pct"])

    def test_staffing_follows_the_hotels_rules_on_every_ledger_day(self):
        hotel = json.loads((b.HERE / "sandbox_hotel.json").read_text(encoding="utf-8"))["parameters"]
        param = {"servers": "covers_per_server", "hosts": "covers_per_host",
                 "runners": "covers_per_runner", "kitchen": "covers_per_kitchen_staff"}
        for e in self.ledger.values():
            for role in b.ROLES:
                rule = e["staffing"]["rules"][role]
                self.assertEqual(rule["covers_per"], hotel[param[role]], (e["index"], role))
                self.assertEqual(rule["covers_per_source"], "hotel", (e["index"], role))
                self.assertEqual(math.ceil(e["predicted"] / rule["covers_per"]), e["staffing"][role],
                                 (e["index"], role))

    def test_no_alert_on_a_budget_nobody_set(self):
        for e in self.ledger.values():
            self.assertNotIn("labor_budget_exceeded", e["staffing"]["sanity"]["flags"], e["index"])

    def test_confidence_bands_reproduce_every_ledger_day(self):
        for e in self.ledger.values():
            rel = (e["range"][1] - e["range"][0]) / e["predicted"]
            band = next((c for limit, c in b.CONFIDENCE_BANDS if rel < limit), 0.5)
            self.assertEqual(band, e["confidence"], e["index"])

    def test_drivers_add_up_to_every_forecast(self):
        for i, e in self.ledger.items():
            d = self.drivers[i]
            self.assertAlmostEqual(d["baseline"] + sum(d["components"].values()), d["yhat"], places=6)
            self.assertEqual(round(d["yhat"]), e["predicted"], i)

    def test_displayed_drivers_add_up_and_stay_within_one_cover(self):
        for d in self.out["days"]:
            ev, raw = d["evening"], self.drivers[d["day"]]
            self.assertEqual(ev["baseline"] + sum(x["covers"] for x in ev["drivers"]), ev["predicted"])
            self.assertLess(abs(ev["baseline"] - raw["baseline"]), 1)
            shown = sorted(x["covers"] for x in ev["drivers"])
            exact = sorted(v for v in raw["components"].values())
            nonzero = [v for v in exact if any(abs(v - s) < 1 for s in shown)]
            self.assertEqual(len(shown), len(nonzero))

    def test_ape_formula_matches_ledger(self):
        # The manager's error uses the ledger's own formula; prove it on the agent side.
        for e in self.ledger.values():
            if e["ape_pct"] is not None:
                a = e["actual_reported"]
                self.assertEqual(round(100 * abs(a - e["predicted"]) / a, 1), e["ape_pct"])

    def test_no_emoji_left(self):
        text = b.OUT.read_text(encoding="utf-8")
        self.assertFalse(any(ord(c) >= 0x1F000 or c in "⚠️" for c in text))


if __name__ == "__main__":
    unittest.main()
