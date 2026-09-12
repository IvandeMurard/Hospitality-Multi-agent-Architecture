# Vision: why built this way, and what would make it wrong

*Dated 2026-08-19. Written before the first real pilot property goes live — re-read this
afterward. Part of it will be wrong by then. That's not a flaw in the exercise; a vision page
that survives contact with a pilot unchanged wasn't saying anything falsifiable in the first
place.*

[README](README.md) says what's built. [COGNITION.md](COGNITION.md) says why memory matters more
than prediction. This page says something narrower: which of the bets behind the architecture are
actually defensible, which ones stopped being differentiators without anyone noticing, and what
would prove the central one wrong.

Every claim below carries one of the five labels the README already defines — **Built**,
**Shadow-mode**, **Synthetic PoC**, **Design**, **Research**. `Built` means the code runs, not
that anyone uses it.

## What's actually defensible, ranked

1. **The act-and-measure loop, and specifically capturing manager overrides.** Recommend, capture
   the real outcome, name the gap between the two, recalibrate — a system missing any one of
   those four predicts into the void instead of learning. This is the mechanism worth protecting.
   **Status: Built** (the mechanism runs end to end on the F&B node) — **with zero real users and
   no accumulated corpus.** A moat claimed on a built-but-unused mechanism is a specification with
   good production values, not an advantage yet. It becomes one only by running in production
   long enough to accumulate outcomes a competitor can't copy by installing the same libraries.

   **The second return path, which isn't built.** Those four steps are one loop: they correct the
   *parameters* of the next forecast. They do not change *which* recommendations get made, or
   which ones are judged worth interrupting a manager for. A manager who overrides the same class
   of recommendation five times is not reporting a calibration error — they are reporting that the
   class shouldn't have been surfaced. Turning that into a standing constraint on what the
   orchestrator emits, rather than into another nudged threshold, is a different mechanism from
   recalibration, and this system does not have it. **Status: Design.** Naming it here because a
   loop that only ever tunes its own numbers gets more accurate and never gets wiser, and the
   override corpus — the thing ranked first on this page — is exactly the input the missing
   mechanism would consume.

   What that mechanism has to do is route the correction, because an override is not one kind of
   error. The manager who overrides is reporting that *some layer* was wrong, and which layer
   decides what the fix is:

   | What the override reveals | Where the fix has to land |
   |---|---|
   | A fact the system held and reality has since changed | The property's memory |
   | A choice the house made and nobody encoded | A recorded decision, with its owner |
   | A preference that has now recurred three times | A rule, not a nudged weight |
   | A pattern the model has never seen | The training corpus and the golden dataset |
   | A recommendation that should never have been surfaced | The significance filter upstream |
   | An action that should not have been offered at all | A closed lane |

   Only the fourth row is recalibration. The other five change something a retrain cannot reach,
   which is the whole distinction this section exists to make. **Status: Design** — and the routing
   question is the cheap part; the expensive part is that `submit_feedback_to_memory` records the
   override as free text today, so nothing currently distinguishes row one from row five
   ([MCP.md](MCP.md)).
2. **Compliance wired into the product, not bolted on.** Typed guardrail trips, a blocking CI eval
   gate (see [EVAL_GATE.md](EVAL_GATE.md)), an audited incident history. **Status: Built.** Treated
   internally as a cost for a long time — freezes, blocked merges, engineering hours. That was a
   misreading: once compliance is wired into supervision and the audit trail rather than added
   after the fact, switching providers means revalidating all of it. That switching cost is the
   point.
3. **Per-property operational memory — the Decision Ledger.** What *this* property does when it
   rains during a trade fair, and what happened the last time someone overrode the system about it.
   The name matters because "memory" describes the storage, which is commodity, while the ledger
   describes the linkage from recommendation to response to outcome, which is not
   ([COGNITION.md](COGNITION.md)). Composes over time — eight months of captured outcomes aren't
   copied, they're lived.

   Two statuses, because conflating them is how this bet gets oversold. **The ledger itself:
   Built** — the linkage runs, recommendation to response to outcome, in one auditable record.
   **The corpus inside it: Synthetic PoC** — everything it currently holds came from sandbox
   data. The capability to store and retrieve this kind of record is not the differentiator
   anymore (see below); what's not copyable is what the corpus is *made of*, and how long it
   takes to accumulate. A Built mechanism holding synthetic rows is a mechanism, not a moat.
4. **PMS-agnosticism.** The memory lives above Apaleo and Mews, not inside either. A group running
   both has one memory; a PMS-native tool only ever sees its own properties. **Status: Design** for
   the canonical schema behind this; Aetherix runs on Apaleo today.
5. **A multi-property network effect** — a new hotel starting from priors learned at similar
   properties. **Status: Research.** Not started, and deliberately not being built right now (see
   README's status table). A promise, not a proof — it doesn't get sold as one.

## What stopped being a differentiator

Three things this project used to lead with have become table stakes, independently and within
weeks of each other in mid-2026:

| Used to be the pitch | What commoditized it |
|---|---|
| "A system with operational memory" | Production-grade agent memory infrastructure (Mem0, Zep, Letta, and similar) shipped as installable libraries, some free |
| "MCP-native, callable by the PMS ecosystem" | Apaleo's own MCP server went to public general availability the same season |
| "Human-in-the-loop by design" | Multiple unrelated products in adjacent categories shipped the same approve-before-action pattern independently, in the same few weeks |

None of these three are false. They're just no longer separators — they're prerequisites, the
hygiene a serious system is expected to have. The discipline that follows: never open a pitch,
an interview, or this page's argument on any of the three. They belong in the second paragraph,
not the first.

## The central bet, stated so it can be shown wrong

**A property-management system won't go deep into F&B operational verticals** — staffing
calibrated to local labor law, capture-rate mechanics specific to F&B, weekly recalibration on
real outcomes, typed guardrails against bad training data. The reasoning: F&B is a thin slice of
a PMS's revenue (rooms dominate), and a PMS is a horizontal platform by construction — that kind
of vertical depth is exactly what a platform delegates to its marketplace rather than building
itself.

This is the load-bearing hypothesis of the whole thesis, and it is a bet, not a fact. Three
concrete signals would falsify it:

1. A PMS's own AI copilot expands from reporting into actual F&B operations — staffing,
   capture-rate management — rather than staying at the dashboard layer.
2. A PMS ships an instrumented outcome-capture loop of its own, not just a prediction.
3. An F&B-focused vendor in this space raises capital and integrates vertically into a PMS,
   closing the gap from the other direction.

None of the three has happened as of this writing. If one does, this paragraph is wrong, and the
response isn't to argue with the evidence — it's to say so and revisit the thesis.

## What this page is not

It doesn't say *how* the loop works — no decision-emission schema, no signal contract, no
mechanics of what gets logged at the moment a recommendation is made. That layer stays
unpublished by design: it's the one piece of this that isn't rebuildable just by reading about it,
which makes it the one thing worth not describing in public. What's published here is *that* the
loop exists and what it's for, not the wiring.

It also doesn't claim more than the README's status table claims. Anima is a thesis, not a
product. Peritia doesn't have code. Federated priors have no substrate. Repeating a claim on this
page doesn't upgrade its label.

## What would make the whole page wrong faster than any single bullet

If accuracy stays the headline instead of the loop. The real-data benchmark ([`benchmark/`](benchmark/))
already shows the forecast model itself is not defensible — Prophet ties a naive baseline on the
median day, and any competitor retrains a comparable model in a week. Leading with "our AI
predicts better" was always the losing argument here; leading with the loop and the compliance
wired around it is the only version of this thesis that survives a demo.

## The number the loop has to be judged on

A thesis that says the loop matters more than the accuracy needs a loop metric, or the accuracy
metric wins by default — it's the one that exists. MAPE per category is measured and gated
([EVAL_GATE.md](EVAL_GATE.md)); nothing yet measures whether the loop is working.

Two numbers, both computable from fields the MCP contract already carries — the `outcome` enum on
`submit_feedback_to_memory` ([MCP.md](MCP.md)) — and neither collectable before the pilot:

- **Acceptance rate**: accepted or modified recommendations over recommendations delivered. The
  `ignored` value is the one to watch hardest: an override is a manager engaging with the system,
  an ignore is a manager routing around it, and only the first is a learning signal.
- **Manager minutes per accepted recommendation.** This is the direct measurement of the
  interruption budget that the README calls the hard part. A system that raises acceptance by
  asking more often has not improved; it has spent someone else's attention to buy its own score.

**Status: Design** — the enum is Built, the measurement is not, and the pilot is where both become
real. The pairing is the point: acceptance rate alone is a Goodhart target, and a system optimized
on it learns to emit bland, agreeable recommendations that cost nothing to approve. Either number
read without the other is worse than neither.
