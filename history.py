"""E3: SQLite persistence and a genuine tool-generated time-series chart."""
from __future__ import annotations
from datetime import datetime
from pathlib import Path
import sqlite3


class HistoryStore:
    def __init__(self, database_path: Path):
        self.database_path = database_path
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute("CREATE TABLE IF NOT EXISTS measurements (timestamp TEXT, download_mbps REAL, upload_mbps REAL, gateway_rtt_ms REAL)")

    def _connect(self): return sqlite3.connect(self.database_path)

    def save(self, download: float, upload: float, gateway_rtt: float | None) -> None:
        with self._connect() as connection:
            connection.execute("INSERT INTO measurements VALUES (?, ?, ?, ?)", (datetime.now().astimezone().isoformat(timespec="seconds"), download, upload, gateway_rtt))

    def chart(self, output_path: Path) -> Path:
        import matplotlib.pyplot as plot
        with self._connect() as connection:
            rows = connection.execute("SELECT timestamp, download_mbps, upload_mbps, gateway_rtt_ms FROM measurements ORDER BY rowid").fetchall()
        if not rows: raise ValueError("No history has been recorded yet. Run the dashboard or traffic command first.")
        timestamps = [datetime.fromisoformat(row[0]) for row in rows]
        figure, axes = plot.subplots(2, 1, sharex=True, figsize=(10, 6))
        axes[0].plot(timestamps, [row[1] for row in rows], label="Download Mbps"); axes[0].plot(timestamps, [row[2] for row in rows], label="Upload Mbps")
        axes[0].set_ylabel("Mbps"); axes[0].legend(); axes[0].grid(True, alpha=.3)
        axes[1].plot(timestamps, [row[3] for row in rows], label="Gateway RTT ms", color="purple")
        axes[1].set_ylabel("ms"); axes[1].legend(); axes[1].grid(True, alpha=.3)
        figure.suptitle("Network Monitoring History (genuine runtime data)"); figure.autofmt_xdate(); figure.tight_layout()
        output_path.parent.mkdir(parents=True, exist_ok=True); figure.savefig(output_path, dpi=150); plot.close(figure)
        return output_path
