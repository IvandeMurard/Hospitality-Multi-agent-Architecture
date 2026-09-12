# Working on this repo

A map, not a manual. This file is the *agent* harness for whoever — or whatever — edits
here: the environment, the permissions, and what counts as done. The *evaluation*
harness is a different object and lives in [`EVAL_GATE.md`](EVAL_GATE.md); the two
senses of the word are disambiguated there.

This file exists because this repo holds no application code: a change here is a change
to a **claim**, so the rules below are about evidence, not style.

## What this repo is, and is not

Public meta-repo. Documentation only — no application code, no CI, no tests. The
execution nodes carry their own code and their own gates: Aetherix (private), Tacet
([public](https://github.com/IvandeMurard/tacet-app)). A statement here is a claim
*about* those repos and can only be as strong as what runs in them.

## The rule that governs everything else

Every component claim carries exactly one of the five status labels defined in
[`llms.txt`](llms.txt) — Built, Shadow-mode, Synthetic PoC, Design, Research —
and `llms.txt` is the canonical source when they disagree. **Adding a sentence does
not upgrade a label.** If a change describes something that does not run, it says
Design or Research in the same sentence that describes it, not three paragraphs later.

The corollary, which is the easier one to break: a claim repeated across README,
VISION, COGNITION and the portfolio is still one claim. Repetition is not evidence.

## Source order, for when two documents disagree

The hygiene agent detects drift between files. This is how to resolve it, so that a
detected conflict has a right answer instead of an argument:

1. **What runs in the node repos** — above every document here. A doc that contradicts
   the code is wrong, even when it is better written.
2. **[`llms.txt`](llms.txt)** for status labels and current component status.
3. **The specialist document** for its own subject: [`MCP.md`](MCP.md) for the tool
   contract, [`EVAL_GATE.md`](EVAL_GATE.md) for CI and eval mechanics,
   [`VISION.md`](VISION.md) and [`COGNITION.md`](COGNITION.md) for the thesis and what
   would falsify it.
4. **[`README.md`](README.md)** last on any detail. It summarizes the others, so on a
   conflict it is the derived copy and it is the one that gets corrected.

And when the answer is in none of them: say what could not be found. An unstated gap
is the one failure this repo's whole argument cannot survive — the documents earn their
credibility from [`EVAL_GATE.md`](EVAL_GATE.md)'s habit of publishing its own limits.

## Three boundaries that are not negotiable

1. **The loop's wiring stays unpublished.** The decision-emission schema, the signal
   contract, and what gets logged at the moment a recommendation is made are
   deliberately absent from this repo ([VISION.md](VISION.md), "What this page is
   not"). Describing *that* the loop exists is the published layer; describing how it
   is wired is not. Do not add it, and do not infer it into a diagram.
2. **No third-party corpora.** This repo is MIT. Source material — articles, threads,
   datasets, someone else's documentation — gets cited and quoted short, never vendored
   in full. Republishing someone's work under this licence is a licence problem and a
   credibility problem at once.
3. **No model identifiers in commits, PRs or prose.** Which assistant wrote a paragraph
   is not part of the record.

## Task contract, before a non-trivial change

Write these four lines first. They take a minute and they are what stops an edit from
quietly becoming a different, easier edit:

```
goal:         one sentence, the change itself — not the topic
files:        the exact paths allowed to change
done_when:    what a reader could check to confirm it landed
escalate_when: the condition under which you stop and ask instead of deciding
```

`done_when` has to be checkable by someone who did not make the change. "The section
reads better" is not a stop condition. "VISION bet 1 names the return path and labels
it Design" is.

`escalate_when` earns its line here specifically: most changes to this repo are
positioning decisions wearing documentation clothes. Reframing what the mesh is *for*,
changing which argument leads, or promoting a component's label are the owner's calls,
not an editing pass's.

## Scope discipline on corrections

When a review rejects one part of a change, fix **that part**. A rejected paragraph
that comes back as a rewritten page converts one known problem into several unknown
ones, and the correct prose that got rewritten along the way is now different rather
than better.

A correction carries: the unit, the verdict, the reason, the evidence, and the scope —
explicitly, *this file only, leave the rest*. Cap it at three attempts on the same
unit; a fourth means the problem is in the plan that produced it, and the plan is not
visible from inside the correction.

## Turn a repeated failure into infrastructure

A failure that recurs and does not change the repo will recur again. Classify it before
retrying, and make the fix permanent in the matching form:

| Failure | Permanent artifact |
|---|---|
| The editor guessed a convention that exists but was not written down | A line in this file |
| A claim drifted out of sync across files | A hygiene-agent detector, or a cross-link |
| A status label got upgraded by prose rather than by evidence | A stated check in the PR description |
| A boundary above got crossed | A rule in "Three boundaries", stated as a never |

Re-running the same change with a firmer prompt is not a fix.

## Stop conditions

Stop and hand back when: a change would need information from a private repo to be
verifiable; a diff exceeds the files named in its own contract; a claim's evidence
turns out to be another document in this repo rather than something that runs; or the
change would make the repo's argument stronger by making it less falsifiable.

That last one is the failure mode this project is most exposed to, precisely because
it is good at sounding rigorous.

## Related

- [`llms.txt`](llms.txt) — canonical status vocabulary and current component status
- [`EVAL_GATE.md`](EVAL_GATE.md) — how the same discipline is enforced in CI on the
  node that has code
