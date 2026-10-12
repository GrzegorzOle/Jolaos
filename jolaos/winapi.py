"""Cienka warstwa nad rejestrem, PowerShellem i uprawnieniami administratora."""

from __future__ import annotations

import ctypes
import json
import os
import subprocess
import sys
import winreg
from dataclasses import dataclass
from typing import Any

HIVES = {
    "HKCU": winreg.HKEY_CURRENT_USER,
    "HKLM": winreg.HKEY_LOCAL_MACHINE,
}

TYPE_NAMES = {
    winreg.REG_DWORD: "dword",
    winreg.REG_SZ: "sz",
    winreg.REG_BINARY: "binary",
    winreg.REG_EXPAND_SZ: "expand_sz",
}
TYPE_CODES = {v: k for k, v in TYPE_NAMES.items()}

CREATE_NO_WINDOW = 0x08000000


@dataclass(frozen=True)
class RegValue:
    """Adres jednej wartości rejestru wraz z pożądaną zawartością."""

    hive: str
    path: str
    name: str
    kind: str
    desired: Any

    @property
    def address(self) -> str:
        return "\\".join((self.hive, self.path, self.name))


def is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def relaunch_as_admin(extra_args: list[str] | None = None) -> bool:
    """Uruchamia bieżący program ponownie z podniesionymi uprawnieniami."""
    if getattr(sys, "frozen", False):
        exe = sys.executable
        args = list(sys.argv[1:])
    else:
        exe = sys.executable
        args = ["-m", "jolaos", *sys.argv[1:]]
    if extra_args:
        args.extend(extra_args)
    params = subprocess.list2cmdline(args)
    rc = ctypes.windll.shell32.ShellExecuteW(None, "runas", exe, params, os.getcwd(), 1)
    return rc > 32


def _open_key(hive: str, path: str, write: bool = False):
    access = winreg.KEY_READ | (winreg.KEY_WRITE if write else 0)
    if write:
        return winreg.CreateKeyEx(HIVES[hive], path, 0, access)
    return winreg.OpenKey(HIVES[hive], path, 0, access)


def read_value(hive: str, path: str, name: str) -> dict | None:
    """Zwraca {"kind": ..., "data": ...} albo None, gdy wartość nie istnieje."""
    try:
        with _open_key(hive, path) as key:
            data, code = winreg.QueryValueEx(key, name)
    except FileNotFoundError:
        return None
    except OSError:
        return None
    kind = TYPE_NAMES.get(code, str(code))
    if isinstance(data, bytes):
        data = data.hex()
    return {"kind": kind, "data": data}


def write_value(hive: str, path: str, name: str, kind: str, data: Any) -> None:
    code = TYPE_CODES[kind]
    if kind == "binary" and isinstance(data, str):
        data = bytes.fromhex(data)
    with _open_key(hive, path, write=True) as key:
        winreg.SetValueEx(key, name, 0, code, data)


def delete_value(hive: str, path: str, name: str) -> None:
    try:
        with _open_key(hive, path, write=True) as key:
            winreg.DeleteValue(key, name)
    except FileNotFoundError:
        pass


def value_matches(current: dict | None, kind: str, desired: Any) -> bool:
    if current is None:
        return False
    if current["kind"] != kind:
        return False
    if kind == "binary":
        want = desired.hex() if isinstance(desired, bytes) else desired
        return current["data"].lower() == str(want).lower()
    return current["data"] == desired


def run_powershell(script: str, timeout: int = 180) -> subprocess.CompletedProcess:
    cmd = [
        "powershell.exe",
        "-NoProfile",
        "-NonInteractive",
        "-ExecutionPolicy",
        "Bypass",
        "-Command",
        script,
    ]
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        creationflags=CREATE_NO_WINDOW,
    )


def powershell_json(script: str, timeout: int = 180) -> Any:
    """Uruchamia skrypt i parsuje jego wyjście jako JSON (pusta lista, gdy brak)."""
    wrapped = (
        "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; "
        f"$__r = @({script}); "
        "ConvertTo-Json -InputObject $__r -Compress -Depth 4"
    )
    result = run_powershell(wrapped, timeout=timeout)
    out = result.stdout.strip()
    if not out:
        return []
    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        return []
    if isinstance(data, dict):
        return [data]
    return data or []


def run_cmd(args: list[str], timeout: int = 60) -> subprocess.CompletedProcess:
    return subprocess.run(
        args,
        capture_output=True,
        text=True,
        encoding="cp852" if os.name == "nt" else "utf-8",
        errors="replace",
        timeout=timeout,
        creationflags=CREATE_NO_WINDOW,
    )


def program_path() -> str:
    """Ścieżka, pod którą zadanie harmonogramu ma uruchamiać Jolaosa."""
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'
    entry = os.path.join(os.path.dirname(os.path.abspath(__file__)), "__main__.py")
    return f'"{sys.executable}" "{entry}"'


def open_in_shell(target: str) -> None:
    os.startfile(target)  # noqa: S606 - celowe otwarcie zasobu przez powłokę
