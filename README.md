# Network Monitoring Tool — Computer Networks PBL Activity 1

**Student:** Jajdiya Yug SanjayBhai  
**Enrollment:** 240210107029  
**Branch / Semester / Batch:** Computer Engineering / 5 / B2  
**Faculty:** Mr. Chinmay Vyas  
**Academic Year:** 2026–27  
**Environment:** Windows, Python 3.13.9; Home Wi-Fi and College Lab

## Implemented requirements

| Code | Module | What it does |
|---|---|---|
| C1 | Interface Traffic Monitor | Uses two successive interface-counter samples to calculate live download/upload Mbps and packet counters. |
| C2 | Local Subnet Host Discovery | Detects the active IPv4 interface, mask and subnet at runtime, then performs an explicitly authorised local sweep with IP/hostname/MAC where available. |
| C3 | Reachability and Latency | Probes the detected gateway, a configurable public DNS resolver and a website; reports min/avg/max RTT, jitter, loss and status over a sliding window. |
| C4 | Traffic Composition | Bounded packet capture showing TCP, UDP, ICMP, ARP, DNS, HTTP/HTTPS and other traffic plus IP top talkers. |
| E1 | Threshold Alerting | Checks throughput, RTT and loss limits; shows alerts and appends timestamped records to `logs/alerts.log`. |
| E3 | Historical Logging & Charting | Persists live dashboard readings to `data/history.sqlite3` and creates a real time-series image in `charts/`. |

## Install

Use Windows PowerShell from this folder:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

The declared libraries are `psutil`, `rich`, `matplotlib`, and `scapy`. Packet capture on Windows also needs [Npcap](https://npcap.com/) and may require starting PowerShell as Administrator.

## Run

```powershell
python main.py interfaces
python main.py dashboard
python main.py dashboard --duration 60
python main.py traffic --samples 5
python main.py latency
python main.py discover --authorized-local-scan
python main.py capture --seconds 10 --count 250
python main.py chart
```

Use `--interface "Wi-Fi"` on any command if automatic selection chooses the wrong active interface. The tool intentionally discovers interfaces, IP address, subnet, and gateway at runtime; it does not contain fixed local network values.

## Safety and error handling

- Only use `discover --authorized-local-scan` on a local network you are authorised to scan. The command refuses to scan until that confirmation is present and rejects detected subnets over 254 hosts unless you knowingly change `--max-hosts`.
- `capture` collects only a bounded number/duration of packets on your chosen interface. It reports Npcap/permission issues without crashing.
- Unreachable targets show `DOWN`, and unavailable interfaces report a clear error.
- Defaults in `config.py` are conservative starting values. Adjust thresholds and targets there for your own approved environment.

## Genuine evidence for the report

Do not submit supplied or edited measurements. Run the commands on your own Home Wi-Fi or College Lab connection and capture full-screen images that visibly include the dashboard hostname, IP/subnet and system date/time. Use one genuine screenshot per module (C1–C4, E1, E3). The generated `charts/network_history.png` is the E3 chart after the dashboard has recorded readings. A threshold alert is demonstrated by temporarily setting a realistic low threshold in `config.py`, running the dashboard, and retaining the resulting screen plus timestamped `logs/alerts.log` entry.

## Suggested three-function walkthrough

Explain these in your own words in the report:

1. `TrafficMonitor.sample()` in `traffic_monitor.py`: why rates need a previous counter and elapsed time.
2. `discover_hosts()` in `host_discovery.py`: how the detected `IPv4Network` provides usable hosts and why authorisation is checked.
3. `LatencyMonitor.probe_all()` in `latency_monitor.py`: how the sliding window derives RTT statistics, jitter and loss.

## Limitations

ICMP can be blocked, devices may not answer ping, and MAC/hostname data depend on the local network and ARP/DNS availability. Packet capture needs Npcap and suitable permissions. The monitor is intended for short, supervised educational measurements, not continuous production monitoring.
