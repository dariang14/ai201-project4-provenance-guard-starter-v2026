"""
What your test runs. ← UNIT 8, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
false positives needs your own writing. One about label coverage needs inputs
across the score range. One about the appeal path needs a real content_id.

Working that out is Milestone 3's first step, and this file is where you write
it down. `run_eval.py` runs everything here three times.

Two are filled in as examples. Replace them with what your criteria actually
need — these are a shape, not a set.

A scenario carries **either** of these:

    "texts"   a list of strings. Each is sent as {"text": ..., "creator_id": ...}
              with a creator_id made up for you. Use this for most criteria.

    "bodies"  a list of whole request bodies, sent exactly as written. Use this
              when the malformed request IS the point — empty text, no `text`
              field at all, something enormous. A bad-input criterion needs it,
              because you cannot express "the field is missing" as a string.
"""

SCENARIOS = [
    {
        "name": "my own writing",
        "criterion": 1,
        # ⚠️ PUT YOUR OWN WRITING HERE. Not AI text, not a sample from the web —
        # things you actually wrote. This is the criterion that matters most and
        # it's meaningless with someone else's prose.
        "texts": [
            "If you can get up and do what needs to be done even when you don't feel like it, you can change your life",
            "The best art perfectly captures and articulates very real human emotions and experiences",
            "Remember who you are and never forget it",
            "When the world was open and free and I could be who I wanted to be",
            "Don't live as a slave to your impulses",
            "Everything matters and it doesn't at the same time",
            "It's cooler to care, always has been",
            "Knowledge alone isn't power. The acquisition of knowledge and its application is power.",
            "Write out what you feel and read it as art. Does what I keep to myself contribute to something greater?",
            "Do it now, not later. Anti-procastinate.",
        ],
    },
    {
        "name": "score spread",
        "criterion": 2,
        # One text I'm confident is AI-generated, one I'm confident is
        # human-written — the same pair used for calibration in the Unit 7
        # README. Criterion 2 is the gap between their combined_score values,
        # which has to be read off the pasted JSON by hand (run_eval.py
        # doesn't diff two rows against each other for you).
        "texts": [
            (
                "In today's rapidly evolving digital landscape, it is important to note that "
                "artificial intelligence plays a crucial role in driving innovation across "
                "industries. Moreover, organizations must carefully consider the implementation "
                "of these technologies in order to maximize efficiency and achieve optimal "
                "outcomes. Ultimately, a comprehensive and strategic approach is essential for "
                "long-term success in this ever-changing environment."
            ),
            (
                "So I burned the rice again. Third time this week — my roommate is going to "
                "start side-eyeing the rice cooker like it personally betrayed her. I don't even "
                "know what I did differently. Same water, same everything. Ordered pizza instead, "
                "ate it standing over the sink like a raccoon, no regrets."
            ),
        ],
    },
    {
        "name": "label coverage",
        "criterion": 3,
        # Six inputs, two aimed at each label — picked from calibration runs
        # against the live service, not guessed. In order: ai, ai, unsure,
        # unsure, human, human.
        "texts": [
            (
                "In today's rapidly evolving digital landscape, it is important to note that "
                "artificial intelligence plays a crucial role in driving innovation across "
                "industries. Moreover, organizations must carefully consider the implementation "
                "of these technologies in order to maximize efficiency and achieve optimal "
                "outcomes. Ultimately, a comprehensive and strategic approach is essential for "
                "long-term success in this ever-changing environment."
            ),
            (
                "My name is Maria and I work at the library downtown. I help people find books "
                "and I also run the kids reading hour on Saturdays. I like my job because I meet "
                "a lot of nice people. Sometimes it is hard when we are short staffed but we "
                "manage. I have worked there for three years now."
            ),
            (
                "So I burned the rice again. Third time this week — my roommate is going to "
                "start side-eyeing the rice cooker like it personally betrayed her. I don't even "
                "know what I did differently. Same water, same everything. Ordered pizza instead, "
                "ate it standing over the sink like a raccoon, no regrets."
            ),
            (
                "Run. Just run and don't look back, because the tide was already closing in around "
                "the rocks and there was no time left to think about it, none at all. Go."
            ),
            (
                "In todays rapidly evolvign digital landscape, its importnat to note that AI "
                "plays a crucial role in driving innovaton across industries!! Moreover orgs must "
                "carefully consider the implementaton of these technologies, in order to maximize "
                "efficiency and acheive optimal outcomes. Ultimately a comprehensive & strategic "
                "approach is essential for long term success in this ever changing enviroment."
            ),
            (
                "Ontological commitments permeate epistemological frameworks pervasively. "
                "Phenomenological inquiry necessitates methodological rigor absolutely. "
                "Hermeneutical interpretation demands contextual sensitivity profoundly. "
                "Dialectical reasoning facilitates conceptual clarity thoroughly. "
                "Epistemic humility undergirds philosophical discourse perpetually."
            ),
        ],
    },
    {
        "name": "bad input",
        "criterion": 5,
        "bodies": [
            {"text": "", "creator_id": "eval_bad_empty"},
            {"creator_id": "eval_bad_missing"},          # no text field at all
            {"text": "word " * 50000, "creator_id": "eval_bad_huge"},
            {"text": None, "creator_id": "eval_bad_null"},
        ],
    },

    # Criterion 4 (the appeal path) isn't here on purpose: it needs a
    # submission followed by an appeal against the content_id that came back,
    # which this file's "texts"/"bodies" shape can't express — a single
    # request per entry. Tested instead with a standalone script,
    # run_appeal_eval.py, documented in the README's Run Log and Verdicts
    # section.
]


def validate() -> list[str]:
    """
    Complain about anything malformed, before a long run rather than during.

    A "bodies" scenario is deliberately exempt from the empty check — an empty
    string is the whole point of a bad-input case, and refusing to run one
    would make that criterion untestable.
    """
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("name"):
            problems.append(f"scenario {i} has no name")

        texts = scenario.get("texts")
        bodies = scenario.get("bodies")

        if texts and bodies:
            problems.append(
                f"scenario {i} ('{scenario.get('name')}') has both texts and "
                f"bodies — pick one"
            )
            continue

        if bodies:
            for j, body in enumerate(bodies, 1):
                if not isinstance(body, dict):
                    problems.append(
                        f"scenario {i}, body {j} is not a dict — bodies are whole "
                        f"request bodies, like {{'text': '', 'creator_id': 'x'}}"
                    )
            continue

        if not texts:
            problems.append(f"scenario {i} has no texts and no bodies")
            continue

        for j, text in enumerate(texts, 1):
            if not str(text).strip():
                problems.append(
                    f"scenario {i}, text {j} is empty — if an empty submission is what "
                    f"you're testing, use 'bodies' instead of 'texts'"
                )
            elif str(text).startswith("REPLACE ME"):
                problems.append(
                    f"scenario {i} ('{scenario.get('name')}'), text {j} is still "
                    f"the placeholder"
                )
    return problems
