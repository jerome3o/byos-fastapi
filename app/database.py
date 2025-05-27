import json
import sqlite3
from datetime import datetime

from .models import Device, DeviceLog


class Database:
    def __init__(self, db_path: str = "trmnl.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS devices (
                    mac_address TEXT PRIMARY KEY,
                    api_key TEXT UNIQUE NOT NULL,
                    friendly_id TEXT UNIQUE NOT NULL,
                    created_at TEXT NOT NULL,
                    last_seen TEXT,
                    firmware_version TEXT,
                    battery_voltage REAL
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS device_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mac_address TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    data TEXT NOT NULL,
                    FOREIGN KEY (mac_address) REFERENCES devices (mac_address)
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS screens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT UNIQUE NOT NULL,
                    device_id TEXT,
                    content_type TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    file_path TEXT NOT NULL
                )
            """)

    def get_device(self, mac_address: str) -> Device | None:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM devices WHERE mac_address = ?", (mac_address,)
            )
            row = cursor.fetchone()
            if row:
                return Device(
                    mac_address=row["mac_address"],
                    api_key=row["api_key"],
                    friendly_id=row["friendly_id"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    last_seen=datetime.fromisoformat(row["last_seen"])
                    if row["last_seen"]
                    else None,
                    firmware_version=row["firmware_version"],
                    battery_voltage=row["battery_voltage"],
                )
            return None

    def create_device(self, device: Device) -> Device:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO devices (mac_address, api_key, friendly_id, created_at,
                firmware_version) VALUES (?, ?, ?, ?, ?)
            """,
                (
                    device.mac_address,
                    device.api_key,
                    device.friendly_id,
                    device.created_at.isoformat(),
                    device.firmware_version,
                ),
            )
        return device

    def update_device_status(self, mac_address: str, **kwargs):
        fields = []
        values = []

        for key, value in kwargs.items():
            if value is not None:
                if key == "last_seen" and isinstance(value, datetime):
                    value = value.isoformat()
                fields.append(f"{key} = ?")
                values.append(value)

        if fields:
            values.append(mac_address)
            query = f"UPDATE devices SET {', '.join(fields)} WHERE mac_address = ?"
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(query, values)

    def log_device_data(self, mac_address: str, log_data: DeviceLog):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO device_logs (mac_address, timestamp, data)
                VALUES (?, ?, ?)
            """,
                (
                    mac_address,
                    datetime.utcnow().isoformat(),
                    json.dumps(log_data.dict()),
                ),
            )

    def get_device_by_api_key(self, api_key: str) -> Device | None:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM devices WHERE api_key = ?", (api_key,))
            row = cursor.fetchone()
            if row:
                return Device(
                    mac_address=row["mac_address"],
                    api_key=row["api_key"],
                    friendly_id=row["friendly_id"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    last_seen=datetime.fromisoformat(row["last_seen"])
                    if row["last_seen"]
                    else None,
                    firmware_version=row["firmware_version"],
                    battery_voltage=row["battery_voltage"],
                )
            return None
