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

- **The namespace is reserved.** The signal contract carries `staff.*` and `institutional.*`
  alongside `guest.*`. A fifth node is an addition, not a redesign.
- **The pattern is proven elsewhere.** [Lore](https://github.com/IvandeMurard/Lore) does this in
  aviation maintenance: it interviews a senior by voice after an intervention, files the
  knowledge against the machine and the conditions it applies to, and returns it to a junior
  behind the governing procedure, attributed by name and date.
- **Lore stays separate.** Folding it in would make this a hospitality product with five nodes.
  Keeping it out makes it evidence that the architecture holds in a second industry under a
  stricter regime, where a licensed technician signs the release and nothing else can.
- **Deliberately unnamed.** A functional label beats a proper noun on something with no code.

### Open questions, for whoever picks this up

None of these is answered, and each blocks the next:

1. **Who benefits?** Lore answers a junior asking a question. Here the consumer could be the
   orchestrator, an incoming manager, or the property at handover — each implying a different
   capture moment and retention rule.
2. **What triggers capture?** Lore has a natural boundary: the end of an intervention. Hotel
   operations have no equivalent. A departure is too late; a weekly prompt is abandoned by
   week three.
3. **Employee data is not lighter than guest data.** Modelling what a worker knows touches
   performance and monitoring law, and a capture system read as surveillance is dead on
   arrival whatever its architecture.
4. **How does it avoid becoming a wiki nobody writes?** Every knowledge-management project
   fails here. Voice capture is Lore's answer; whether it transfers from a hangar to a service
   floor is untested.
5. **What would falsify it?** Define the failure before building, as everything else here
   does: what does a bad answer look like, and above what rate is it unacceptable?

## Reading list in this repo

- [`demo/closed-loop/memory_tour.md`](demo/closed-loop/memory_tour.md): what the system knows
  after 30 days
- [`demo/closed-loop/whatsapp_transcript.md`](demo/closed-loop/whatsapp_transcript.md): the
  full manager thread: anticipation, self-reports, drift detection
- [`benchmark/`](benchmark/): the real-data benchmark that motivated this whole framing
