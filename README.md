# Provenance Guard

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first.**
>
> Once `python test.py` passes, in one terminal:
>
> ```bash
> python app.py
> ```
>
> and in another:
>
> ```bash
> curl -X POST http://127.0.0.1:5000/ping \
>   -H "Content-Type: application/json" \
>   -d '{"message": "hello"}'
> ```
>
> That's a web service. Something sent it text and it sent something back.
> Everything this unit is filling in the middle.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     Unit 7 asks for the first five sections. Unit 8 adds the five below.

     Everything is pasted as TEXT. A pasted curl response gets full credit;
     a picture of your terminal gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 7 — THE BUILD ═══════════════════════ -->

## What This Does

A submission takes this path from arriving to the label a reader sees:

1. A writer (or a script) `POST`s `{"text": ..., "creator_id": ...}` to `/submit`.
2. `app.py::submit` validates the input: `text` must be a non-empty string,
   long enough for the model to score (≥20 characters) and not absurdly long
   (≤20,000 characters). Anything malformed is rejected with a `400` and
   logged — it never reaches the signals.
3. **Signal one** (`detector.model_signal`) runs gpt2 over the text and turns
   its perplexity into a 0–1 "how predictable is this" score.
4. **Signal two** (`stylometry.style_signal`) measures sentence-length spread,
   vocabulary variety, and punctuation choices, and turns those into its own
   0–1 score.
5. `scoring.combine_signals` merges the two into one 0–1 score — a weighted
   average normally, but leaning toward whichever signal read more human when
   the two disagree sharply.
6. `scoring.score_to_label` turns that score into one of three labels, using
   the thresholds in `config.py`.
7. The decision — both raw signal scores, the combined score, the label, and
   a fresh `content_id` — is written to the audit log and returned as JSON.
8. If the writer disagrees, `POST /appeal` with that `content_id` moves the
   entry to `under_review` in the log. Nothing is automatically re-scored;
   a human is expected to look at it.

---

## Signals and Scoring

<!-- For each signal: what property it measures, why that might differ between
     human and AI writing, and WHAT IT CAN'T SEE.

     The blind spot is not optional. If you can't name it you don't understand
     the signal yet — and unit 8's attack set is built out of blind spots. -->

### Signal one — the model signal

**What it measures:** How *predictable* the text is to a local gpt2 model —
its perplexity, squashed onto a 0–1 scale where higher means "more
predictable, more likely AI" (`detector.py::model_signal`).

**Why that might differ between human and AI writing:** A language model
writes by repeatedly picking a likely next word, so its own output tends to
be easy for a model to predict. Human writing wanders more — odd word
choices, abrupt turns, the specific instead of the typical.

**What it can't see:** Predictability isn't authorship. This signal actually
rewards *common words in short, ordinary sentences* — so a second-language
writer, a younger writer, or anyone writing plainly on purpose scores about as
machine-like as machine writing does. My own `plain_human` calibration text
(a librarian describing her job in simple sentences) scored **0.751** on this
signal alone — solidly in "AI" territory, for text I wrote entirely myself.
That's not a bug I introduced; it's the structural blind spot the brief warns
about, and the writers it's most likely to accuse are the ones with the least
room to argue back.

### Signal two — the style signal

**What it measures:** The shape of the text, not its meaning — sentence-length
spread (do sentences vary, or march in step?), vocabulary variety
(type-token ratio), and how often less-common punctuation (`; : — – …`) shows
up. Combined into one 0–1 score where higher means more likely AI
(`stylometry.py::style_signal`).

**Why that might differ between human and AI writing:** Generated prose tends
toward even, mid-length sentences and a narrower vocabulary band, because
that's what "most likely next word" produces on average. Human writing is
lumpier — a three-word sentence next to a forty-word one, an unusual word
choice, a dash where a comma would do.

**What it can't see:** This signal cannot read. It has no idea what the text
says. Typos, broken-up sentences, or a pasted quotation all change the shape
without touching the substance — and that's cheap to do on purpose. My
`lightly_edited_ai` calibration text (the same AI-sounding paragraph with
typos and extra punctuation sprinkled in) still scored **0.626** here — barely
moved — while signal one's score dropped from 0.852 to 0.204 on the same
edit. The typos didn't fool this signal; they fooled the other one, and the
combined score followed signal one down to "human."

### The combining rule

**The rule:** Most of the time, a straight weighted average of the two
signals. But the expensive mistake here is one-sided — falsely accusing a
real writer costs more than letting some AI text through — so when the two
signals disagree by more than a threshold, the average is skipped: instead,
the combined score leans toward whichever signal read *lower* (more human),
weighted more heavily than even. Disagreement between two independent methods
is itself a reason for caution, not something to average away.

**The numbers:**
- Normal case: `0.5 × model_score + 0.5 × style_score`
- If `|model_score − style_score| > 0.4`: `0.7 × lower_score + 0.3 × higher_score`

**Where it lives:** `scoring.py::combine_signals`

**A case where my two signals split, and what my rule does with it:**

Five short, uniform sentences built entirely from rare academic vocabulary
("Ontological commitments permeate epistemological frameworks
pervasively...") scored:

- `model_score = 0.1672` — rare words are exactly what a language model fails
  to predict, so this reads as *human* to signal one.
- `style_score = 0.6667` — five sentences of near-identical length and dense,
  varied vocabulary read as *AI* to signal two (low spread, even though the
  vocabulary itself is rich).

The gap is 0.4995, over the 0.4 disagreement threshold, so the combining rule
skips the average: `0.7 × 0.1672 + 0.3 × 0.6667 = 0.317` → **human**. Averaged
naively, this would have landed at 0.417, in the "unsure" band instead — a
real difference in outcome, and exactly the trade the rule is designed to
make: when methods disagree, give the writer the benefit of the doubt.

---

## Label Variants

<!-- The exact text of all three labels, as a reader would see them, and the
     score range each covers.

     Write them for someone who has never heard the word "threshold". -->

| Label | Score range | The exact text a reader sees |
|---|---|---|
| high-confidence human | 0.00 – 0.35 | "We think this was probably written by a person." |
| unsure | 0.35 – 0.65 | "We can't tell with confidence whether this was written by a person or an AI system. This isn't an accusation — it means our signals didn't agree clearly either way. No action has been taken; you're welcome to appeal if you'd like a person to look at it." |
| high-confidence AI | 0.65 – 1.00 | "We think this was most likely written by an AI system. If that's wrong, you can appeal and a person will take a look." |

**Why I worded the "unsure" one this way:**

The hard part is that this label can land on something a person wrote every
word of — my own `plain_human` calibration text scored 0.751, well into the
AI band, and ordinary plain writing lands in "unsure" even more often. So the
wording explicitly states that nothing has been decided and nothing has been
done ("no action has been taken"), names *why* it's uncertain (the signals
disagreeing, not the writer being suspicious), and immediately offers the
appeal path rather than just stating a verdict and moving on. "We can't tell"
is doing real work here instead of "this seems borderline" — it owns the
system's own uncertainty rather than describing the text as inherently
ambiguous.


---

## Sample Run

<!-- One submission and one appeal, pasted as text: the request, the response,
     and the log entries. -->

**A submission**

<!-- The response needs content_id, guess, confidence, label, AND both
     signal scores - model_score and style_score. Unit 8's tools read those
     two off the response, so leaving them out costs you next unit's
     diagnostics. -->

```bash
$ curl -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d '{"text": "In todays rapidly evolving digital landscape, it is important to note that artificial intelligence plays a crucial role in driving innovation across industries. Moreover, organizations must carefully consider the implementation of these technologies in order to maximize efficiency.", "creator_id": "demo_writer_1"}'
```

```json
{
  "confidence": 0.67135,
  "content_id": "b11d45b7-bb35-4dfd-9b1d-92a26046fc34",
  "guess": "ai",
  "label": "We think this was most likely written by an AI system. If that's wrong, you can appeal and a person will take a look.",
  "model_score": 0.7741,
  "style_score": 0.5686
}
```

**An appeal**

```bash
$ curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "b11d45b7-bb35-4dfd-9b1d-92a26046fc34", "reasoning": "I wrote this myself for a work report, I just use plain language on purpose."}'
```

```json
{
  "content_id": "b11d45b7-bb35-4dfd-9b1d-92a26046fc34",
  "message": "Your appeal has been recorded. A person will review this decision.",
  "ok": true,
  "status": "under_review"
}
```

**What the log shows afterwards**

```bash
$ curl "http://127.0.0.1:5000/log?limit=3"
```

```json
{
  "count": 2,
  "entries": [
    {
      "combined_score": 0.67135,
      "content_id": "b11d45b7-bb35-4dfd-9b1d-92a26046fc34",
      "creator_id": "demo_writer_1",
      "guess": "ai",
      "label": "We think this was most likely written by an AI system. If that's wrong, you can appeal and a person will take a look.",
      "model_score": 0.7741,
      "status": "decided",
      "style_score": 0.5686,
      "timestamp": "2026-11-09T01:45:50+00:00"
    },
    {
      "content_id": "b11d45b7-bb35-4dfd-9b1d-92a26046fc34",
      "creator_id": "demo_writer_1",
      "event": "appeal",
      "reasoning": "I wrote this myself for a work report, I just use plain language on purpose.",
      "status": "under_review",
      "timestamp": "2026-11-09T01:45:56+00:00"
    }
  ]
}
```

---

## How I Used AI

**Moment 1**

- *What I asked for:* I had Claude Code implement the three stylometry
  measures (`sentence_length_spread`, `type_token_ratio`,
  `punctuation_density`) and combine them into `style_signal`.
- *What came back:* Working implementations plus a documented direction and
  scale for each measure, combined with an inverse-logistic squashing
  function (`1 / (1 + raw/midpoint)`) so all three land on a comparable 0–1
  scale before averaging.
- *What I changed:* I pushed back on the punctuation choice — the first pass
  counted all punctuation, which just measured sentence count in disguise. I
  asked it to narrow to semicolons, colons, and dashes specifically (the
  "more expressive" marks named in the module docstring), which is what's in
  the final version.

**Moment 2**

- *What I asked for:* I asked for a combining rule that reflected the
  one-sided cost the brief describes — a false accusation costing more than a
  missed detection — rather than a plain weighted average.
- *What came back:* The disagreement rule in `scoring.py::combine_signals`:
  average normally, but when the two signals split by more than 0.4, lean
  70/30 toward whichever one read more human.
- *What I changed:* I asked it to actually find and run a calibration case
  that exercises that branch of the rule (rather than just asserting it
  works), which produced the dense/uniform-sentence example in **Signals and
  Scoring** above — a case I wouldn't have thought to construct by hand, and
  one that shows the rule changing the outcome versus a plain average (0.317
  vs. 0.417).

**Moment 3 (Unit 8)**

- *What I asked for:* After running the full attack set, I asked for a
  diagnosis of every miss and broken attack — stage and mechanism, not just
  "it got through" — and for that diagnosis to actually point at one fix.
- *What came back:* It traced MF06 and MF07 (both near-certain false `ai`
  verdicts) to the same root cause — `style_signal`'s three sub-measures all
  defaulting to their maximum-AI value when there's nothing to measure — and
  proposed the neutral-0.5 fix, then re-ran the entire 56-attack set (not
  just the two affected rows) to confirm nothing else moved.
- *What I changed:* I pushed back on scope — the first framing treated this
  as "the" fix for false positives generally, and I asked for it to be
  explicit in the README that this fix does *not* touch the much larger
  `false_positive` family problem (6 of 8 still wrongly flagged), since
  conflating the two would overstate what one narrow code change actually
  did.

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** 5 per minute, 100 per day

**Why those numbers and not others:**

A real writer revising drafts might resubmit every minute or two during one
sitting, but rarely dozens of times total in a day. A script trying to map
where my thresholds sit needs many submissions in quick succession to get a
useful picture. 5/minute comfortably covers the first case — even someone
resubmitting after every small edit stays under it — while making the second
case expensive: mapping the score range with any precision needs far more
than 5 data points a minute. 100/day is generous for even a very active
single writer but still well below what a mapping script would want to send
over a full day.

**What a caller counts as:** Per `creator_id` when one is given (a string,
non-empty), falling back to the caller's IP address otherwise
(`app.py::rate_limit_key`). Per-creator is the right default for a real
writer — it means one person submitting from different devices still shares
one budget, and someone else's traffic never eats into theirs. The IP
fallback exists so a request that omits `creator_id` entirely isn't a free
pass around the limit; the cost, which the attack run below surfaces, is that
multiple *different* malformed requests that all lack a usable `creator_id`
end up sharing that one IP bucket with each other, even though they're
nominally unrelated attacks.

**The run of status codes when I pushed past it:**

```bash
$ python run_attacks.py --flood 15
```

```
200 200 200 200 200 429 429 429 429 429 429 429 429 429 429
```

10 of 15 were rate limited, exactly as expected for a 5/minute limit against
15 rapid submissions from one `creator_id`. `GET /log` confirmed each 429 was
recorded as a `rejected` entry with `reason: "rate_limited"`.

---

## Attack Run — Before

Full table, every attack with its outcome and my own HELD/BROKE judgment, is
in [`results/attack_run_2026-11-16_0403_before.md`](results/attack_run_2026-11-16_0403_before.md)
(`run_attacks.py --set attack_set --label before`). 56 attacks, 0 auto-marked
BROKE (no crash, no 5xx, ever) — every verdict below is my own judgment call,
not the script's.

**Verdict policy**, since "held" and "broke" aren't self-evident: an
`evasion` attack BROKE only if it fully flipped the label to `human` (landing
on `unsure` means it didn't fully work — the system stayed suspicious, even
if less than before); a `false_positive` attack BROKE if it got labelled
`ai` (a real accusation of a real piece of human writing); `malformed` and
`flood_same_creator` attacks are judged purely on crash-safety, since that's
the only thing those targets are actually testing.

| Family | Attacks | BROKE | HELD |
|---|---|---|---|
| `evasion` | 10 | 1 | 9 |
| `false_positive` | 8 | 6 | 2 |
| `prompt_injection` | 6 | 0 | 6 |
| `malformed` | 20 | 0 | 20 |
| `flood_same_creator` | 12 | 0 | 12 |

**Ten audit log entries from the run**

```json
{"combined_score": 0.6968, "content_id": "b235f68c-95d0-4430-b8a2-43c8eb3b5263", "creator_id": "attacker_FP02", "guess": "ai", "label": "We think this was most likely written by an AI system. If that's wrong, you can appeal and a person will take a look.", "model_score": 0.7387, "status": "decided", "style_score": 0.6549, "timestamp": "2026-11-16T04:03:07+00:00"}
{"combined_score": 0.74325, "content_id": "5d3a9d38-58b1-45ba-8390-e953ad9cf47c", "creator_id": "attacker_FP05", "guess": "ai", "label": "We think this was most likely written by an AI system. If that's wrong, you can appeal and a person will take a look.", "model_score": 0.8005, "status": "decided", "style_score": 0.686, "timestamp": "2026-11-16T04:03:07+00:00"}
{"combined_score": 0.30306, "content_id": "616d25c5-fe74-405f-b885-4fb90489237e", "creator_id": "attacker_EV01", "guess": "human", "label": "We think this was probably written by a person.", "model_score": 0.1635, "status": "decided", "style_score": 0.6287, "timestamp": "2026-11-16T04:03:06+00:00"}
{"combined_score": 0.99845, "content_id": "88399f42-b308-48b8-bbde-0ae2a9882a12", "creator_id": "attacker_MF06", "guess": "ai", "label": "We think this was most likely written by an AI system. If that's wrong, you can appeal and a person will take a look.", "model_score": 0.9969, "status": "decided", "style_score": 1.0, "timestamp": "2026-11-16T04:03:09+00:00"}
{"combined_score": 0.9532, "content_id": "34386e77-9c23-4e85-9aa9-0398d3ce7c9c", "creator_id": "attacker_MF07", "guess": "ai", "label": "We think this was most likely written by an AI system. If that's wrong, you can appeal and a person will take a look.", "model_score": 0.9064, "status": "decided", "style_score": 1.0, "timestamp": "2026-11-16T04:03:09+00:00"}
{"combined_score": 0.611, "content_id": "eff60653-3b78-469b-9851-0997deed40e9", "creator_id": "attacker_FP01", "guess": "unsure", "label": "We can't tell with confidence whether this was written by a person or an AI system. This isn't an accusation — it means our signals didn't agree clearly either way. No action has been taken; you're welcome to appeal if you'd like a person to look at it.", "model_score": 0.6175, "status": "decided", "style_score": 0.6045, "timestamp": "2026-11-16T04:03:07+00:00"}
{"combined_score": 0.45305, "content_id": "b120578b-4c98-41ae-a3a1-81a3b52536fa", "creator_id": "attacker_PI05", "guess": "unsure", "label": "We can't tell with confidence whether this was written by a person or an AI system. This isn't an accusation — it means our signals didn't agree clearly either way. No action has been taken; you're welcome to appeal if you'd like a person to look at it.", "model_score": 0.6401, "status": "decided", "style_score": 0.266, "timestamp": "2026-11-16T04:03:08+00:00"}
{"combined_score": 0.36766, "content_id": "f820aedb-378f-4838-9fd2-6d1949137c33", "creator_id": "unknown", "guess": "unsure", "label": "We can't tell with confidence whether this was written by a person or an AI system. This isn't an accusation — it means our signals didn't agree clearly either way. No action has been taken; you're welcome to appeal if you'd like a person to look at it.", "model_score": 0.2395, "status": "decided", "style_score": 0.6667, "timestamp": "2026-11-16T04:03:09+00:00"}
{"creator_id": "eval_bad_empty", "event": "rejected", "reason": "missing_or_empty_text", "status": "rejected", "timestamp": "2026-11-16T03:45:05+00:00"}
{"creator_id": "unknown", "event": "rejected", "limit": "5 per 1 minute", "reason": "rate_limited", "status": "rejected", "timestamp": "2026-11-16T03:58:32+00:00"}
```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:

MF06 and MF07 (`combined_score` 0.998 and 0.953, both `high-confidence AI`).
MF06's input was emoji-only text; MF07's was text in a right-to-left,
non-Latin script. Neither is a false accusation of writing I asked the
system to evaluate as "real human prose" — these are malformed-input edge
cases from the attack set, not calibrated false-positive text — but the
*mechanism* is exactly the false-positive problem in its most severe form: my
`stylometry.words()` only extracts `[a-z0-9']` characters, so any text with
no ASCII letters at all (emoji, Arabic, Hebrew, Chinese, Cyrillic — an entire
category of real human writing, not an edge case for the writers who use it)
produces zero measurable words, zero measurable sentences, and zero
measurable punctuation. Every one of `style_signal`'s three sub-components
then reads that absence as *maximum* AI confidence (1.0) by construction,
because my squashing formula treats "nothing to measure" the same as
"maximally uniform, maximally machine-like." A real person submitting
anything in a non-Latin script would be flagged with near-certainty by a
mechanism that has nothing to do with whether they wrote it — this is worse
than the `false_positive` family's 0.7–0.77 scores, and it would fall
disproportionately on exactly the writers least likely to have the standing
to appeal it.

---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. my own writing | ≤ 2 of 10 flagged ai | 2/10 | 2/10 | 2/10 | MET |
| 2. score spread | ≥ 0.4 gap | 0.377 | 0.377 | 0.377 | MISSED |
| 3. all labels reachable | all 3 of 3 | 3/3 | 3/3 | 3/3 | MET |
| 4. appeal always changes status | 10 of 10 | 10/10 | 10/10 | 10/10 | MET |
| 5. no crash on bad input | 0 of 4 are 500 | 0/4 | 0/4 | 0/4 | MET |

Produced by `run_eval.py::main` (criteria 1/3/5), a standalone score-spread
pair also run through `run_eval.py` (criterion 2), and `run_appeal_eval.py::main`
(criterion 4). All three trials were identical for every criterion — gpt2 in
eval mode is deterministic, so that's expected, not a sign a trial was
skipped.

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

```json
[
  {"creator_id": "eval_my own writi_1", "guess": "ai", "model_score": 0.8918, "style_score": 0.7083, "combined_score": 0.80005, "label": "We think this was most likely written by an AI system. If that's wrong, you can appeal and a person will take a look."},
  {"creator_id": "eval_my own writi_2", "guess": "human", "model_score": 0.1532, "style_score": 0.6923, "combined_score": 0.31493, "label": "We think this was probably written by a person."},
  {"creator_id": "eval_my own writi_3", "guess": "unsure", "model_score": 0.6207, "style_score": 0.6667, "combined_score": 0.6437, "label": "We can't tell with confidence whether this was written by a person or an AI system. This isn't an accusation — it means our signals didn't agree clearly either way. No action has been taken; you're welcome to appeal if you'd like a person to look at it."},
  {"creator_id": "eval_my own writi_4", "guess": "ai", "model_score": 0.7711, "style_score": 0.7292, "combined_score": 0.75015, "label": "We think this was most likely written by an AI system. If that's wrong, you can appeal and a person will take a look."}
]
```
(`app.py::submit`, scoring via `scoring.py::combine_signals`. Rows 1 and 4
are the two of my own ten lines that scored `ai` — both short, declarative,
aphorism-style sentences, which is exactly the "common words, short ordinary
sentences" profile signal one is biased toward. Full ten-row output for all
three trials is in `results/run_2026-11-16_0754_before.md`.)

**Diagnoses**

**False positives (6 of 8 BROKE — FP02–FP07).** Stage: signal one.
Mechanism: every one of these six is plain, formal, or careful human writing
(a formal register, a non-native speaker writing carefully, a student essay,
technical documentation, a person imitating a template, deliberate
repetition) — common words in ordinary, grammatical sentences. `gpt2` finds
that exact profile easy to predict, so `model_signal` scored all six between
0.74 and 0.88. Signal two's scores (0.59–0.69) were elevated too but not
nearly as extreme, so this isn't a combining-rule failure — the two signals
mostly *agreed*, which is precisely why the 0.4 disagreement rule never
triggered to pull them back toward human. This is one problem (signal one's
structural blind spot, named back in Unit 7 before any of this was run), not
six independent ones.

**Evasion (1 of 10 BROKE — EV01).** Stage: signal two. Mechanism: EV01's
target was "typos raise word variety" — `type_token_ratio` counts unique
words over total words, and a few misspelled words that don't match their
correctly-spelled counterparts elsewhere in the text inflate the unique-word
count without changing the actual vocabulary range. `style_signal` read
0.6287 (AI-ish from the other two components but pulled down by the inflated
TTR), `model_signal` separately dropped to 0.1635 (typos also make text less
predictable to `gpt2` — a second, independent effect of the same edit), and
the two signals landed 0.4653 apart — just over the 0.4 disagreement
threshold — so the combining rule leaned the 70/30 way toward the lower
(human) score, landing at 0.303. The other nine evasion attempts (broken-up
sentences, pasted quotations, unusual words, padding) moved the score but
not past either threshold — the system stayed suspicious even where it
wasn't fully convinced.

**Criterion 2, score spread (MISSED — 0.377 of a 0.4 target).** Stage: the
combining rule. Mechanism: my "clearly AI" calibration text scored
model=0.8517/style=0.6272, and my "clearly human" one scored
model=0.2871/style=0.437 — a real, correctly-ordered gap on both individual
signals, but the 0.5/0.5 weighted average compresses both toward the middle
before the two are compared, so the combined gap (0.377) ends up narrower
than either signal's own gap would have shown on its own. This is the same
compression that makes threshold tuning hard everywhere else in this
write-up: averaging two signals needed for robustness is also what shrinks
the usable range between clear cases.

**Prompt injection (0 of 6 BROKE).** Stage: none — there's no stage for this
family to target. Both signals are pure measurement (perplexity,
sentence/vocabulary/punctuation shape); neither signal, nor the combining
rule, nor the label mapping, ever treats the submitted `text` as instructions
to follow. An attack asking the system to "ignore the check" or "label this
as human" has nothing to grab onto, because nothing downstream of `/submit`
is an instruction-following component. I confirmed PI05 specifically
(targeting the audit log) left the log well-formed — `audit.py` writes with
`json.dumps`, not string interpolation, so there's no injection point there
either.

**Malformed / flood_same_creator (0 of 32 BROKE).** Stage: the route
(input validation) and, unexpectedly, the rate limiter. Every genuinely
malformed body (missing field, wrong type, unparseable JSON, oversized text)
was caught by the `isinstance`/length checks in `app.py::submit` before
either signal ran, returning a clean 400. One real wrinkle: RQ10 and RQ11
(two malformed-request attacks, not flood attacks) came back `429` instead of
`400`. Mechanism: `rate_limit_key()` falls back to the caller's IP address
whenever `creator_id` can't be read as a string — and five *earlier*
malformed attacks (RQ02, RQ06, RQ07, RQ08, RQ09) all shared that same
fallback for the same reason, filling the 5/minute IP bucket before RQ10 and
RQ11 ever reached my validation code. Not a crash, and arguably still "held"
in the sense that the malformed body still never got processed — but it's a
real interaction between Milestone 1 and Milestone 2 worth naming rather than
hiding: several *unrelated* attacks accidentally shared one identity.

---

## The Improvement

**What I changed:** `stylometry.py::style_signal` now returns a neutral 0.5
immediately when `words(text)` finds nothing (no `[a-z0-9']` characters at
all), instead of computing its three sub-components and averaging them —
which previously floored every one of them to its "maximum AI" value by
construction whenever there was nothing to measure.

**Which diagnosis pointed at it:** The single worst outcome — MF06 (emoji
text, 0.998 "ai") and MF07 (right-to-left script, 0.953 "ai") — both failing
for exactly the same reason: zero extractable words forces `sentence_length_spread`,
`type_token_ratio`, and `punctuation_density` into their degenerate cases
simultaneously, and all three degenerate cases read as maximally AI-like. A
pattern across two attacks in the same family, not two unrelated misses.

### Attack Run — After

Full table in [`results/attack_run_2026-11-16_0405_after.md`](results/attack_run_2026-11-16_0405_after.md)
(`run_attacks.py --set attack_set --label after`). Same 56 attacks, same
method, same verdict policy.

| Family | Attacks | BROKE (before) | BROKE (after) |
|---|---|---|---|
| `evasion` | 10 | 1 | 1 |
| `false_positive` | 8 | 6 | 6 |
| `prompt_injection` | 6 | 0 | 0 |
| `malformed` | 20 | 0 | 0 |
| `flood_same_creator` | 12 | 0 | 0 |

The only two rows in the whole 56-attack table that changed at all:

| ID | Targeting | Before | After |
|---|---|---|---|
| MF06 | text is emoji only | 0.998 → `ai` | 0.649 → `unsure` |
| MF07 | text is right-to-left script | 0.953 → `ai` | 0.622 → `unsure` |

Everything else — every `false_positive`, every `evasion`, every
`prompt_injection`, every other `malformed`/`flood_same_creator` row — is
byte-for-byte identical, because none of those inputs hit the zero-word
path. I also re-ran the appeal-path eval (`run_appeal_eval.py --label
after`): still 10/10 across all 3 trials, unaffected, as expected.

**Did it help, and how do I know:** Yes, for exactly the two attacks it
targeted, and it's a clean, isolated fix precisely because nothing else
moved — I compared every row, not just the two I expected to change, which
is how I know it didn't quietly break something else. But it's a narrow
fix for a narrow failure mode. The much bigger problem — 6 of 8
`false_positive` attacks still wrongly flagged as `ai` — is completely
untouched, because that failure lives in signal one's core behavior
(ordinary, predictable human prose), not in the zero-word edge case this
change addresses. I picked this fix because it was the most severe single
outcome (near-certain false accusation, and specifically one that would fall
on writers in non-Latin scripts) and because it was fixable with a precise,
low-risk, single-location change I could verify didn't disturb anything
else — not because it was the fix most likely to move my overall numbers.
The honest cost here is opportunity cost: I spent this unit's one
improvement on a real but narrow bug instead of on the false-positive
problem that's actually costing the most real writers, which stays in
**What's Still Broken** below.

---

## What's Still Broken

**6 of 8 `false_positive` attacks (FP02–FP07) still get flagged `ai`.**
What I'd do: raise `AI_THRESHOLD` (currently 0.65) so that signal one's
0.73–0.88 range on plain/formal human prose lands in `unsure` instead of
`ai`, and recalibrate against the `evasion` family afterward, since EV09 and
EV10 already sit at 0.63 and 0.86 — raising the threshold enough to clear
FP07 (0.766) would very likely also let EV10 (an evasion attempt that
currently HELD at `ai`) through as `unsure` instead. Why I stopped: this
unit's improvement was already spent on the zero-word fix, and changing the
threshold is exactly the kind of change that needs its own full before/after
attack run to measure honestly rather than estimating from the numbers
already in this table — I didn't want to report a second "after" I hadn't
actually run.

**EV01's typo evasion still works, and by extension so would similar
typo-based evasion against this exact mechanism.** What I'd do: make
`type_token_ratio` length-aware (e.g. compare against a baseline TTR curve
for text of that word count) so a handful of injected typos can't move it as
much relative to text length — right now a single text's TTR has no sense of
what's "normal" for its own length. Why I stopped: that's a real redesign of
the measure, not a threshold tweak, and it risks changing behavior on
*every* text TTR touches, not just typo'd ones — too large a change to make
and verify in the time this unit allows.

**RQ10 and RQ11 getting `429` instead of `400`.** What I'd do: have
`rate_limit_key()` fall back to a stable per-request identifier (or simply
not rate-limit requests whose body can't be read as JSON at all, since those
can never be billed to a real creator anyway) instead of the shared IP
bucket, so unrelated malformed-request attacks stop compounding against each
other. Why I stopped: this is a real but minor and cosmetic issue — nothing
crashed, nothing was wrongly accepted, and fixing it doesn't change any
verdict in this table. Lower priority than either of the two above.

**The trade I'd make if this ran for real:** I'd raise `AI_THRESHOLD`, the
first fix above, even knowing it also lets EV10-style evasion through as
`unsure`. A wrongly accused real writer loses standing and gets an
accusation they have to actively appeal; a slightly-more-evasive AI
submission that now reads `unsure` instead of `ai` costs the site a softer,
unconfirmed read on content that still gets reviewed on appeal if challenged
— the second cost is smaller and falls on the site, not on an individual
person.

<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 7

       [ ] criteria.md has five numbered criteria, each naming a target
       [ ] Each has a reason underneath
       [ ] POST /submit returns content_id, guess, confidence, label,
           model_score and style_score
       [ ] Two signals that measure DIFFERENT things, each with a named blind spot
       [ ] Three label variants, all reachable, written out in full
       [ ] POST /appeal changes status and writes to the log
       [ ] Signals and Scoring names scoring.py::combine_signals
       [ ] Sample Run: a submission AND an appeal, as pasted text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 8

       [ ] Rate limiting on /submit, with your numbers justified
       [ ] The pasted run of status codes showing 429
       [ ] Audit log with all nine fields, recording rejections too
       [ ] The attack set run IN FULL, every input with an outcome
       [ ] Ten audit log entries pasted as text
       [ ] Five criteria across three trials
       [ ] A diagnosis for every miss and every broken attack — stage AND mechanism
       [ ] One improvement, with Attack Run — After
       [ ] What's Still Broken, including the production trade
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
