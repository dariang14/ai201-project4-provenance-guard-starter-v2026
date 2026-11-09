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

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** ___ per minute, ___ per day

**Why those numbers and not others:**
<!-- Think about two people: a real writer submitting their own work a few
     times an hour, and a script sending a thousand variations to map your
     thresholds. Your numbers have to be liveable for the first and hostile to
     the second. -->

**What a caller counts as:** <!-- per address, or per creator_id? They fail
differently — one script can look like a thousand callers, and one household
can look like one. -->

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

```

```

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->



**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

```json

```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:



---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

```json

```

**Diagnoses**

<!-- For each miss AND each broken attack: the stage and the mechanism.

     Your service has five stages: the route, signal one, signal two, the
     combining rule, and the label mapping.

     Not a diagnosis:  "The evasion attacks got through."
     A diagnosis:      "Four evasion inputs got through. All four had typos
                        added to AI-generated text. My second signal measures
                        word variety, and typos raise word variety — so it read
                        them as more human. My combining rule weights that
                        signal at 0.6, so it dragged the whole score down."

     Look for a pattern. Five failures on one signal is one problem, not five. -->



---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->



**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->



---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->



**The trade I'd make if this ran for real:**

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->



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
