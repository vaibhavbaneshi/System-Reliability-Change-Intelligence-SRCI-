import time

try:
    from prometheus_client import Counter, Gauge, Histogram
except ImportError:
    Counter = Gauge = Histogram = None

_metrics_initialized = False
rca_runs_total = None
rca_duration_seconds = None
unprocessed_incidents_gauge = None
rca_escalations_total = None
rca_active_workers_gauge = None


def _init_metrics():
    global _metrics_initialized
    global rca_runs_total, rca_duration_seconds, unprocessed_incidents_gauge
    global rca_escalations_total, rca_active_workers_gauge

    if _metrics_initialized or Counter is None:
        _metrics_initialized = True
        return

    rca_runs_total = Counter(
        "srci_rca_runs_total",
        "Total RCA pipeline runs",
        ["status"],
    )
    rca_duration_seconds = Histogram(
        "srci_rca_duration_seconds",
        "RCA pipeline duration in seconds",
        buckets=(0.5, 1, 2, 5, 10, 30, 60),
    )
    unprocessed_incidents_gauge = Gauge(
        "srci_unprocessed_incidents",
        "Incidents awaiting autonomous RCA",
    )
    rca_escalations_total = Counter(
        "srci_rca_escalations_total",
        "RCA results flagged for human review",
    )
    rca_active_workers_gauge = Gauge(
        "srci_rca_active_workers",
        "Currently running RCA worker tasks",
    )
    _metrics_initialized = True


def record_rca_run(status: str, duration_sec: float):
    _init_metrics()
    if rca_runs_total is not None:
        rca_runs_total.labels(status=status).inc()
    if rca_duration_seconds is not None:
        rca_duration_seconds.observe(duration_sec)


def record_escalation():
    _init_metrics()
    if rca_escalations_total is not None:
        rca_escalations_total.inc()


def set_unprocessed_count(count: int):
    _init_metrics()
    if unprocessed_incidents_gauge is not None:
        unprocessed_incidents_gauge.set(count)


def set_active_workers(count: int):
    _init_metrics()
    if rca_active_workers_gauge is not None:
        rca_active_workers_gauge.set(count)


class RcaTimer:
    def __enter__(self):
        self._start = time.monotonic()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.duration_sec = time.monotonic() - self._start
        status = "failed" if exc_type else "completed"
        record_rca_run(status, self.duration_sec)
