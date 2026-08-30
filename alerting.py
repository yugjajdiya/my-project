"""E1: configurable threshold evaluation and timestamped alert logging."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from config import MonitorConfig
from traffic_monitor import TrafficReading
from latency_monitor import LatencyResult


@dataclass
class Alert:
    timestamp: str
    message: str


class AlertManager:
    def __init__(self, config: MonitorConfig, log_path: Path):
        self.config, self.log_path = config, log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def check(self, traffic: TrafficReading | None, latency: list[LatencyResult]) -> list[Alert]:
        alerts: list[Alert] = []
        if traffic:
            if traffic.download_mbps > self.config.download_limit_mbps: alerts.append(self._new(f"Download {traffic.download_mbps:.2f} Mbps exceeds {self.config.download_limit_mbps:.2f} Mbps"))
            if traffic.upload_mbps > self.config.upload_limit_mbps: alerts.append(self._new(f"Upload {traffic.upload_mbps:.2f} Mbps exceeds {self.config.upload_limit_mbps:.2f} Mbps"))
        for item in latency:
            if item.average_ms is not None and item.average_ms > self.config.rtt_limit_ms: alerts.append(self._new(f"{item.name} RTT {item.average_ms:.1f} ms exceeds {self.config.rtt_limit_ms:.1f} ms"))
            if item.loss_percent > self.config.packet_loss_limit_percent: alerts.append(self._new(f"{item.name} packet loss {item.loss_percent:.1f}% exceeds {self.config.packet_loss_limit_percent:.1f}%"))
        for alert in alerts:
            with self.log_path.open("a", encoding="utf-8") as file: file.write(f"{alert.timestamp} | {alert.message}\n")
        return alerts

    @staticmethod
    def _new(message: str) -> Alert:
        return Alert(datetime.now().astimezone().isoformat(timespec="seconds"), message)
