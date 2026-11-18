#!/usr/bin/env python3
"""
Run the five Unit 9 criteria, three trials each.

    python run_unit9_eval.py --label before   # preload disabled
    python run_unit9_eval.py --label after    # preload enabled (default)

Unlike run_eval.py (Unit 8), these criteria are about the *service*, not a
detection decision, so this script owns starting and stopping gunicorn
itself between trials where that matters (criterion 7 needs a fresh worker
each trial).
"""

import argparse
import datetime as dt
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import requests

import config

ROOT = Path(__file__).parent
URL = f"http://{config.HOST}:{config.PORT}"
ERR_LOG = ROOT / "logs" / "_gunicorn_eval_error.log"
ACC_LOG = ROOT / "logs" / "_gunicorn_eval_access.log"


def start_gunicorn(preload: bool):
    env = os.environ.copy()
    env["AI201_PRELOAD_DETECTOR"] = "1" if preload else "0"
    ERR_LOG.write_text("")
    proc = subprocess.Popen(
        ["gunicorn", "app:app", "--bind", f"{config.HOST}:{config.PORT}",
         "--workers", "1", "--config", "gunicorn.conf.py",
         "--access-logfile", str(ACC_LOG), "--error-logfile", str(ERR_LOG)],
        cwd=ROOT, env=env,
    )
    return proc


def stop_gunicorn(proc):
    proc.send_signal(signal.SIGTERM)
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()


def wait_for_ready(preload: bool, timeout=90):
    marker = "ready for requests" if preload else "preload disabled"
    deadline = time.time() + timeout
    while time.time() < deadline:
        if ERR_LOG.exists() and marker in ERR_LOG.read_text():
            return True
        time.sleep(0.5)
    return False


def submit(text, creator_id, timeout=90):
    t0 = time.perf_counter()
    try:
        r = requests.post(f"{URL}/submit", json={"text": text, "creator_id": creator_id}, timeout=timeout)
        wall_ms = (time.perf_counter() - t0) * 1000
        return r.status_code, wall_ms, (r.json() if r.content else {})
    except Exception as exc:  # noqa: BLE001
        return None, (time.perf_counter() - t0) * 1000, {"error": str(exc)}


WARM_TEXT = "A steady-state warm request used only to measure latency after the model is already loaded."


def criterion_6_warm_latency():
    """9 of 10 warm requests under 500ms."""
    for i in range(10):
        submit(WARM_TEXT, f"c6_{i}")
    # Use the server's own measured duration_ms (from instrumentation.py) rather
    # than client-side wall time, since that's what criterion 6 is actually about.
    entries = requests.get(f"{URL}/requests?limit=10").json()["entries"]
    server_ms = [e["duration_ms"] for e in entries if e["path"] == "/submit"][-10:]
    under = sum(1 for d in server_ms if d < 500)
    return {"under_500ms": under, "of": len(server_ms), "durations_ms": server_ms}


def criterion_8_log_completeness():
    """100% of a mixed batch of 6 requests (3 good, 3 bad) produce one complete entry each."""
    bodies = [
        {"text": "A perfectly normal submission for the log-completeness check.", "creator_id": "c8_good_1"},
        {"text": "Another normal one, different text entirely, for the same check.", "creator_id": "c8_good_2"},
        {"text": "A third normal submission to round out the good half of this batch.", "creator_id": "c8_good_3"},
        {"text": "", "creator_id": "c8_bad_empty"},
        {"creator_id": "c8_bad_missing"},
        {"text": "x", "creator_id": "c8_bad_short"},
    ]
    before_count = len(requests.get(f"{URL}/requests?limit=100000").json()["entries"])
    for body in bodies:
        requests.post(f"{URL}/submit", json=body, timeout=30)
    after = requests.get(f"{URL}/requests?limit=100000").json()["entries"]
    new_entries = after[before_count:]
    required = {"timestamp", "method", "path", "status", "duration_ms", "request_summary", "response_summary"}
    complete = sum(1 for e in new_entries if required.issubset(e.keys()))
    return {"sent": len(bodies), "logged": len(new_entries), "complete": complete}


def criterion_9_cost_bound():
    """Average duration_ms over 20 warm requests stays under 200ms."""
    for i in range(20):
        submit(WARM_TEXT, f"c9_{i}")
    entries = requests.get(f"{URL}/requests?limit=20").json()["entries"]
    server_ms = [e["duration_ms"] for e in entries if e["path"] == "/submit"][-20:]
    avg = sum(server_ms) / len(server_ms) if server_ms else None
    return {"avg_ms": round(avg, 2) if avg else None, "n": len(server_ms), "hundred_a_day_seconds": round((avg or 0) * 100 / 1000, 2)}


def criterion_10_regression():
    """Rate limiter still gives 5x200 then 10x429 on a 15-request flood."""
    codes = []
    flood_text = "This is an ordinary submission sent repeatedly to check the rate limiter still works."
    for i in range(15):
        status, _, _ = submit(flood_text, "c10_flood")
        codes.append(status)
    successes = sum(1 for c in codes if c == 200)
    limited = sum(1 for c in codes if c == 429)
    return {"codes": codes, "successes": successes, "limited": limited}


def run_trial(label, preload, trial_num, do_c7_and_c10):
    proc = start_gunicorn(preload)
    ready = wait_for_ready(preload)
    results = {}

    if do_c7_and_c10:
        t0 = time.perf_counter()
        status, wall_ms, body = submit("Measuring first-request latency after a fresh worker start, for criterion 7.", "c7_first")
        entries = requests.get(f"{URL}/requests?limit=1").json()["entries"]
        server_ms = entries[0]["duration_ms"] if entries else None
        results["c7_first_request"] = {"status": status, "server_ms": server_ms, "wall_ms": round(wall_ms, 2), "ready_detected": ready}

    results["c6_warm_latency"] = criterion_6_warm_latency()
    results["c8_log_completeness"] = criterion_8_log_completeness()
    results["c9_cost_bound"] = criterion_9_cost_bound()

    if do_c7_and_c10:
        results["c10_regression"] = criterion_10_regression()

    stop_gunicorn(proc)
    time.sleep(1)
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", default="")
    parser.add_argument("--preload", default="1")
    parser.add_argument("--trials", type=int, default=3)
    args = parser.parse_args()
    preload = args.preload == "1"

    all_trials = []
    for t in range(1, args.trials + 1):
        print(f"trial {t}/{args.trials} (preload={preload})...", file=sys.stderr)
        r = run_trial(args.label, preload, t, do_c7_and_c10=True)
        all_trials.append(r)
        print(json.dumps(r, indent=2), file=sys.stderr)

    config.RESULTS_DIR.mkdir(exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y-%m-%d_%H%M")
    label = f"_{args.label}" if args.label else ""
    path = config.RESULTS_DIR / f"unit9_eval_{stamp}{label}.md"
    path.write_text(f"# Unit 9 eval — {args.label or 'run'} (preload={preload})\n\n```json\n"
                     + json.dumps(all_trials, indent=2) + "\n```\n", encoding="utf-8")
    print(f"Wrote {path.relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()
