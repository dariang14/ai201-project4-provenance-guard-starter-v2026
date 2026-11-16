# Attack run — after

- Produced by: `run_attacks.py::main`
- Service: `app.py::submit`
- 56 attacks · 2026-11-16 04:05
- Auto-marked BROKE (5xx, crash, no response): **0**
- Left for you to judge: **56**

The Verdict column is blank where a script can't honestly decide. Whether
an evasion worked depends on where you put your thresholds — read the
`targets` column, look at what came back, and write HELD or BROKE yourself.

Each attack submits as creator_id `attacker_<id>`, and the content_id it
came back with is in the table — either one will match this run against your
audit log when you go looking for the ten entries to paste.

| ID | Family | Targeting | Status | Content ID | Guess | Score | Verdict |
|---|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | `658b7b96-0c01-448e-9fb9-d24b4f8d76d1` | human | 0.303 | BROKE |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | `b4c1b4b4-58ec-458e-9cfc-598d892196ae` | unsure | 0.502 | HELD |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | `a8c1cd89-a423-473d-b944-32cabbb97340` | unsure | 0.589 | HELD |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | `14685c4a-f6ea-4121-93b8-b25685a11a65` | unsure | 0.617 | HELD |
| EV05 | evasion | both signals: heavy human editing pass | 200 | `88119737-1096-4ed3-9069-2e646fe18789` | unsure | 0.400 | HELD |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | `ff3bc9e9-d791-4edf-8937-63d0af118ad9` | unsure | 0.544 | HELD |
| EV07 | evasion | signal two: padding with punctuation | 200 | `6d80dcd4-5294-4aae-8710-0f54f8028525` | unsure | 0.509 | HELD |
| EV08 | evasion | signal one: text below the token window | 200 | `be0cff25-11f9-4ff0-9baf-0ff3d3273754` | unsure | 0.396 | HELD |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | `93c87b72-8254-4da0-9f24-823f9336e1d4` | unsure | 0.630 | HELD |
| EV10 | evasion | signal two: repeated stanza structure | 200 | `fbf7b675-262e-4a83-9219-73bf1742165e` | ai | 0.863 | HELD |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | `2f7b135b-e7d7-4605-b16e-e09de3f2ac16` | unsure | 0.611 | HELD |
| FP02 | false_positive | human writing in a formal register | 200 | `c9a9ac93-2a03-4744-bfcc-b2ea80416b84` | ai | 0.697 | BROKE |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | `c47af222-a3cf-4a61-a523-a2346edce884` | ai | 0.716 | BROKE |
| FP04 | false_positive | a student essay written to a rubric | 200 | `16c5a0f1-4d8a-433e-aaed-b4431df02a24` | ai | 0.711 | BROKE |
| FP05 | false_positive | technical documentation written by a person | 200 | `a242a235-8e2d-47ec-ad79-fb3ea5432316` | ai | 0.743 | BROKE |
| FP06 | false_positive | a person imitating a formal template | 200 | `2981252f-a3c4-47bf-9917-c6d464d9877c` | ai | 0.733 | BROKE |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | `e2796eb8-00ad-4520-a446-6999eaaba932` | ai | 0.766 | BROKE |
| FP08 | false_positive | very short genuine human submission | 200 | `b53e58a2-6d74-44f5-b1ea-de1332c763d7` | unsure | 0.417 | HELD |
| PI01 | prompt_injection | instruction to ignore the check | 200 | `2035bd67-532b-4c2c-a64d-6386fcfd1ab3` | unsure | 0.481 | HELD |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | `d29fa57d-a2db-4450-a3de-f8820ca226fa` | human | 0.307 | HELD |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | `b78238e0-52f2-45bd-b2a6-41b9194fd879` | unsure | 0.522 | HELD |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | `03c0e3b4-453f-4a49-8c09-9243f8e0462a` | unsure | 0.532 | HELD |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | `a62797cc-3835-4ae5-8668-91aac3b52455` | unsure | 0.453 | HELD |
| PI06 | prompt_injection | instruction plus real human text | 200 | `2517a7fe-98d8-4e82-b756-8fa8df2ba75e` | unsure | 0.583 | HELD |
| MF01 | malformed | text is only whitespace | 400 | `—` | — | — | HELD |
| MF02 | malformed | text is a single character | 400 | `—` | — | — | HELD |
| MF03 | malformed | text is control characters | 200 | `40049c89-da8a-486f-96f9-a93d886f96b5` | human | 0.200 | HELD |
| MF04 | malformed | text is only punctuation | 200 | `88d26fb7-6838-448d-8be0-ee4192363e2a` | human | 0.158 | HELD |
| MF05 | malformed | text is a very long single word | 200 | `77d910f8-efe9-44d4-823f-a6fc5ded26e7` | ai | 0.832 | HELD |
| MF06 | malformed | text is emoji only | 200 | `d079f460-959d-48f4-98f3-df63bd82966f` | unsure | 0.649 | HELD |
| MF07 | malformed | text is right-to-left script | 200 | `af8fa997-fea0-4970-848d-e59fc2714b1d` | unsure | 0.622 | HELD |
| MF08 | malformed | text is 60,000 characters | 400 | `—` | — | — | HELD |
| RQ01 | malformed | no text field at all | 400 | `—` | — | — | HELD |
| RQ02 | malformed | no creator_id | 200 | `c157b13c-e182-4d60-a391-ddc548028ade` | unsure | 0.368 | HELD |
| RQ03 | malformed | text is a number | 400 | `—` | — | — | HELD |
| RQ04 | malformed | text is a list | 400 | `—` | — | — | HELD |
| RQ05 | malformed | text is null | 400 | `—` | — | — | HELD |
| RQ06 | malformed | creator_id is an object | 400 | `—` | — | — | HELD |
| RQ07 | malformed | body is a JSON array, not an object | 400 | `—` | — | — | HELD |
| RQ08 | malformed | body is unparseable JSON | 400 | `—` | — | — | HELD |
| RQ09 | malformed | body is empty | 400 | `—` | — | — | HELD |
| RQ10 | malformed | body is form-encoded, not JSON | 429 | `—` | — | — | HELD |
| RQ11 | malformed | body is JSON claiming to be plain text | 429 | `—` | — | — | HELD |
| RQ12 | malformed | deeply nested JSON | 400 | `—` | — | — | HELD |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | `f2a09404-e5ef-4e38-8a6e-190414876545` | human | 0.220 | HELD |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | `9521cad1-6fdf-4bdb-a4f7-0ddb9a0217e2` | human | 0.220 | HELD |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | `153ab2f1-79f1-405b-98f9-2fd2ef6e96bc` | human | 0.220 | HELD |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | `5f1d72f7-8d37-4219-99d8-aa629979bf6c` | human | 0.220 | HELD |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | `aadbf033-5bfd-4290-93fe-70731535123e` | human | 0.220 | HELD |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |

---

## By family

| Family | Attacks | Auto-BROKE | Left to judge |
|---|---|---|---|
| `evasion` | 10 | 0 | 10 |
| `false_positive` | 8 | 0 | 8 |
| `flood_same_creator` | 12 | 0 | 12 |
| `malformed` | 20 | 0 | 20 |
| `prompt_injection` | 6 | 0 | 6 |

> The **false_positive** family is the one to look at hardest. Those are
> written to be genuine human writing that reads as machine-like. Every one
> your service calls AI is a real writer it would have accused.

---

## What came back

The detail behind the table. Paste the interesting failures into your
README — the ones that show something, not the ten easiest.

### EV01 — `evasion`

*Targeting:* signal two: typos raise word variety

```json
{
  "id": "EV01",
  "status": 200,
  "content_id": "658b7b96-0c01-448e-9fb9-d24b4f8d76d1",
  "creator_id": "attacker_EV01",
  "guess": "human",
  "confidence": 0.30306,
  "model_score": 0.1635,
  "style_score": 0.6287,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### EV02 — `evasion`

*Targeting:* signal two: broken-up sentences raise length spread

```json
{
  "id": "EV02",
  "status": 200,
  "content_id": "b4c1b4b4-58ec-458e-9cfc-598d892196ae",
  "creator_id": "attacker_EV02",
  "guess": "unsure",
  "confidence": 0.5022500000000001,
  "model_score": 0.5943,
  "style_score": 0.4102,
  "label": "We can't tell with confidence whether this was written by a person or an AI system. This isn't an accusation \u2014 it means our signals didn't agree clearly either way. No action has been taken; you're welcome to appeal if you'd like a person to look at it.",
  "error": null,
  "verdict": ""
}
```

### EV03 — `evasion`

*Targeting:* signal two: a pasted quotation changes the shape

```json
{
  "id": "EV03",
  "status": 200,
  "content_id": "a8c1cd89-a423-473d-b944-32cabbb97340",
  "creator_id": "attacker_EV03",
  "guess": "unsure",
  "confidence": 0.5892,
  "model_score": 0.6662,
  "style_score": 0.5122,
  "label": "We can't tell with confidence whether this was written by a person or an AI system. This isn't an accusation \u2014 it means our signals didn't agree clearly either way. No action has been taken; you're welcome to appeal if you'd like a person to look at it.",
  "error": null,
  "verdict": ""
}
```

### EV04 — `evasion`

*Targeting:* signal one: unusual words raise perplexity

```json
{
  "id": "EV04",
  "status": 200,
  "content_id": "14685c4a-f6ea-4121-93b8-b25685a11a65",
  "creator_id": "attacker_EV04",
  "guess": "unsure",
  "confidence": 0.6173,
  "model_score": 0.6114,
  "style_score": 0.6232,
  "label": "We can't tell with confidence whether this was written by a person or an AI system. This isn't an accusation \u2014 it means our signals didn't agree clearly either way. No action has been taken; you're welcome to appeal if you'd like a person to look at it.",
  "error": null,
  "verdict": ""
}
```

### EV05 — `evasion`

*Targeting:* both signals: heavy human editing pass

```json
{
  "id": "EV05",
  "status": 200,
  "content_id": "88119737-1096-4ed3-9069-2e646fe18789",
  "creator_id": "attacker_EV05",
  "guess": "unsure",
  "confidence": 0.39975,
  "model_score": 0.3212,
  "style_score": 0.4783,
  "label": "We can't tell with confidence whether this was written by a person or an AI system. This isn't an accusation \u2014 it means our signals didn't agree clearly either way. No action has been taken; you're welcome to appeal if you'd like a person to look at it.",
  "error": null,
  "verdict": ""
}
```

### EV06 — `evasion`

*Targeting:* signal two: one very long sentence and one very short

```json
{
  "id": "EV06",
  "status": 200,
  "content_id": "ff3bc9e9-d791-4edf-8937-63d0af118ad9",
  "creator_id": "attacker_EV06",
  "guess": "unsure",
  "confidence": 0.5441,
  "model_score": 0.5727,
  "style_score": 0.5155,
  "label": "We can't tell with confidence whether this was written by a person or an AI system. This isn't an accusation \u2014 it means our signals didn't agree clearly either way. No action has been taken; you're welcome to appeal if you'd like a person to look at it.",
  "error": null,
  "verdict": ""
}
```

### EV07 — `evasion`

*Targeting:* signal two: padding with punctuation

```json
{
  "id": "EV07",
  "status": 200,
  "content_id": "6d80dcd4-5294-4aae-8710-0f54f8028525",
  "creator_id": "attacker_EV07",
  "guess": "unsure",
  "confidence": 0.5087,
  "model_score": 0.5862,
  "style_score": 0.4312,
  "label": "We can't tell with confidence whether this was written by a person or an AI system. This isn't an accusation \u2014 it means our signals didn't agree clearly either way. No action has been taken; you're welcome to appeal if you'd like a person to look at it.",
  "error": null,
  "verdict": ""
}
```

### EV08 — `evasion`

*Targeting:* signal one: text below the token window

```json
{
  "id": "EV08",
  "status": 200,
  "content_id": "be0cff25-11f9-4ff0-9baf-0ff3d3273754",
  "creator_id": "attacker_EV08",
  "guess": "unsure",
  "confidence": 0.3957,
  "model_score": 0.2452,
  "style_score": 0.5462,
  "label": "We can't tell with confidence whether this was written by a person or an AI system. This isn't an accusation \u2014 it means our signals didn't agree clearly either way. No action has been taken; you're welcome to appeal if you'd like a person to look at it.",
  "error": null,
  "verdict": ""
}
```

### EV09 — `evasion`

*Targeting:* both: AI text with a human opening paragraph bolted on

```json
{
  "id": "EV09",
  "status": 200,
  "content_id": "93c87b72-8254-4da0-9f24-823f9336e1d4",
  "creator_id": "attacker_EV09",
  "guess": "unsure",
  "confidence": 0.6304000000000001,
  "model_score": 0.7042,
  "style_score": 0.5566,
  "label": "We can't tell with confidence whether this was written by a person or an AI system. This isn't an accusation \u2014 it means our signals didn't agree clearly either way. No action has been taken; you're welcome to appeal if you'd like a person to look at it.",
  "error": null,
  "verdict": ""
}
```

### EV10 — `evasion`

*Targeting:* signal two: repeated stanza structure

```json
{
  "id": "EV10",
  "status": 200,
  "content_id": "fbf7b675-262e-4a83-9219-73bf1742165e",
  "creator_id": "attacker_EV10",
  "guess": "ai",
  "confidence": 0.8627499999999999,
  "model_score": 0.9792,
  "style_score": 0.7463,
  "label": "We think this was most likely written by an AI system. If that's wrong, you can appeal and a person will take a look.",
  "error": null,
  "verdict": ""
}
```

### FP01 — `false_positive`

*Targeting:* plain, clear human writing with no flourishes

```json
{
  "id": "FP01",
  "status": 200,
  "content_id": "2f7b135b-e7d7-4605-b16e-e09de3f2ac16",
  "creator_id": "attacker_FP01",
  "guess": "unsure",
  "confidence": 0.611,
  "model_score": 0.6175,
  "style_score": 0.6045,
  "label": "We can't tell with confidence whether this was written by a person or an AI system. This isn't an accusation \u2014 it means our signals didn't agree clearly either way. No action has been taken; you're welcome to appeal if you'd like a person to look at it.",
  "error": null,
  "verdict": ""
}
```

### FP02 — `false_positive`

*Targeting:* human writing in a formal register

```json
{
  "id": "FP02",
  "status": 200,
  "content_id": "c9a9ac93-2a03-4744-bfcc-b2ea80416b84",
  "creator_id": "attacker_FP02",
  "guess": "ai",
  "confidence": 0.6968000000000001,
  "model_score": 0.7387,
  "style_score": 0.6549,
  "label": "We think this was most likely written by an AI system. If that's wrong, you can appeal and a person will take a look.",
  "error": null,
  "verdict": ""
}
```

### FP03 — `false_positive`

*Targeting:* a non-native English speaker writing carefully

```json
{
  "id": "FP03",
  "status": 200,
  "content_id": "c47af222-a3cf-4a61-a523-a2346edce884",
  "creator_id": "attacker_FP03",
  "guess": "ai",
  "confidence": 0.716,
  "model_score": 0.8051,
  "style_score": 0.6269,
  "label": "We think this was most likely written by an AI system. If that's wrong, you can appeal and a person will take a look.",
  "error": null,
  "verdict": ""
}
```

### FP04 — `false_positive`

*Targeting:* a student essay written to a rubric

```json
{
  "id": "FP04",
  "status": 200,
  "content_id": "16c5a0f1-4d8a-433e-aaed-b4431df02a24",
  "creator_id": "attacker_FP04",
  "guess": "ai",
  "confidence": 0.71115,
  "model_score": 0.8329,
  "style_score": 0.5894,
  "label": "We think this was most likely written by an AI system. If that's wrong, you can appeal and a person will take a look.",
  "error": null,
  "verdict": ""
}
```

### FP05 — `false_positive`

*Targeting:* technical documentation written by a person

```json
{
  "id": "FP05",
  "status": 200,
  "content_id": "a242a235-8e2d-47ec-ad79-fb3ea5432316",
  "creator_id": "attacker_FP05",
  "guess": "ai",
  "confidence": 0.74325,
  "model_score": 0.8005,
  "style_score": 0.686,
  "label": "We think this was most likely written by an AI system. If that's wrong, you can appeal and a person will take a look.",
  "error": null,
  "verdict": ""
}
```

### FP06 — `false_positive`

*Targeting:* a person imitating a formal template

```json
{
  "id": "FP06",
  "status": 200,
  "content_id": "2981252f-a3c4-47bf-9917-c6d464d9877c",
  "creator_id": "attacker_FP06",
  "guess": "ai",
  "confidence": 0.7334,
  "model_score": 0.8814,
  "style_score": 0.5854,
  "label": "We think this was most likely written by an AI system. If that's wrong, you can appeal and a person will take a look.",
  "error": null,
  "verdict": ""
}
```

### FP07 — `false_positive`

*Targeting:* human writing that repeats a phrase deliberately

```json
{
  "id": "FP07",
  "status": 200,
  "content_id": "e2796eb8-00ad-4520-a446-6999eaaba932",
  "creator_id": "attacker_FP07",
  "guess": "ai",
  "confidence": 0.76555,
  "model_score": 0.8816,
  "style_score": 0.6495,
  "label": "We think this was most likely written by an AI system. If that's wrong, you can appeal and a person will take a look.",
  "error": null,
  "verdict": ""
}
```

### FP08 — `false_positive`

*Targeting:* very short genuine human submission

```json
{
  "id": "FP08",
  "status": 200,
  "content_id": "b53e58a2-6d74-44f5-b1ea-de1332c763d7",
  "creator_id": "attacker_FP08",
  "guess": "unsure",
  "confidence": 0.41715,
  "model_score": 0.3223,
  "style_score": 0.512,
  "label": "We can't tell with confidence whether this was written by a person or an AI system. This isn't an accusation \u2014 it means our signals didn't agree clearly either way. No action has been taken; you're welcome to appeal if you'd like a person to look at it.",
  "error": null,
  "verdict": ""
}
```

### PI01 — `prompt_injection`

*Targeting:* instruction to ignore the check

```json
{
  "id": "PI01",
  "status": 200,
  "content_id": "2035bd67-532b-4c2c-a64d-6386fcfd1ab3",
  "creator_id": "attacker_PI01",
  "guess": "unsure",
  "confidence": 0.4807,
  "model_score": 0.4625,
  "style_score": 0.4989,
  "label": "We can't tell with confidence whether this was written by a person or an AI system. This isn't an accusation \u2014 it means our signals didn't agree clearly either way. No action has been taken; you're welcome to appeal if you'd like a person to look at it.",
  "error": null,
  "verdict": ""
}
```

### PI02 — `prompt_injection`

*Targeting:* instruction disguised as a system message

```json
{
  "id": "PI02",
  "status": 200,
  "content_id": "d29fa57d-a2db-4450-a3de-f8820ca226fa",
  "creator_id": "attacker_PI02",
  "guess": "human",
  "confidence": 0.30695,
  "model_score": 0.2044,
  "style_score": 0.4095,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### PI03 — `prompt_injection`

*Targeting:* instruction wrapped in the writer's voice

```json
{
  "id": "PI03",
  "status": 200,
  "content_id": "b78238e0-52f2-45bd-b2a6-41b9194fd879",
  "creator_id": "attacker_PI03",
  "guess": "unsure",
  "confidence": 0.52225,
  "model_score": 0.5943,
  "style_score": 0.4502,
  "label": "We can't tell with confidence whether this was written by a person or an AI system. This isn't an accusation \u2014 it means our signals didn't agree clearly either way. No action has been taken; you're welcome to appeal if you'd like a person to look at it.",
  "error": null,
  "verdict": ""
}
```

### PI04 — `prompt_injection`

*Targeting:* attempt to make the label text hostile

```json
{
  "id": "PI04",
  "status": 200,
  "content_id": "03c0e3b4-453f-4a49-8c09-9243f8e0462a",
  "creator_id": "attacker_PI04",
  "guess": "unsure",
  "confidence": 0.5324,
  "model_score": 0.4998,
  "style_score": 0.565,
  "label": "We can't tell with confidence whether this was written by a person or an AI system. This isn't an accusation \u2014 it means our signals didn't agree clearly either way. No action has been taken; you're welcome to appeal if you'd like a person to look at it.",
  "error": null,
  "verdict": ""
}
```

### PI05 — `prompt_injection`

*Targeting:* attempt to inject into the audit log

```json
{
  "id": "PI05",
  "status": 200,
  "content_id": "a62797cc-3835-4ae5-8668-91aac3b52455",
  "creator_id": "attacker_PI05",
  "guess": "unsure",
  "confidence": 0.45305,
  "model_score": 0.6401,
  "style_score": 0.266,
  "label": "We can't tell with confidence whether this was written by a person or an AI system. This isn't an accusation \u2014 it means our signals didn't agree clearly either way. No action has been taken; you're welcome to appeal if you'd like a person to look at it.",
  "error": null,
  "verdict": ""
}
```

### PI06 — `prompt_injection`

*Targeting:* instruction plus real human text

```json
{
  "id": "PI06",
  "status": 200,
  "content_id": "2517a7fe-98d8-4e82-b756-8fa8df2ba75e",
  "creator_id": "attacker_PI06",
  "guess": "unsure",
  "confidence": 0.58265,
  "model_score": 0.5583,
  "style_score": 0.607,
  "label": "We can't tell with confidence whether this was written by a person or an AI system. This isn't an accusation \u2014 it means our signals didn't agree clearly either way. No action has been taken; you're welcome to appeal if you'd like a person to look at it.",
  "error": null,
  "verdict": ""
}
```

### MF01 — `malformed`

*Targeting:* text is only whitespace

```json
{
  "id": "MF01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF02 — `malformed`

*Targeting:* text is a single character

```json
{
  "id": "MF02",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF02",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF03 — `malformed`

*Targeting:* text is control characters

```json
{
  "id": "MF03",
  "status": 200,
  "content_id": "40049c89-da8a-486f-96f9-a93d886f96b5",
  "creator_id": "attacker_MF03",
  "guess": "human",
  "confidence": 0.20001000000000002,
  "model_score": 0.0,
  "style_score": 0.6667,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### MF04 — `malformed`

*Targeting:* text is only punctuation

```json
{
  "id": "MF04",
  "status": 200,
  "content_id": "88d26fb7-6838-448d-8be0-ee4192363e2a",
  "creator_id": "attacker_MF04",
  "guess": "human",
  "confidence": 0.15784000000000004,
  "model_score": 0.0112,
  "style_score": 0.5,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### MF05 — `malformed`

*Targeting:* text is a very long single word

```json
{
  "id": "MF05",
  "status": 200,
  "content_id": "77d910f8-efe9-44d4-823f-a6fc5ded26e7",
  "creator_id": "attacker_MF05",
  "guess": "ai",
  "confidence": 0.83215,
  "model_score": 0.9976,
  "style_score": 0.6667,
  "label": "We think this was most likely written by an AI system. If that's wrong, you can appeal and a person will take a look.",
  "error": null,
  "verdict": ""
}
```

### MF06 — `malformed`

*Targeting:* text is emoji only

```json
{
  "id": "MF06",
  "status": 200,
  "content_id": "d079f460-959d-48f4-98f3-df63bd82966f",
  "creator_id": "attacker_MF06",
  "guess": "unsure",
  "confidence": 0.64907,
  "model_score": 0.9969,
  "style_score": 0.5,
  "label": "We can't tell with confidence whether this was written by a person or an AI system. This isn't an accusation \u2014 it means our signals didn't agree clearly either way. No action has been taken; you're welcome to appeal if you'd like a person to look at it.",
  "error": null,
  "verdict": ""
}
```

### MF07 — `malformed`

*Targeting:* text is right-to-left script

```json
{
  "id": "MF07",
  "status": 200,
  "content_id": "af8fa997-fea0-4970-848d-e59fc2714b1d",
  "creator_id": "attacker_MF07",
  "guess": "unsure",
  "confidence": 0.62192,
  "model_score": 0.9064,
  "style_score": 0.5,
  "label": "We can't tell with confidence whether this was written by a person or an AI system. This isn't an accusation \u2014 it means our signals didn't agree clearly either way. No action has been taken; you're welcome to appeal if you'd like a person to look at it.",
  "error": null,
  "verdict": ""
}
```

### MF08 — `malformed`

*Targeting:* text is 60,000 characters

```json
{
  "id": "MF08",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF08",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ01 — `malformed`

*Targeting:* no text field at all

```json
{
  "id": "RQ01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ02 — `malformed`

*Targeting:* no creator_id

```json
{
  "id": "RQ02",
  "status": 200,
  "content_id": "c157b13c-e182-4d60-a391-ddc548028ade",
  "creator_id": null,
  "guess": "unsure",
  "confidence": 0.36766,
  "model_score": 0.2395,
  "style_score": 0.6667,
  "label": "We can't tell with confidence whether this was written by a person or an AI system. This isn't an accusation \u2014 it means our signals didn't agree clearly either way. No action has been taken; you're welcome to appeal if you'd like a person to look at it.",
  "error": null,
  "verdict": ""
}
```

### RQ03 — `malformed`

*Targeting:* text is a number

```json
{
  "id": "RQ03",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ03",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ04 — `malformed`

*Targeting:* text is a list

```json
{
  "id": "RQ04",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ04",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ05 — `malformed`

*Targeting:* text is null

```json
{
  "id": "RQ05",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ05",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ06 — `malformed`

*Targeting:* creator_id is an object

```json
{
  "id": "RQ06",
  "status": 400,
  "content_id": null,
  "creator_id": {
    "id": "x"
  },
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ07 — `malformed`

*Targeting:* body is a JSON array, not an object

```json
{
  "id": "RQ07",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ08 — `malformed`

*Targeting:* body is unparseable JSON

```json
{
  "id": "RQ08",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ09 — `malformed`

*Targeting:* body is empty

```json
{
  "id": "RQ09",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ10 — `malformed`

*Targeting:* body is form-encoded, not JSON

```json
{
  "id": "RQ10",
  "status": 429,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ11 — `malformed`

*Targeting:* body is JSON claiming to be plain text

```json
{
  "id": "RQ11",
  "status": 429,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ12 — `malformed`

*Targeting:* deeply nested JSON

```json
{
  "id": "RQ12",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ12",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_01 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_01",
  "status": 200,
  "content_id": "f2a09404-e5ef-4e38-8a6e-190414876545",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.22010000000000002,
  "model_score": 0.0287,
  "style_score": 0.6667,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_02 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_02",
  "status": 200,
  "content_id": "9521cad1-6fdf-4bdb-a4f7-0ddb9a0217e2",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.22010000000000002,
  "model_score": 0.0287,
  "style_score": 0.6667,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_03 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_03",
  "status": 200,
  "content_id": "153ab2f1-79f1-405b-98f9-2fd2ef6e96bc",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.22010000000000002,
  "model_score": 0.0287,
  "style_score": 0.6667,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_04 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_04",
  "status": 200,
  "content_id": "5f1d72f7-8d37-4219-99d8-aa629979bf6c",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.22010000000000002,
  "model_score": 0.0287,
  "style_score": 0.6667,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_05 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_05",
  "status": 200,
  "content_id": "aadbf033-5bfd-4290-93fe-70731535123e",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.22010000000000002,
  "model_score": 0.0287,
  "style_score": 0.6667,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_06 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_06",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_07 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_07",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_08 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_08",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_09 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_09",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_10 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_10",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_11 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_11",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_12 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_12",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```
