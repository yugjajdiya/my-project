"""C2: authorised local-subnet host discovery, with optional ARP enhancement."""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import socket
import subprocess
import re
from network_info import InterfaceInfo


@dataclass
class Host:
    ip: str
    hostname: str | None
    mac: str | None = None


def _reachable(ip: str, timeout_ms: int) -> bool:
    try:
        return subprocess.run(["ping", "-n", "1", "-w", str(timeout_ms), ip], capture_output=True, timeout=3).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def discover_hosts(info: InterfaceInfo, authorized: bool, max_hosts: int = 254, timeout_ms: int = 500) -> list[Host]:
    """Sweep the detected local subnet after explicit user authorisation."""
    if not authorized:
        raise PermissionError("Discovery is disabled by default. Re-run with --authorized-local-scan only on a network you may scan.")
    hosts = list(info.network.hosts())
    if len(hosts) > max_hosts:
        raise ValueError(f"Detected subnet has {len(hosts)} hosts. Use --max-hosts after confirming authorisation.")
    discovered: list[Host] = []
    with ThreadPoolExecutor(max_workers=32) as pool:
        futures = {pool.submit(_reachable, str(ip), timeout_ms): str(ip) for ip in hosts}
        for future in as_completed(futures):
            ip = futures[future]
            if future.result():
                try:
                    hostname = socket.gethostbyaddr(ip)[0]
                except socket.herror:
                    hostname = None
                discovered.append(Host(ip, hostname))
    try:
        arp_output = subprocess.check_output(["arp", "-a"], text=True, errors="replace", timeout=5)
        mac_by_ip = {match.group(1): match.group(2).replace("-", ":") for match in re.finditer(r"(\d+\.\d+\.\d+\.\d+)\s+([0-9a-f-]{17})", arp_output, re.IGNORECASE)}
        for host in discovered: host.mac = mac_by_ip.get(host.ip)
    except (OSError, subprocess.SubprocessError):
        pass
    return sorted(discovered, key=lambda host: tuple(map(int, host.ip.split("."))))
