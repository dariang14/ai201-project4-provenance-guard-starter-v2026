"""
Signal two: the style signal. ← YOU BUILD THIS IN MILESTONE 4

Signal one reads the text for meaning. This one measures it *as text* — the
shape of it, without understanding a word.

Three measures are stubbed below because the brief names those three. They are
stubs, not implementations: what they compute is yours, and so is how you
combine them.

    sentence_length_spread   do sentences vary in length, or march in step?
    type_token_ratio         how much of the vocabulary repeats?
    punctuation_density      how much punctuation, and how varied?

Why these might differ between human and AI writing: generated prose tends
toward even, mid-length sentences and a narrower band of vocabulary, because
that's what "most likely next word" produces on average. Human writing is
lumpier — a three-word sentence next to a forty-word one.

⚠️ **The blind spot, which you have to name in Milestone 1.**

This signal cannot read. It has no idea what the text says. Anything that
changes the shape without changing the substance moves it — adding typos,
breaking up sentences, pasting in a quotation. That is a very cheap thing for
someone to do on purpose, and unit 8's attack set will do it to you.

Build each function on its own and call it from a terminal before you wire
anything together:

    python stylometry.py "some text to look at"
"""

import re
import statistics


def sentences(text: str) -> list[str]:
    """Split into sentences. Rough and good enough — given to you."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p.strip()]


def words(text: str) -> list[str]:
    """Split into lowercase words, punctuation stripped. Given to you."""
    return re.findall(r"[a-z0-9']+", text.lower())


# ── The three measures — YOU BUILD THESE ─────────────────────────────────────

def sentence_length_spread(text: str) -> float:
    """
    How much sentence length varies, as a coefficient of variation
    (stdev / mean word-count-per-sentence).

    Returns:
        A float, 0.0 or higher. **Higher means more human** — real writers mix
        short and long sentences; generated text tends to march at a fairly
        even pace. A single sentence (or an empty string) has no variation to
        measure, so it returns 0.0 — the most machine-like reading, since that
        is also what a flat, unvarying text looks like on this measure.
    """
    lengths = [len(words(s)) for s in sentences(text)]
    lengths = [n for n in lengths if n > 0]
    if len(lengths) < 2:
        return 0.0
    mean = statistics.mean(lengths)
    if mean == 0:
        return 0.0
    return statistics.stdev(lengths) / mean


def type_token_ratio(text: str) -> float:
    """
    Unique words over total words.

    Returns:
        A float between 0 and 1. **Higher means more human** — a wider,
        less repetitive vocabulary. Falls as text gets longer regardless of
        who wrote it (common words repeat), so it's only informative for
        texts of broadly similar length — a blind spot worth naming.
    """
    tokens = words(text)
    if not tokens:
        return 0.0
    return len(set(tokens)) / len(tokens)


def punctuation_density(text: str) -> float:
    """
    How much of the more expressive punctuation shows up, per sentence.

    Counts semicolons, colons, em/en dashes, and ellipses — not commas or full
    stops, which are too common to distinguish anyone. **Higher means more
    human.** These marks take a deliberate choice to reach for; generated text
    tends to lean on plain commas and periods instead.

    Returns:
        A float, 0.0 or higher (marks per sentence).
    """
    sents = sentences(text)
    if not sents:
        return 0.0
    marks = len(re.findall(r"[;:–—]|\.\.\.", text))
    return marks / len(sents)


# ── Combining them ───────────────────────────────────────────────────────────

def style_signal(text: str) -> float:
    """
    The style signal as a 0–1 score. **Higher means more likely AI.**

    All three measures above are written as "higher means more human", so each
    gets flipped and squashed onto (0, 1] before combining:

        ai_component = 1 / (1 + raw / midpoint)

    `raw = 0` (no spread, no interesting punctuation) maps to `1.0` — the most
    AI-ish reading. Larger `raw` pushes toward `0.0`. `type_token_ratio` is
    already 0–1, so it's just inverted (`1 - ttr`) rather than squashed.

    Midpoints (where a measure reads as a coin flip, 0.5):

        sentence_length_spread   0.5   (coefficient of variation)
        punctuation_density      0.5   (interesting marks per sentence)

    The three components are then averaged with equal weight. Equal weight is
    a starting assumption, not a finding — the four calibration inputs
    (clearly AI, clearly human, plain conventional human, lightly-edited AI)
    are what should actually confirm or challenge it.

    ⚠️ Blind spot: none of these three can read. A pasted quotation, a
    deliberately broken-up sentence, or scattered typos moves this signal
    without changing what the text says — see the module docstring.
    """
    spread = sentence_length_spread(text)
    ttr = type_token_ratio(text)
    punct = punctuation_density(text)

    spread_component = 1.0 / (1.0 + spread / 0.5)
    ttr_component = 1.0 - ttr
    punct_component = 1.0 / (1.0 + punct / 0.5)

    score = (spread_component + ttr_component + punct_component) / 3.0
    return round(min(max(score, 0.0), 1.0), 4)


if __name__ == "__main__":
    import sys

    text = " ".join(sys.argv[1:]) or (
        "The system works well. It handles most cases correctly and provides "
        "good results. Users generally find it easy to use and understand."
    )

    print(f"{len(sentences(text))} sentences, {len(words(text))} words\n")
    print(f"sentence_length_spread   {sentence_length_spread(text)}")
    print(f"type_token_ratio         {type_token_ratio(text)}")
    print(f"punctuation_density      {punctuation_density(text)}")
    print(f"style_signal             {style_signal(text)}   (higher = more likely AI)")
    print("\nAll zeros? These are stubs — Milestone 4 is where you build them.")
