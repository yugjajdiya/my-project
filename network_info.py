"""Runtime interface, address and gateway discovery without hard-coded values."""
from __future__ import annotations
import ipaddress
import socket
import subprocess
import re
from dataclasses import dataclass
import psutil


@dataclass
class InterfaceInfo:
    name: str
    ipv4: str
    netmask: str
    network: ipaddress.IPv4Network
    gateway: str | None


def list_interfaces() -> list[str]:
    """Return interfaces which currently have an IPv4 address."""
    return [name for name, addresses in psutil.net_if_addrs().items()
            if any(address.family == socket.AF_INET and not address.address.startswith("127.") for address in addresses)]


def default_gateway() -> str | None:
    """Read the current default IPv4 gateway from Windows routing output."""
    try:
        output = subprocess.check_output(["route", "print", "-4"], text=True, errors="replace", timeout=5)
        match = re.search(r"^\s*0\.0\.0\.0\s+0\.0\.0\.0\s+(\d+\.\d+\.\d+\.\d+)", output, re.MULTILINE)
        return match.group(1) if match else None
    except (OSError, subprocess.SubprocessError):
        return None


def get_interface_info(interface: str | None = None) -> InterfaceInfo:
    """Resolve a selected or automatically selected active IPv4 interface."""
    candidates = [interface] if interface else list_interfaces()
    for name in candidates:
        for address in psutil.net_if_addrs().get(name, []):
            if address.family == socket.AF_INET and not address.address.startswith("127."):
                network = ipaddress.ip_network(f"{address.address}/{address.netmask}", strict=False)
                return InterfaceInfo(name, address.address, address.netmask, network, default_gateway())
    raise ValueError("No active IPv4 interface was found. Connect to a network or choose another interface.")
