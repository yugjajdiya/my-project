"""Rich auto-refreshing dashboard that integrates C1, C3, E1 and E3."""
from __future__ import annotations
from datetime import datetime
import socket
import time
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from alerting import AlertManager
from history import HistoryStore
from latency_monitor import LatencyMonitor
from traffic_monitor import TrafficMonitor


def render(info, traffic, latency, alerts):
    layout = Layout(); layout.split_column(Layout(name="header", size=4), Layout(name="body"), Layout(name="alerts", size=5))
    layout["header"].update(Panel(f"[bold]NETWORK MONITOR[/bold]  Host: {socket.gethostname()}  IP: {info.ipv4}/{info.network.prefixlen}  Time: {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')}", title="Computer Networks PBL Activity 1"))
    body = Table(title=f"Interface: {info.name} | Gateway: {info.gateway or 'Not detected'}", expand=True)
    body.add_column("Traffic / Target"); body.add_column("Download / Average RTT"); body.add_column("Upload / Min-Max"); body.add_column("Loss / Jitter"); body.add_column("Status")
    if traffic: body.add_row("Traffic", f"{traffic.download_mbps:.3f} Mbps", f"{traffic.upload_mbps:.3f} Mbps", f"Rx {traffic.packets_received} / Tx {traffic.packets_sent}", "LIVE")
    else: body.add_row("Traffic", "Sampling baseline…", "", "", "WAIT")
    for item in latency:
        body.add_row(item.name, "—" if item.average_ms is None else f"{item.average_ms:.1f} ms", "—" if item.minimum_ms is None else f"{item.minimum_ms:.1f}–{item.maximum_ms:.1f} ms", f"{item.loss_percent:.0f}% / {item.jitter_ms:.1f} ms", f"[green]{item.status}[/green]" if item.status == "UP" else f"[red]{item.status}[/red]")
    layout["body"].update(body)
    message = "\n".join(f"[yellow]{alert.timestamp}: {alert.message}[/yellow]" for alert in alerts[-3:]) or "[green]No current threshold breaches.[/green]"
    layout["alerts"].update(Panel(message, title="E1 Alerts")); return layout


def run_dashboard(info, config, duration: int | None, data_dir) -> None:
    monitor = TrafficMonitor(info.name)
    targets = {"Gateway": info.gateway, "Public DNS": config.public_dns, "Website": config.website}
    latency = LatencyMonitor({key: value for key, value in targets.items() if value}, config.latency_window, config.ping_timeout_seconds)
    alert_manager = AlertManager(config, data_dir.parent / "logs" / "alerts.log"); history = HistoryStore(data_dir / "history.sqlite3")
    alerts = []; started = time.monotonic()
    with Live(console=Console(), refresh_per_second=4) as live:
        while duration is None or time.monotonic() - started < duration:
            traffic = monitor.sample(); results = latency.probe_all()
            alerts.extend(alert_manager.check(traffic, results))
            if traffic:
                gateway = next((item.average_ms for item in results if item.name == "Gateway"), None); history.save(traffic.download_mbps, traffic.upload_mbps, gateway)
            live.update(render(info, traffic, results, alerts)); time.sleep(config.sample_seconds)
