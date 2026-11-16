#!/usr/bin/env python3
"""
Run criterion 4 (the appeal path) three times.  <- UNIT 8, MILESTONE 3

    python app.py                                  # in one terminal
    python run_appeal_eval.py --label before       # in another
    python run_appeal_eval.py --label after

criteria.md's criterion 4 is: for 10 out of 10 valid appeals (a real
content_id from a prior submission, with reasoning text), the audit log
shows a status: "under_review" entry for that content_id, and POST /appeal
never returns a 5xx.

That needs a submit-then-appeal round trip, which doesn't fit scenarios.py's
shape (one request per entry) — scenarios.py's own docstring says to test a
criterion like this by hand or with a separate script. This is that script.

Each round trip submits under its own creator_id so ten appeals in one trial
don't trip the rate limiter against each other — that would be testing rate
limiting, not the appeal path.
"""

import argparse
import datetime as dt
import sys

import config

DEFAULT_URL = f"http://{config.HOST}:{config.PORT}"
TEXT = (
    "This is a submission made only to test the appeal path. The content "
    "itself doesn't matter for this criterion — only whether the appeal "
    "changes status and gets recorded."
)


def run_trial(url, trial, timeout):
    import requests

    results = []
    for i in range(1, 11):
        creator_id = f"appeal_eval_t{trial}_{i}"
        row = {"i": i, "creator_id": creator_id}
        try:
            submit_resp = requests.post(
                f"{url}/submit",
                json={"text": TEXT, "creator_id": creator_id},
                timeout=timeout,
            )
        except Exception as exc:  # noqa: BLE001
            row.update(ok=False, stage="submit", error=f"{type(exc).__name__}: {exc}")
            results.append(row)
            continue

        if submit_resp.status_code >= 500:
            row.update(ok=False, stage="submit", status=submit_resp.status_code,
                       error="5xx on submit")
            results.append(row)
            continue

        content_id = (submit_resp.json() or {}).get("content_id")
        if not content_id:
            row.update(ok=False, stage="submit", status=submit_resp.status_code,
                       error="no content_id in submit response")
            results.append(row)
            continue

        try:
            appeal_resp = requests.post(
                f"{url}/appeal",
                json={"content_id": content_id, "reasoning": "testing the appeal path"},
                timeout=timeout,
            )
        except Exception as exc:  # noqa: BLE001
            row.update(ok=False, stage="appeal", content_id=content_id,
                       error=f"{type(exc).__name__}: {exc}")
            results.append(row)
            continue

        row["appeal_status"] = appeal_resp.status_code
        row["content_id"] = content_id
        if appeal_resp.status_code >= 500:
            row.update(ok=False, stage="appeal", error="5xx on appeal")
            results.append(row)
            continue

        try:
            log_resp = requests.get(f"{url}/log?limit=200", timeout=timeout)
            entries = log_resp.json().get("entries", [])
        except Exception as exc:  # noqa: BLE001
            row.update(ok=False, stage="log_check", error=f"{type(exc).__name__}: {exc}")
            results.append(row)
            continue

        under_review = any(
            e.get("content_id") == content_id and e.get("status") == "under_review"
            for e in entries
        )
        row["ok"] = bool(under_review) and appeal_resp.status_code < 300
        if not row["ok"]:
            row["stage"] = "log_check"
            row["error"] = "no under_review entry found for this content_id"
        results.append(row)

    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--label", default="")
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--timeout", type=float, default=90.0)
    args = parser.parse_args()

    try:
        import requests  # noqa: F401
    except ImportError:
        print("The `requests` package isn't installed.\n"
              "Run: pip install -r requirements.txt", file=sys.stderr)
        sys.exit(1)

    try:
        import requests as _r
        _r.get(f"{args.url}/health", timeout=5)
    except Exception:  # noqa: BLE001
        print(f"Nothing answering at {args.url}. Start it:  python app.py",
              file=sys.stderr)
        sys.exit(1)

    all_trials = []
    for trial in range(1, args.trials + 1):
        results = run_trial(args.url, trial, args.timeout)
        ok_count = sum(1 for r in results if r.get("ok"))
        print(f"trial {trial}: {ok_count}/10 appeals changed status and logged correctly")
        all_trials.append(results)

    write_report(all_trials, args)


def write_report(all_trials, args):
    config.RESULTS_DIR.mkdir(exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y-%m-%d_%H%M")
    label = f"_{args.label}" if args.label else ""
    path = config.RESULTS_DIR / f"appeal_eval_{stamp}{label}.md"

    n = len(all_trials)
    counts = [sum(1 for r in trial if r.get("ok")) for trial in all_trials]
    verdict = "MET" if all(c == 10 for c in counts) else "MISSED"

    lines = [
        f"# Appeal path eval{f' — {args.label}' if args.label else ''}",
        "",
        "- Produced by: `run_appeal_eval.py::main`",
        "- Criterion 4: every valid appeal changes status to under_review and is logged;",
        "  target is 10/10, held across all 3 trials.",
        f"- {n} trials · {dt.datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "| Criterion | Target | " + " | ".join(f"Run {i}" for i in range(1, n + 1)) + " | Verdict |",
        "|---|---|" + "|".join(["---"] * n) + "|---|",
        "| 4. appeal always changes status and logs | 10 of 10 | "
        + " | ".join(f"{c}/10" for c in counts) + f" | {verdict} |",
        "",
        "---",
        "",
        "## What actually came back",
        "",
    ]

    for trial_number, results in enumerate(all_trials, 1):
        lines += [f"**Trial {trial_number}**", "", "```json"]
        import json
        lines.append(json.dumps(results, indent=2))
        lines += ["```", ""]

    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nWrote {path.relative_to(config.ROOT)}")
    print(f"Verdict: {verdict}")


if __name__ == "__main__":
    main()
