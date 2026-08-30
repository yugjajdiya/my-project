"""C3: configurable reachability, RTT, jitter, and packet-loss statistics."""
from __future__ import annotations
from collections import deque
from dataclasses import dataclass
import re
import subprocess
import time


@dataclass
class LatencyResult:
    name: str
    target: str
    minimum_ms: float | None
    average_ms: float | None
    maximum_ms: float | None
    jitter_ms: float | None
    loss_percent: float
    status: str


class LatencyMonitor:
    def __init__(self, targets: dict[str, str], window: int = 10, timeout_seconds: int = 2):
        self.targets, self.timeout_seconds = targets, timeout_seconds
        self.samples = {name: deque(maxlen=window) for name in targets}

    def _ping(self, target: str) -> float | None:
        """Ping once using Windows ping and return measured RTT in ms when available."""
        try:
            started = time.perf_counter()
            completed = subprocess.run(["ping", "-n", "1", "-w", str(self.timeout_seconds * 1000), target],
                                       capture_output=True, text=True, timeout=self.timeout_seconds + 3)
            match = re.search(r"(?:time[=<])\s*(\d+(?:\.\d+)?)\s*ms", completed.stdout, re.IGNORECASE)
            if completed.returncode == 0:
                return float(match.group(1)) if match else (time.perf_counter() - started) * 1000
        except (OSError, subprocess.SubprocessError):
            pass
        return None

    def probe_all(self) -> list[LatencyResult]:
        results = []
        for name, target in self.targets.items():
            sample = self._ping(target)
            values = self.samples[name]
            values.append(sample)
            successful = [value for value in values if value is not None]
            loss = 100 * (len(values) - len(successful)) / len(values)
            jitter = (sum(abs(successful[index] - successful[index - 1]) for index in range(1, len(successful))) /
                      (len(successful) - 1)) if len(successful) > 1 else 0.0
            results.append(LatencyResult(name, target, min(successful) if successful else None,
                sum(successful) / len(successful) if successful else None, max(successful) if successful else None,
                jitter, loss, "UP" if sample is not None else "DOWN"))
        return results
