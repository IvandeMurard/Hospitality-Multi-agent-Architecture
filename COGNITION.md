# Cognition, not just prediction

*The design thesis behind the architecture. Aetherix is the proof; Anima is the promise.*

## The argument

The prediction layer of vertical AI is commoditizing fast. Our own benchmark
([`benchmark/`](benchmark/)) shows Prophet tying a naive same-weekday baseline on the median
day, on real restaurant data. What does not commoditize is what sits around the prediction:

- **capturing outcomes** next to the forecasts that preceded them,
- **self-reporting** the miss to the human, in plain language, the next morning,
- **guarding** the training data against implausible inputs (typed, auditable rejections),
- **recalibrating** on what actually happened,
- and compounding all of it into a **per-property operational memory** that a competitor
  cannot copy by training the same model.

The order matters. Persistent agent memory became commodity infrastructure during 2026 — the
storage is not the asset, and a claim resting on "we have memory" would be resting on a library
anyone can install. The asset is the four bullets above it: a record of what was recommended,
which role overrode it and why, and what actually happened.

That object has a name here: the **Decision Ledger**. The rename was not cosmetic. "Memory"
names the storage, which is the commodity; the ledger names the *linkage* — each recommendation
tied to the response it got and the outcome that followed — which is the part a competitor
cannot install. It also retires a phrase this project used to use: not "self-improving memory",
which claims a result, but **outcome-tracked operational history**, which claims a mechanism.
The first is only earnable by demonstrating that the system learned; the second is checkable
today. **Status: Built** — the ledger consolidates records that were previously spread across
several tables, so what shipped is traceability over existing data, not a new store.

That is a memory of a trade's
decisions rather than of its conversations, and the only way to get one is to run in production
for months. This system has not done that yet.

**The general form of this argument stopped being a differentiator too.** Through 2026 the
industry converged on it under the name harness engineering: the model is not the agent, the
environment around it is where reliability comes from, and the harness — not the weights — is
where operating knowledge compounds. That is the same shape as the claim above, one level up the
stack, and it is consensus now rather than insight. It cuts both ways, so both get said. It is
evidence the shape is right, since it was arrived at independently by teams building coding
agents with nothing hospitality-specific in view. And it strips this page of any claim to
originality: what stays specific is not the shape but the filling — a memory whose unit is a
*decision and its outcome*, in a trade where the outcome is legible the next morning and the
person who overrode the system is on the payroll. The general argument is free to copy. The
corpus is not.

Aetherix, the F&B node, implements this loop today. The demo artifacts in
[`demo/closed-loop/`](demo/closed-loop/) show it end to end: the agent citing its drivers the
evening before, flagging a corrupted POS export, naming its own drift after three consecutive
misses, and recovering from a +25% regime shift through weekly recalibration. Sandbox data,
real mechanics, deterministic reruns.

## Extending the thesis to guests: Anima (Synthetic PoC)

Anima applies the same cognitive architecture to the guest relationship. **Status: Synthetic
PoC** — the four layers, a synthetic-cohort eval and a working MCP server exist; none of it has
met a real guest ([`llms.txt`](llms.txt)). So what is unproven here is not the code but the
claim, which is why the outline below is stated as a thesis and not as a result:

- **Four memory layers with different lifetimes.** Working memory (the current stay, expires),
  episodic memory (stay + a short tail), semantic memory (durable preferences), and an
  anonymized segment layer (what guests-like-this tend to need). Temporal separation is the
  point: most guest-AI failures come from treating everything as permanent.
- **Scope-gated access.** Any consumer must declare which layer it queries. No blanket
  "give me everything about this guest".
- **Cognition informs; it never decides.** Anima answers "who is this guest, right now?".
  A separate orchestrator, with human validation, decides what to do about it. Same boundary
  Aetherix enforces between perception and decision.
- **Privacy first, structurally — context, not surveillance.** Inferred guest state is
  sensitive personal data. The non-negotiable gate is not before any build, since the PoC above
  is already built; it is before any *real guest datum* enters it: formal GDPR/CNIL analysis and
  a DPIA. Stating it the looser way made this page read as stricter than the project actually
  is, which is its own kind of inaccuracy. We consider the privacy posture part of the product,
  not a compliance tax: a guest-cognition system a hotel cannot legally deploy is worthless.

**What the layers cover across a stay.** Anima is a guest memory, not a digital twin: it holds
what was said and what happened, not a model of the person. *During* the stay, requests,
interactions and events stated or recorded while the guest is in house live in working memory.
*After* it, a short episodic tail remains, and only preferences stated or repeatedly confirmed
reach semantic memory. *Before* arrival — **Design**, not in the PoC — anticipation draws on
booking data and situational context only: local transit disruption, events, weather. Tacet
produces those signals keyed by place and time, never by person; Anima links them to the booking,
so the personal-data processing stays in the one node the DPIA covers. Signals on the routes into
the property would be a Tacet extension, also **Design**. No external data about the person, and
no profiling: a first-time guest is not recognised, but can still be anticipated from the
situation they are arriving into.

**Health data stays in the stay — Design.** An allergy, or a dietary restriction that reveals a health condition, is health data
(GDPR art. 9), not a preference. It is used only when the guest states it for a concrete service,
on explicit consent, held in working memory, and never promoted to a durable preference or used
for inference. Keeping it for a future stay would need its own explicit, separate consent. The
layer's expiry is a minimisation measure; it is not the legal basis, and the DPIA decides.

The detailed schemas (signal contracts, confidence weighting, federation design) are
deliberately private. This page states the thesis; the proof will follow the same path
Aetherix took: build, instrument, benchmark honestly, publish the loop.

### What a guest-side ledger would have to distinguish

**Status: Research.** The Decision Ledger is Built on the F&B node, where the loop closes because
the outcome is arithmetic — the POS counts the covers by the end of service. Asking what the
equivalent object would be on the guest node produces six candidate terms: what the system
*inferred*, what the guest *said*, what actually *happened*, what could or should have happened
instead, what went well or badly, and what deserves to be kept. They are worth writing down
because they are not one list. They are three kinds of object, and treating them as one is the
shortest path back to the omniscient-concierge framing this page exists to refuse.

| Term | Kind of object | Observable? |
|---|---|---|
| What was inferred / what was said | Provenance of a claim | Yes — the cheapest of the six, and the outline above omits it; it is carried on the published [Anima page](https://ivandemurard.com/anima) instead |
| What happened | Trace of an event | Only as guest *actions*. Never as guest state |
| What could or should have happened | Counterfactual | No. The room that was not assigned left no trace |
| What went well or badly | Judgement | Not without a named grader, and there is none |
| What deserves to be kept | Decision | Not a record at all — and the one act that manufactures the sensitive data |

Three consequences, which are why this is a Research note and not a paragraph of ambition:

- **The counterfactual is not recordable, but it is elicitable — at the override.** A manager who
  rejects a suggestion is already stating what should have happened instead, for their own
  reasons, at the one moment it is legible. The Peritia section below reaches the same conclusion
  for a different node (open question 2, fourth candidate); one author reaching it twice is not
  independent evidence, but it does mean the argument is not specific to guests. It also bounds
  the claim: an override reveals a counterfactual about a *recommendation*, and says nothing about
  the stays for which nothing was recommended.
- **"What happened" has one honest measurement, and it is not satisfaction.** A guest who does
  not complain is not a guest who was served well, which is why the well/badly row stays empty.
  What can be counted without inferring anything is the **repeat rate** — how often a preference
  the system already held failed to be applied; the guest who asked for a quiet room on three
  consecutive stays and had to ask again on the fourth. It needs no new personal data and no
  grader, and it embarrasses the property rather than flattering it, which is the property a real
  metric has to have. Not measured today: there is no property to measure it on.
- **"What deserves to be kept" is where the DPIA actually bites.** Promoting an inference into
  durable memory is the act that creates sensitive personal data. The four layers currently settle
  retention by rule and decay rather than by judgement, and installing a judge there reopens
  exactly the permanent-label failure the layers exist to prevent.

This is an axis of *input*, and it does not replace the override-routing table in
[VISION.md](VISION.md), which is an axis of *output* — where a correction has to land. The two
compose rather than compete. Neither is a candidate for the typed reason class that
[MCP.md](MCP.md) still declines to invent until real managers have overridden something: that
restraint stands, and nothing in this subsection is adopted or upgrades a label.

## Extending the thesis to staff: institutional knowledge (not started)

Aetherix remembers what the property did. Anima would remember what a guest is like. Neither
remembers **what the people who work there know** — the memory that leaves fastest, when a
manager resigns or a head chef retires and a decade of context about this kitchen, these
suppliers, this Tuesday walks out with them.

Nothing is built. What exists is a reserved place and a proven pattern:

- **The architecture already admits it.** The contract governing exchanges between nodes was
  designed for a domain none of them currently occupies. A fifth node would be an addition
  rather than a rewrite, which is the whole difference between a roadmap item and a rebuild.
- **The pattern is proven elsewhere.** [Lore](https://github.com/IvandeMurard/Lore) does this in
  aviation maintenance: it interviews a senior by voice after an intervention, files the
  knowledge against the machine and the conditions it applies to, and returns it to a junior
  behind the governing procedure, attributed by name and date.
- **Lore stays separate.** Folding it in would make this a hospitality product with five nodes.
  Keeping it out makes it evidence that the architecture holds in a second industry under a
  stricter regime, where a licensed technician signs the release and nothing else can.
- **Deliberately unnamed.** A functional label beats a proper noun on something with no code.

### What Peritia could answer

Two different lists, because conflating them is how a scoping document quietly turns into a
promise nobody can keep.

**Unconstrained** — the kind of question the tool is meant to eventually close:
- Why does the kitchen favor this supplier despite a higher price?
- How does this particular oven run compared to its spec sheet, and what does the team do
  about it?
- Last time this exact problem came up with this supplier or this piece of equipment, what
  happened and how was it resolved?
- What is the unwritten protocol when a recurring situation happens on a full Saturday night?
- What does an experienced host do for this type of recurring complaint, and why does it work?

**Constrained by what exists today** — technical and regulatory:
- *Technical*: Peritia inherits Lore's capture pattern, a voice interview after a bounded
  intervention. Aviation maintenance has that boundary — the end of a job on a tail number.
  Hospitality doesn't (open question 2, below). Until a trigger is defined, the tool can only
  answer questions whose capture moment is already identifiable — the end of a named incident,
  not continuous ambient capture.
- *Regulatory*: knowledge that stays strictly professional and non‑nominative as to an
  individual's performance — a recipe fix, a supplier quirk, a piece of equipment's behavior —
  sits outside employee‑monitoring law the same way Lore's torque‑spec deviations do. The
  moment captured knowledge shifts from "what is the trick" to "how did this specific employee
  handle it," it becomes performance/behavior data and the constraint gets real. The answerable
  set, today, is bounded to transferable procedural know‑how — not staff evaluation.

### Open questions, for whoever picks this up

None of these is settled, and each still blocks the next — but each now carries a working
direction rather than a blank:

1. **Who benefits?** Working hypothesis: two consumers, not one. *The agents* — including the
   orchestrator — get a continuously improving picture of the property's operating context,
   which sharpens recommendations into something idiosyncratic rather than generic. *The
   humans* — managers and operational teams, and through them the guests — get faster
   onboarding, more automatic transmission of critical information, and an audit trail of who
   knew what. This doesn't resolve the capture‑moment question below; it means the payload has
   two destinations, which likely implies two different retention and access rules rather than
   one pipe.
2. **What triggers capture?** Candidates on the table: a fixed ritual (a recurring debrief), a
   data‑driven comparative trigger (an anomaly or a recurring pattern surfaces and the system
   asks about it), or an agent‑initiated request following a named business event. None chosen
   — this is the one place the Lore pattern doesn't transfer cleanly, since hospitality has no
   "end of intervention" boundary. **A fourth candidate, added late and currently the strongest:**
   the capture moment is the *correction*. A manager who overrides a recommendation is already
   telling the system it was wrong about something, and doing it for their own reasons rather than
   as a favour to a knowledge base. Asking one routing question at that moment — was the fact
   stale, was there a rule nobody recorded, is there a technique the system doesn't have — rides on
   work that happens anyway. Unlike the three candidates above, it asks the human for nothing
   extra, which is why it should be the one tested first.
3. **Is employee data actually the blocker?** Worth recording as a live pushback: this wasn't
   blocking for Lore, so why would it be here? The comparison holds only if Peritia stays where
   Lore stays — professional, transferable know‑how (a technique, a supplier relationship, an
   equipment quirk), never a record of how a *named individual* performs. Lore arguably sits in
   a *more* regulated domain — licensed, safety‑critical, signed release — and ships anyway,
   because the captured knowledge is about the aircraft and the procedure, not about grading the
   technician. The real risk in hospitality is scope creep: service work is more relational than
   a torque spec, so "how do you handle a difficult guest" drifts toward behavior/performance
   data in a way "how do you compensate for an oven running hot" doesn't. Read as a scope
   discipline to hold — know‑how, not conduct — not a hard legal blocker, but it needs to be a
   stated design constraint from day one, the same way "context, not surveillance" is stated for
   Anima, and ideally checked with whoever represents staff before anything ships.
4. **How does it avoid becoming a wiki nobody writes?** Agreed as a real risk, not a
   hypothetical: this can look time‑consuming and low‑value to exactly the teams whose time is
   scarcest. Still unanswered — Lore's answer (voice capture riding on an existing documentation
   obligation) has no equivalent hook to attach to here. **Partially superseded by the fourth
   candidate in question 2:** the override is the hook. It is not a documentation obligation, but it
   has the property that matters — the human is already motivated to perform it, because the
   alternative is living with an output they disagree with. That converts the problem from "get
   busy people to write things down" to "ask one well-placed question at a moment they were going
   to act anyway", which is a materially easier problem. It does not close the question: an
   override tells you a *recommendation* was wrong, and Peritia wants know-how that no
   recommendation touched.
5. **What would falsify it?** Reframed rather than answered: hospitality isn't fully SOP‑free —
   food safety, brand standards, and safety procedures exist — but the knowledge Peritia would
   want is precisely what sits *outside* the written procedure, the exceptions and local
   optimizations nobody wrote down. Which means there's no ground truth to check answers
   against, SOP or otherwise. A more useful falsification criterion may not be "matches the
   SOP" but "matches the outcome": log a captured answer next to what actually happened when a
   junior followed it — the same predict‑versus‑outcome loop Aetherix already runs. That would
   make Peritia's correctness measurable the same way the rest of the architecture is, instead of
   needing a separate evaluation frame.

## Reading list in this repo

- [`demo/closed-loop/memory_tour.md`](demo/closed-loop/memory_tour.md): what the system knows
  after 30 days
- [`demo/closed-loop/whatsapp_transcript.md`](demo/closed-loop/whatsapp_transcript.md): the
  full manager thread: anticipation, self-reports, drift detection
- [`benchmark/`](benchmark/): the real-data benchmark that motivated this whole framing
