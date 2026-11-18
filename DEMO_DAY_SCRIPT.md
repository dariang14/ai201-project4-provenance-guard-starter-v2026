# Demo Day — standup script

Read this almost verbatim, or use it as a safety net if you blank. You have
**3 minutes**. Four beats, matching the slide's prompts.

---

## 1. What I built (~45 sec)

> "I built Provenance Guard — a service that reads a piece of text and
> tells you how confident it is that the text was written by a person or by
> an AI. It runs two independent checks on the text — one runs a small
> language model and asks 'how predictable is this writing,' the other
> measures things like sentence length and vocabulary variety — and
> combines them into one score with three possible answers: human, unsure,
> or AI.
>
> For this final unit, I extended it so it runs the way a real service
> would: through a production server instead of a dev one, with every
> request timed and logged, so I can say exactly how fast it is and what it
> costs to run. Here it is answering a request." *(run the curl command
> from the README's Sample Run section, or just show `/health` responding)*

## 2. What standard I set (~30 sec)

> "My criterion is: the first request after the server restarts should
> answer in under 5 seconds. I wrote it before I ran anything, because I'd
> just switched from a dev server to a real one and didn't know yet whether
> that would behave differently.
>
> I set the bar at 5 seconds because that's generous for a real user, but
> anything close to it would already be a bad experience — and it turned
> out to matter a lot more than I expected."

## 3. What the test found (~45 sec)

> "I ran it 3 times, and on the numbers alone it passed all 3 — 3.4, 3.5,
> and 3.5 seconds. But before I had that formal test, I'd already found the
> real problem by hand: on one actual run, loading the model took 64
> seconds — and gunicorn, the real server, killed the connection after 30
> seconds because it assumed something had frozen. That's not a slow
> answer, that's a dropped one.
>
> The cause was in the server's worker lifecycle: the model was loading
> *inside* the first user's request instead of before the server started
> accepting traffic at all. My run log shows the three clean trials, but I
> reported the asterisk anyway, because those three numbers happened to run
> on a warm disk cache and don't prove the 64-second case can't happen
> again."

## 4. What I changed (~45 sec)

> "I changed when the model loads — now it loads once, right when the
> server starts, before it accepts any real traffic, instead of on
> whichever request happens to arrive first.
>
> It helped a lot: the first real request went from 3.5 seconds down to
> about 70-80 milliseconds — around 45 times faster — and it also means the
> worst case I found by hand, the 64-second one, can't happen to a real
> user anymore, because the slow part now happens before anyone's waiting
> on it.
>
> What's still broken: I don't have a reliable way to force that
> worst-case slowdown on demand, so I can't say with total confidence it's
> gone for good — only that the design no longer lets it reach a real
> request. If I had more time, that's the one thing I'd build next: a way
> to deliberately recreate heavy load and confirm the fix holds up under
> it, not just in a clean test."

---

## If someone asks a follow-up you don't expect

You don't have to know everything. True, safe answers:

- **"What does 'preload' actually do?"** → "It just moves one slow step —
  loading the model into memory — from 'whenever the first user shows up'
  to 'right when the server turns on.' Same work, different timing."
- **"Why didn't the 3 trials show the 64-second case?"** → "Because I ran
  them right after lots of other testing, so the files the model needs
  were still cached by the operating system. A truly fresh machine
  wouldn't have that head start."
- **"What does this cost to run?"** → "Nothing in dollars — it's a model
  that runs on the machine itself, not a paid API. The real cost is
  compute time, and it's small: about 40-60 milliseconds per request."
- **Anything else you genuinely don't know:** → "That's a good question, I
  don't have a confident answer — I'd want to check the code before I
  said something wrong." (This is a completely fine answer. Saying it
  calmly is better than guessing.)
