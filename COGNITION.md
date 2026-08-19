# Cognition, not just prediction

*The design thesis behind the mesh. Aetherix is the proof; Anima is the promise.*

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
what happened, which human overrode it, and who was right. That is a memory of a trade's
decisions rather than of its conversations, and the only way to get one is to run in production
for months. This system has not done that yet.

Aetherix, the F&B node, implements this loop today. The demo artifacts in
[`demo/closed-loop/`](demo/closed-loop/) show it end to end: the agent citing its drivers the
evening before, flagging a corrupted POS export, naming its own drift after three consecutive
misses, and recovering from a +25% regime shift through weekly recalibration. Sandbox data,
real mechanics, deterministic reruns.

## Extending the thesis to guests: Anima (design stage)

Anima applies the same cognitive architecture to the guest relationship. It is a **design
thesis, not a shipped system**, and we say so plainly. The published outline:

- **Four memory layers with different lifetimes.** Working memory (the current stay, expires),
  episodic memory (stay + a short tail), semantic memory (durable preferences), and an
  anonymized segment layer (what guests-like-this tend to need). Temporal separation is the
  point: most guest-AI failures come from treating everything as permanent.
- **Scope-gated access.** Any consumer must declare which layer it queries. No blanket
  "give me everything about this guest".
- **Cognition informs; it never decides.** Anima answers "who is this guest, right now?".
  A separate orchestrator, with human validation, decides what to do about it. Same boundary
  Aetherix enforces between perception and decision.
- **Privacy first, structurally.** Inferred guest state is sensitive personal data. The
  non-negotiable gate before any build: formal GDPR/CNIL analysis and a DPIA. We consider the
  privacy posture part of the product, not a compliance tax: a guest-cognition system a hotel
  cannot legally deploy is worthless.

The detailed schemas (signal contracts, confidence weighting, federation design) are
deliberately private. This page states the thesis; the proof will follow the same path
Aetherix took: build, instrument, benchmark honestly, publish the loop.

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
   "end of intervention" boundary.
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
   obligation) has no equivalent hook to attach to here.
5. **What would falsify it?** Reframed rather than answered: hospitality isn't fully SOP‑free —
   food safety, brand standards, and safety procedures exist — but the knowledge Peritia would
   want is precisely what sits *outside* the written procedure, the exceptions and local
   optimizations nobody wrote down. Which means there's no ground truth to check answers
   against, SOP or otherwise. A more useful falsification criterion may not be "matches the
   SOP" but "matches the outcome": log a captured answer next to what actually happened when a
   junior followed it — the same predict‑versus‑outcome loop Aetherix already runs. That would
   make Peritia's correctness measurable the same way the rest of the mesh is, instead of
   needing a separate evaluation frame.

## Reading list in this repo

- [`demo/closed-loop/memory_tour.md`](demo/closed-loop/memory_tour.md): what the system knows
  after 30 days
- [`demo/closed-loop/whatsapp_transcript.md`](demo/closed-loop/whatsapp_transcript.md): the
  full manager thread: anticipation, self-reports, drift detection
- [`benchmark/`](benchmark/): the real-data benchmark that motivated this whole framing
