"""Dziennik zmian i konfiguracja. Jeden plik JSON w ProgramData."""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from . import APP_NAME


def data_dir() -> Path:
    base = os.environ.get("ProgramData") or r"C:\ProgramData"
    path = Path(base) / APP_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def journal_path() -> Path:
    return data_dir() / "journal.json"


def report_path() -> Path:
    return data_dir() / "guard-report.txt"


def log_path() -> Path:
    return data_dir() / "jolaos.log"


class Journal:
    """Pamięta, co Jolaos zmienił, i jak było przedtem."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or journal_path()
        self.data: dict[str, Any] = {"version": 1, "config": {}, "heads": {}}
        self.load()

    def load(self) -> None:
        if not self.path.exists():
            return
        try:
            loaded = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        if isinstance(loaded, dict):
            self.data.update(loaded)
            self.data.setdefault("config", {})
            self.data.setdefault("heads", {})

    def save(self) -> None:
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp, self.path)

    # Konfiguracja
    def get_config(self, key: str, default: Any = None) -> Any:
        return self.data["config"].get(key, default)

    def set_config(self, key: str, value: Any) -> None:
        self.data["config"][key] = value
        self.save()

    # Wpisy głów
    def has(self, head_id: str) -> bool:
        return head_id in self.data["heads"]

    def get(self, head_id: str) -> dict | None:
        return self.data["heads"].get(head_id)

    def record(self, head_id: str, previous: Any) -> None:
        """Zapisuje stan sprzed zmiany. Nie nadpisuje istniejącego wpisu,
        żeby przywrócenie zawsze wracało do stanu sprzed PIERWSZEJ zmiany."""
        if head_id in self.data["heads"]:
            self.data["heads"][head_id]["last_applied"] = _now()
        else:
            self.data["heads"][head_id] = {
                "applied": _now(),
                "last_applied": _now(),
                "previous": previous,
            }
        self.save()

    def forget(self, head_id: str) -> None:
        self.data["heads"].pop(head_id, None)
        self.save()

    def applied_ids(self) -> list[str]:
        return list(self.data["heads"].keys())


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def append_log(line: str) -> None:
    try:
        with log_path().open("a", encoding="utf-8") as fh:
            fh.write(f"{_now()} {line}\n")
    except OSError:
        pass
