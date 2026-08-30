"""Computer Networks PBL: C1-C4 plus E1/E3 monitoring utility."""
from __future__ import annotations
import argparse
from pathlib import Path
import time
from config import DEFAULT_CONFIG
from dashboard import run_dashboard
from history import HistoryStore
from host_discovery import discover_hosts
from latency_monitor import LatencyMonitor
from network_info import get_interface_info, list_interfaces
from traffic_analyzer import capture_traffic
from traffic_monitor import TrafficMonitor

ROOT = Path(__file__).resolve().parent; DATA = ROOT / "data"; CHARTS = ROOT / "charts"

def parser():
    command = argparse.ArgumentParser(description="Safe local Network Monitoring Tool (C1-C4, E1, E3)")
    command.add_argument("--interface", help="Active interface name; otherwise detected at runtime")
    commands = command.add_subparsers(dest="command", required=True)
    dash = commands.add_parser("dashboard"); dash.add_argument("--duration", type=int, help="Optional seconds; omit for continuous display")
    traffic = commands.add_parser("traffic"); traffic.add_argument("--samples", type=int, default=5)
    commands.add_parser("interfaces")
    discover = commands.add_parser("discover"); discover.add_argument("--authorized-local-scan", action="store_true", help="Confirm you are authorised to scan this detected local subnet"); discover.add_argument("--max-hosts", type=int, default=254)
    commands.add_parser("latency")
    capture = commands.add_parser("capture"); capture.add_argument("--seconds", type=int, default=DEFAULT_CONFIG.packet_capture_seconds); capture.add_argument("--count", type=int, default=DEFAULT_CONFIG.packet_capture_count)
    commands.add_parser("chart")
    return command

def main():
    args = parser().parse_args()
    if args.command == "interfaces":
        print("\n".join(list_interfaces()) or "No active IPv4 interfaces found."); return
    try: info = get_interface_info(args.interface)
    except ValueError as error: print(f"Error: {error}"); return
    if args.command == "dashboard": run_dashboard(info, DEFAULT_CONFIG, args.duration, DATA)
    elif args.command == "traffic":
        monitor = TrafficMonitor(info.name); print(f"Sampling {info.name} every {DEFAULT_CONFIG.sample_seconds}s..."); monitor.sample()
        for _ in range(args.samples):
            time.sleep(DEFAULT_CONFIG.sample_seconds); print(monitor.sample())
    elif args.command == "discover":
        print(f"Detected local subnet: {info.network} (own IP {info.ipv4})")
        for host in discover_hosts(info, args.authorized_local_scan, args.max_hosts): print(f"{host.ip:15} {host.hostname or '-'} {host.mac or '-'}")
    elif args.command == "latency":
        targets = {"Gateway": info.gateway, "Public DNS": DEFAULT_CONFIG.public_dns, "Website": DEFAULT_CONFIG.website}
        for result in LatencyMonitor({name: target for name, target in targets.items() if target}).probe_all(): print(result)
    elif args.command == "capture":
        summary = capture_traffic(info.name, args.seconds, args.count)
        print(summary.warning or "Protocol summary:"); [print(f"{name:12} packets={values[0]:4} bytes={values[1]}") for name, values in summary.protocols.items()]; print("Top talkers:"); [print(f"{ip:15} {size} bytes") for ip, size in summary.talkers]
    elif args.command == "chart": print(f"Chart written to: {HistoryStore(DATA / 'history.sqlite3').chart(CHARTS / 'network_history.png')}")

if __name__ == "__main__": main()
