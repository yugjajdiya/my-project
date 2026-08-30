"""C1: counter sampling and derived interface throughput."""
from __future__ import annotations
from dataclasses import dataclass
import time
import psutil


@dataclass
class TrafficReading:
    interface: str
    download_mbps: float
    upload_mbps: float
    packets_received: int
    packets_sent: int
    elapsed_seconds: float


class TrafficMonitor:
    def __init__(self, interface: str):
        self.interface = interface
        self._previous = None

    def sample(self) -> TrafficReading | None:
        """Return rates from successive counter samples; first call establishes baseline."""
        counters = psutil.net_io_counters(pernic=True).get(self.interface)
        if counters is None:
            raise ValueError(f"Interface '{self.interface}' is unavailable or down.")
        now = time.monotonic()
        current = (now, counters)
        if self._previous is None:
            self._previous = current
            return None
        before_time, before = self._previous
        elapsed = now - before_time
        self._previous = current
        if elapsed <= 0:
            return None
        return TrafficReading(self.interface, (counters.bytes_recv - before.bytes_recv) * 8 / elapsed / 1_000_000,
                              (counters.bytes_sent - before.bytes_sent) * 8 / elapsed / 1_000_000,
                              counters.packets_recv, counters.packets_sent, elapsed)
