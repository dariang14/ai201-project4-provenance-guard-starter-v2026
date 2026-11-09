# Acceptance criteria — Provenance Guard

Five criteria that say what "working" means for this service, written in unit 7
**before** you built it.

**All five are yours.** None are given.

An acceptance criterion names a number or something plainly observable. *"The
detector is accurate"* is an opinion — and perfect AI detection isn't possible
anyway, so it's an opinion about something nobody can deliver. *"Of 10 pieces I
wrote myself, at most 1 is labelled high-confidence AI"* is a criterion.

Under each, write a sentence or two on **why that target**. *"I allow at most 1
false positive in 10 because on a writing site a wrong accusation costs more
than a missed detection"* is a real answer.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## Pick numbers you can defend

**Cover at least three of these five areas.** They're prompts, not a form.

| Area | A question it could answer |
|---|---|
| False positives | How often may a human's writing get called AI? |
| Score spread | How far apart should clearly-AI and clearly-human text score? |
| Label coverage | Is every one of your three labels actually reachable? |
| The appeal path | Does an appeal always change status and always get recorded? |
| Bad input | What happens when `text` is missing, empty, or enormous? |

Two things worth knowing before you pick numbers:

- **The expensive mistake is one-sided.** Missing some AI text costs the site a
  little. Accusing a real writer costs that person a lot. A criterion that
  treats both errors as equally bad is describing a system nobody would ship.
- **Unit 8 tests across three trials, and the target has to hold across all
  three.** Your first signal runs a model, so identical input can score
  differently twice. A target of "at most 1 in 10" against trials of 2, 1, 2 is
  a **miss**.

---
## 1. False positives on my own writing

Of 10 short paragraphs I write myself (not copied, not AI-assisted), **at most 2** are labelled `high-confidence AI`, across all 3 of unit 8's trials.

**Why this target:** Signal one scores predictability, and plain, ordinary human writing can look exactly as predictable as AI writing — it's the project's central known blind spot. Accusing a real writer of using AI costs that person far more than letting a few AI pieces slip past costs the site, so the tolerance here is deliberately asymmetric: I'd rather this system under-accuse than over-accuse. 2 out of 10 (20%) is generous enough to survive normal variation between trials, but still catches a detector that's flagging plain writing as AI by default.

---

## 2. Score spread between obviously-different inputs

The gap between the `combined_score` for a piece of text I'm confident is AI-generated and a piece I'm confident is human-written is **at least 0.4**, holding across all 3 trials.

**Why this target:** If the two signals can't separate the easy cases, the system has no meaningful signal at all — the hard cases (the ones that actually need a decision) will be unrecoverable. 0.4 is roughly the width of the `unsure` band itself, so a real gap means the two obvious cases land in genuinely different labels, not just different corners of the same one.

---

## 3. All three labels are reachable

Across 6 calibration inputs spread across the score range (2 aimed at each label), **all 3 labels** — `high-confidence human`, `unsure`, `high-confidence ai` — are produced at least once.

**Why this target:** A label nobody can ever reach is a dead branch of the code, and it usually means a weighted average is trapped between its two inputs (see the warning in `config.py` about the style-signal stub). This has to be checked directly rather than assumed, because the failure is silent — the service keeps answering normally, it just never says one of the three things it claims to say.

---

## 4. The appeal path always changes status and always logs

For **10 out of 10** valid appeals (a real `content_id` from a prior submission, with reasoning text), the audit log shows a `status: "under_review"` entry for that `content_id`, and `POST /appeal` never returns a 5xx.

**Why this target:** The appeal path is the only thing standing between a wrong accusation and nothing at all — it has to be perfectly reliable for every well-formed request, not just reliable on average. Zero tolerance here (10/10, not 9/10) reflects that this is the one failure mode that can't be shrugged off as a scoring judgment call; it's a correctness bug if it ever drops an appeal.

---

## 5. Malformed input never crashes the route

Across missing `text`, empty `text`, `text` of 50,000+ words, and a `null` text field — **0 of these produce a 500** (all instead return a clean 400) across 3 trials.

**Why this target:** A crash on bad input is one of the most common real failures a service like this has, and it's also the cheapest attack available — no cleverness needed, just a malformed request. The target is 0 rather than "mostly" because a crash is unambiguously a bug, not a scoring judgment call the way a borderline label is.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 8 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath, like this:

         ## 2. Uncertain cases land in the unsure band

         The system handles uncertain cases well.

         **Why this target:** ...

         > **Revised in unit 8:** Text I judged borderline scores between
         > 0.4 and 0.6 in at least 4 of 5 cases.
         >
         > **Why revised:** "well" gave me nothing to check. I couldn't
         > reach a verdict from it at all.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "At most 1 of 10 of my own pieces flagged as AI" → "at most 3
            of 10", because 1 of 10 turned out to be hard.

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
