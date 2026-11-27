# Staging run, 19 November 2026: the daily recommendation, end to end

One run, on staging, on a fictional hotel, with an anomaly injected by hand. This note says what
ran, what it proves, what it does not, and what broke on the way. It is a record of plumbing, not of
value: nothing here says the recommendation was right or that a manager would act on it.

## Status of what this note covers

| Piece | Status | Why that label |
| --- | --- | --- |
| Daily recommendation, automatic path (F&B node) | **Built** | Merged, tested, deployed, and exercised end to end on staging once |
| Orchestrator, in the shadow of that recommendation | **Synthetic PoC** | Its only run used an input written by hand |
| The Orchestrator as the only way to the manager | **Design** | Not built |

## What ran

- **Where:** the staging deployment of the F&B node, its staging database, and the real messaging
  provider, sending to the project owner's own phone. The hotel is fictional.
- **Input:** one demand anomaly written by hand: a surge for one dinner service, flagged as worth
  acting on. The scan did not produce it, because staging has no live weather, event or baseline
  signals: left alone, the scan finds nothing to report.
- **Switch:** the Orchestrator's shadow mode turned on for the run.

## What happened

| Step | Result |
| --- | --- |
| The anomaly is turned into a recommendation and stored | Yes: "Add 1 staff for 18:00–21:00", with the time left to change it |
| The Orchestrator runs beside it and is linked to it in the decision record | Yes, one run, linked |
| The message the manager receives | Unchanged: built before the Orchestrator runs, and nothing it produces is read into the message |
| The message is sent on WhatsApp | Yes, accepted by the provider at 09:48 UTC, under a minute after it was stored |

## What broke on the way

Two faults stood between the scan and the message. Both had been hidden by the same thing: the test
suite runs on a lighter database that tolerates what the production database refuses.

1. **Recommendations were never kept.** The step that writes a recommendation never confirmed its
   write, and the production database discards an unconfirmed write when the session ends. Present
   since April 2026. The demo script confirms its own writes, which is why the demo always worked.
2. **Recommendations could not be written at all.** Dates were handed to the database as text. The
   test database accepts that; the production database refuses it. So on the real database the
   automatic path had **never** produced a recommendation before this run.

Each fault now has a test that runs against the production database engine in CI. The first test
written for fault 1 replaced the writing step with a stand-in, which is why it missed fault 2; the
second runs the real step.

On staging the first fault cost nothing, because the second meant nothing was ever produced. That is
not reassuring: it means the daily recommendation rested on the demo, not on the automatic path,
until this run.

## What this run does not show

- **That the scan finds anything on its own.** The anomaly was injected. Staging has no live signals.
- **That the Orchestrator reasoned.** Its model step failed on staging (the provider rejected the
  staging credentials), and the run still reported completion. A run that completes without reasoning
  should not read as a success; that was an open fault, not a detail. Fixed the next day, see below.
- **Anything about a real hotel, a real manager or a real decision.** No hotel is connected.
- **Repeatability.** One run. It shows the path can work, not that it works every morning.

## Update, 20 November 2026: the false success is fixed

The fault above is closed. A run whose model step does not answer now ends **degraded**, with a reason
that says the model was unavailable, instead of reading as a success. A degraded run keeps its
figures on the decision record, but it never counts when the Orchestrator is compared with the daily
recommendation: the gap reads "not comparable", never zero.

Checked once on staging, the same way as above: one anomaly injected by hand on the fictional hotel,
the staging model credentials still rejected. The run ended degraded and was linked to its
recommendation. The comparison showed "not comparable". The manager's message was unchanged and was
sent.

A second fault surfaced on the way, of the same family as the two above: one way a run can end was
accepted by the code and refused by the production database. Fixed in the same change, and now
covered by a test.

What this still does not show: that the Orchestrator reasons. The model credentials on staging have not
been renewed, so no run has reasoned yet. Two runs, both on synthetic input. (Superseded on 26 November,
see below.)

## Update, 26 November 2026: the model answered, and its text is not usable

With the staging model credentials renewed, a third run, set up the same way (one anomaly injected by
hand on the fictional hotel), ended **completed**: the Orchestrator's model step answered for the first
time. The manager's message was unchanged and was sent.

What the model wrote is not usable:

1. **It opened by refusing.** It began with a line saying it can only help with food and beverage
   operations, on a request that was exactly that, then answered anyway.
2. **It invented facts.** It said its figure was driven by current bookings and by the hotel's usual
   share of walk-in guests. Staging has neither. (Corrected on 27 November: this note first said it
   also invented the dining room's size. It did not: the size was in its inputs, and its percentage
   was right. The mistake was in reading the run, not in the run.)
3. **It ignored the requested form.** Asked for two sentences, it wrote a four-point memo and was cut
   off mid-word by its length limit.

Why, found on 27 November: the instructions given to the model tell it to always cite bookings, the
walk-in share and walk-ins as its sources, whether or not it has them; the explanation request opens by
redefining the model's role, which most likely read as an attempt to hijack it and triggered the scripted
refusal line; and the two sets of instructions disagree on length. The fix is to the instructions, plus a
check that marks a run degraded when its text cites a source it was not given, refuses for no reason,
or is cut off. It was checked on staging the next day, see below.

Nothing caught this, because in shadow its text reaches no one. That is the concrete reason the
Orchestrator does not yet become the only way to the manager: this text would have reached one.

The run also gave the first comparison between the two paths, and they disagree in direction: the daily
recommendation said 130 covers and one more person, the Orchestrator 51 covers and five fewer. This
shows the comparison works. It says nothing about which side is right: the 130 was written by hand, and
the 51 comes from a forecast with no history for a fictional hotel.

Three runs in all, all on synthetic input. The model answered once, and that answer invented facts.
(Superseded on 27 November, see below.)

## Update, 27 November 2026: the fix, checked once

The fix to the instructions and the check on the text were deployed to staging, and a fourth run was set
up the same way: one anomaly injected by hand on the fictional hotel. It ended **completed**, and the
check raised nothing. The manager's message was unchanged and was sent.

What the model wrote this time:

1. **No refusal.** It went straight to the forecast.
2. **No invented source.** It cited only what it was given: the forecast, the absence of comparable
   past nights, and the absence of weather and event data. Instead of claiming bookings as a source, it
   said the figure should be checked against bookings before committing staff.
3. **Not cut off.** It ended on a full sentence.

What is still wrong: asked for two sentences, it wrote four. Nothing flags length, so nothing caught
it. Minor, and open.

What this does not show: that the fault is gone. One clean run shows the fix held once, on the case
that was seen, not that the next text will be faithful. The check is deliberately narrow: it catches
what the third run did, and a text it does not flag is not proven faithful.

The comparison was again possible, and again in the same direction: 130 covers written by hand on one
side, 50 from a forecast with no history on the other. It still says nothing about which is right.

Four runs in all, all on synthetic input. The model answered twice: the first text invented facts, the
second did not.

## Related

- [README](../README.md), the note under the architecture diagram: why the Orchestrator is built now,
  and why that reverses what this repo said before.
- [Proof protocol](../PROOF_PROTOCOL.md): this run is not one of its links. It tests the plumbing that
  the adoption link will need, not the model, the decision, adoption or economics.
