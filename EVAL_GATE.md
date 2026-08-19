# The Eval Gate: Blocking Merges on Model Regressions, Not on Vibes

*How Aetherix's CI stops a PR that quietly makes the forecast worse — and the evidence that let it go from advisory to blocking.*

## The problem

CI green tells you the code runs. It says nothing about whether the model still
predicts well, whether the parser still reads a manager's WhatsApp reply
correctly, or whether a prompt tweak silently degraded the reasoning behind a
recommendation. For most of this project's life, model quality was checked the
way most solo projects check it: run a script by hand, eyeball a MAPE number,
move on. That doesn't scale past one person's memory, and it means a
regression only surfaces once a manager notices the system got worse.

The eval gate closes that gap: a CI check that runs the model-quality suite on
every PR that touches model, LLM, memory, provider, or prompt code, compares
the result against a frozen baseline, and **blocks the merge** on a real
regression.

## The contract

> Any change that touches the model, the LLM, memory, providers, or prompts
> does not merge without updating the golden dataset and a green eval run.

The same pattern already used for schema drift (a separate blocking gate that
prevents Pydantic models and the database schema from diverging) applied to
model quality. If it's good enough to gate schema correctness, it's good
enough to gate whether the forecast still forecasts.

## How it decides whether to run at all

The gate first has to answer a cheaper question: does this PR touch anything
that could move a model-quality metric? It diffs the PR against `main` and
matches changed files against an explicit trigger list — the forecasting,
parsing, recommendation and memory services, the LLM/embedding provider layer,
the prompt directory, and the golden dataset itself. Touch nothing on that
list, and the gate exits clean without spending CI minutes on Prophet.

Touch something on it, and the file decides how much runs:

| Touched path | What runs |
|---|---|
| A single service (e.g. the forecast engine) | Just that layer's eval subset |
| `providers/` (LLM or embedding swap) | Full run — a provider change can move everything |
| The golden dataset | Only the layers affected by the diff |
| A prompt | Full run on every layer that prompt feeds |

A sha256 cache over the touched trigger files skips re-running the suite on a
rebase or a cosmetic push that didn't actually change any of them.

## The dataset

One JSONL file, one scenario per line, discriminated by a `category` field
rather than split across per-category files — a single file is trivially
diffable in PR review and versions natively with git. Each line carries a
schema version, a unique id, the layer it exercises (forecast, recommendation,
receipt, parser, drift, latency), the input, the expected output or accept
band, and a `failure_trigger`: a human-readable sentence stating exactly what
would make this scenario fail. That last field matters more than it looks —
it forces whoever adds a scenario to state, in advance, what "bad" means for
that case, instead of discovering it after the fact.

Scenarios are organized into an 11-category taxonomy — normal days, event
days, weather anomalies, OTA cancellation waves, weekday/weekend splits,
service mix shifts, closures, holiday eves, out-of-distribution edge cases,
parser intents, and a forward-compatible placeholder for POS anomalies. The
forecast ground truth is drawn from real values in the training series, not
invented; the parser scenarios are grounded in the deterministic behavior of
the receipt-parsing service.

## Coverage and exit codes

Coverage is defined categorically, not by line count: the percentage of
taxonomy categories with at least one passing scenario in the current run.
Line coverage measures whether a test touched the code; it says nothing about
whether the model handles a rainy Friday during a trade fair.

| Coverage | Result |
|---|---|
| ≥ 80% | PASS |
| 60–80% | WARN — flagged in the PR comment, does not block |
| < 60% | FAIL — blocks the merge |

The script's exit code carries the verdict end to end: `0` pass, `1` fail
(a regression over 3 percentage points on any category, or coverage under
60%), `2` error (the script crashed or the dataset is corrupt), `3` warn.
A sticky comment on the PR renders the same result as a Markdown table —
per-category MAPE delta, parser accuracy delta, drift status — updated in
place on every push rather than piling up new comments.

## The escape hatch, and where it stops applying

A PR can carry an `eval-exempt` label to skip the gate, but only for five
authorized reasons: a pure rename or move with no logic change, docs-only,
CI-config-only, infra-only, or test-only. The label is a human override, not
an automatic one — abuse gets caught in review, not by a script.

The harder line is which code is expected to carry eval coverage at all. Not
everything that touches "the model layer" should: a heartbeat monitor or a
dead-man's-switch dispatcher is runtime behavior, not model quality — there's
no golden-dataset scenario that makes sense for "did the alert fire," and its
correctness belongs to unit tests, not a MAPE comparison. The rule that
settled the recurring argument: if a change can move a metric in the golden
dataset, it must carry eval coverage. If it only changes when or whether a job
fires or an alert dispatches, it's a runtime guardrail, and `eval-exempt` with
an `infra` justification is the right call, not a gap to backfill later.

## From advisory to blocking

The gate shipped non-blocking first, on purpose: it runs Prophet inside CI,
and Prophet's fit is not guaranteed deterministic across environments. Turning
on blocking before trusting that determinism would have meant CI failing on
noise, and noise-driven blocking gates get disabled by the second false
alarm — which is worse than not having one.

The rollout to blocking needed evidence, not a calendar date. A canary PR — a
no-op change to a file the gate treats as a forecast trigger — forced three
consecutive Prophet runs inside the actual CI environment. All three produced
an identical forecast MAPE of 25.40%, zero regressions, and 0.00 percentage
points of run-to-run variance against the frozen baseline. The stochasticity
that had been the concern turned out to be environment drift — CI library
versions diverging from local — not Prophet itself: fit in MAP mode with
L-BFGS, and with the environment pinned, Prophet is deterministic. Freezing
the baseline from a CI run rather than a local one removed the drift, and the
gate now blocks on the only thing that was ever the point: a real regression
(exit 1) or a broken run (exit 2), never on reproducibility noise.

## What this doesn't cover yet

Stated plainly, because a gate is only as trustworthy as its stated limits:

- **LLM-as-judge for reasoning quality** — whether the system's explanation of
  a spike is factually correct — is not automated yet. It's a later phase,
  and it ships only after the judge itself is calibrated against human
  verdicts (Cohen's kappa ≥ 0.8 on a held-out calibration set), so the judge
  doesn't get to grade before it's shown it grades like a person would.
- **Full memory-recall precision** runs as a smoke check today, not the
  annotated-ground-truth evaluation a production recall system deserves.
- **Outcome-level evaluation** — did the recommendation get accepted, and did
  accepting it actually help — sits outside this gate entirely. That's the
  trust signal the closed loop is built to produce (see
  [COGNITION.md](COGNITION.md)), and it's a downstream measurement, not a
  pre-merge check.

None of that makes the gate decorative. It means the gate's honest claim is
narrower than "the AI is good": it's "this PR didn't make the model worse on
the cases we've told it to check," which is a smaller, checkable, and
actually enforced promise.

## Related

- [COGNITION.md](COGNITION.md) — why the outcome loop matters more than any
  single forecast
- [benchmark/](benchmark/) — the real-data benchmark this gate protects
  against regressing on
- [README](README.md) — what's built versus what's still design or research
