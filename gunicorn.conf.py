"""
Gunicorn config for Provenance Guard. — UNIT 9

Without PRELOAD_DETECTOR, the detector model loads on whichever request
happens to arrive first after a (re)start — which measured at ~64s on this
machine, comfortably past gunicorn's default 30s worker timeout. `post_fork`
runs in each worker right after it forks, before it accepts any connections,
so the slow load happens once at startup instead of on a real user's first
request.

AI201_PRELOAD_DETECTOR=0 disables preloading — used once, deliberately, to
capture the "before" measurement in results/; it isn't meant to be turned
off in normal use.
"""

import os

timeout = 120  # the cold load is slow; see What It Costs in README.md

PRELOAD_DETECTOR = os.getenv("AI201_PRELOAD_DETECTOR", "1") == "1"


def post_fork(server, worker):
    if not PRELOAD_DETECTOR:
        server.log.info("Worker %s: preload disabled (AI201_PRELOAD_DETECTOR=0).", worker.pid)
        return
    import detector

    server.log.info("Worker %s: loading detector model before accepting requests...", worker.pid)
    detector.warm_up()
    server.log.info("Worker %s: detector model loaded, ready for requests.", worker.pid)
