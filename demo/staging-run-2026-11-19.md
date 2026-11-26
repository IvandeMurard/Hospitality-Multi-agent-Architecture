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
   share of walk-in guests. Staging has neither. It also gave the dining room a size that appears
   nowhere in its inputs.
3. **It ignored the requested form.** Asked for two sentences, it wrote a four-point memo and was cut
   off mid-word by its length limit.

Nothing caught this, because in shadow its text reaches no one. That is the concrete reason the
Orchestrator does not yet become the only way to the manager: this text would have reached one.

The run also gave the first comparison between the two paths, and they disagree in direction: the daily
recommendation said 130 covers and one more person, the Orchestrator 51 covers and five fewer. This
shows the comparison works. It says nothing about which side is right: the 130 was written by hand, and
the 51 comes from a forecast with no history for a fictional hotel.

Three runs in all, all on synthetic input. The model answered once, and that answer invented facts.

## Related

- [README](../README.md), the note under the architecture diagram: why the Orchestrator is built now,
  and why that reverses what this repo said before.
- [Proof protocol](../PROOF_PROTOCOL.md): this run is not one of its links. It tests the plumbing that
  the adoption link will need, not the model, the decision, adoption or economics.
