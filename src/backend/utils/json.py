import json
from pathlib import Path
from threading import Lock

class JSONDB:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.lock = Lock()
        if not self.file_path.exists():
            self._write({"readings": [], "alerts": []})

    def _read(self):
        with self.lock:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)

    def _write(self, data):
        with self.lock:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, default=str)

    # CRUD methods
    def get_readings(self):
        return self._read()["readings"]

    def add_reading(self, reading: dict):
        data = self._read()
        data["readings"].append(reading)
        self._write(data)

    def get_alerts(self):
        return self._read()["alerts"]

    def add_alert(self, alert: dict):
        data = self._read()
        data["alerts"].append(alert)
        self._write(data)

    def update_alert(self, alert_id: int, update_fields: dict):
        data = self._read()
        for alert in data["alerts"]:
            if alert["id"] == alert_id:
                alert.update(update_fields)
                break
        self._write(data)

    def clear_all(self):
        self._write({"readings": [], "alerts": []})
