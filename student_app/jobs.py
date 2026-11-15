"""Slow copilot calls run here, one at a time (the language model has one slot).

The phone gets a ticket at once, and asks for the result every second.
"""

from concurrent.futures import ThreadPoolExecutor
import secrets
import threading


class Jobs:
    def __init__(self, keep: int = 200):
        self._pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="copilot")
        self._futures: dict = {}
        self._lock = threading.Lock()
        self._keep = keep

    def submit(self, fn, *args, **kwargs) -> str:
        ticket = secrets.token_hex(8)
        future = self._pool.submit(fn, *args, **kwargs)
        with self._lock:
            self._futures[ticket] = future
            while len(self._futures) > self._keep:
                self._futures.pop(next(iter(self._futures)))
        return ticket

    def get(self, ticket: str) -> dict:
        with self._lock:
            future = self._futures.get(ticket)
        if future is None:
            return {"status": "unknown"}
        if not future.done():
            return {"status": "pending"}
        error = future.exception()
        if error is not None:
            return {"status": "error", "error": f"{type(error).__name__}: {error}"}
        return {"status": "done", "result": future.result()}

    def shutdown(self):
        self._pool.shutdown(wait=False, cancel_futures=True)
