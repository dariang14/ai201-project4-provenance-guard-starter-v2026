"""
Structured request logging. — UNIT 9

Distinct from `audit.py`: `audit.jsonl` records *decisions* — a submission's
label, once one was reached. This records an *operational* fact about every
request regardless of what it was: a timestamp, what came in, what came out,
how long it took, and what it cost — including requests that errored, were
rejected by input validation, or were rate-limited. Wired in once, in
`app.py`, via Flask's `before_request`/`after_request` hooks, so it covers
every route automatically rather than needing a call added to each one.

    from instrumentation import log_request, read_entries

Cost here is compute time, not a per-call dollar price — the detector runs
locally, so there's no paid API to meter. `cost_usd` stays 0.0 throughout;
`duration_ms` is the real per-run cost this project has.
"""

import json
import threading
from datetime import datetime, timezone

import config

_lock = threading.Lock()

REQUESTS_LOG = config.LOG_DIR / "requests.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def log_request(
    *,
    method: str,
    path: str,
    status: int,
    duration_ms: float,
    request_summary,
    response_summary,
    cost_usd: float = 0.0,
) -> dict:
    """Write one structured log entry for a single request."""
    entry = {
        "timestamp": _now(),
        "method": method,
        "path": path,
        "status": status,
        "duration_ms": round(duration_ms, 2),
        "request_summary": request_summary,
        "response_summary": response_summary,
        "cost_usd": cost_usd,
    }
    line = json.dumps(entry, ensure_ascii=False)
    config.LOG_DIR.mkdir(parents=True, exist_ok=True)
    with _lock:
        with REQUESTS_LOG.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    return entry


def read_entries(limit: int | None = None) -> list[dict]:
    """Read the structured log back, oldest first. `limit` keeps the most recent N."""
    if not REQUESTS_LOG.exists():
        return []

    entries = []
    for line in REQUESTS_LOG.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue

    return entries[-limit:] if limit else entries
