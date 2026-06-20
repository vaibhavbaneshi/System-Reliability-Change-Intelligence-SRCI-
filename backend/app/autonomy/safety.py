import time
from functools import wraps

MAX_RETRIES = 3
RETRY_BASE_DELAY_SEC = 0.5
CIRCUIT_FAILURE_THRESHOLD = 5
CIRCUIT_COOLDOWN_SEC = 30.0


class CircuitBreaker:
    """Simple in-process circuit breaker for RCA runner failures."""

    def __init__(self):
        self._failure_count = 0
        self._opened_at = None

    def is_open(self) -> bool:
        if self._opened_at is None:
            return False
        if (time.monotonic() - self._opened_at) >= CIRCUIT_COOLDOWN_SEC:
            self.reset()
            return False
        return True

    def record_success(self):
        self.reset()

    def record_failure(self):
        self._failure_count += 1
        if self._failure_count >= CIRCUIT_FAILURE_THRESHOLD:
            self._opened_at = time.monotonic()

    def reset(self):
        self._failure_count = 0
        self._opened_at = None


rca_circuit_breaker = CircuitBreaker()


def with_retry(func, *args, **kwargs):
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            last_error = exc
            if attempt == MAX_RETRIES - 1:
                raise
            time.sleep(RETRY_BASE_DELAY_SEC * (attempt + 1))
    raise last_error
