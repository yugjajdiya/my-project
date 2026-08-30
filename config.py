"""Central configuration and user-editable safe defaults."""
from dataclasses import dataclass


@dataclass(frozen=True)
class MonitorConfig:
    sample_seconds: float = 2.0
    latency_window: int = 10
    ping_timeout_seconds: int = 2
    packet_capture_seconds: int = 10
    packet_capture_count: int = 250
    download_limit_mbps: float = 20.0
    upload_limit_mbps: float = 10.0
    rtt_limit_ms: float = 250.0
    packet_loss_limit_percent: float = 25.0
    public_dns: str = "1.1.1.1"
    website: str = "example.com"


DEFAULT_CONFIG = MonitorConfig()
