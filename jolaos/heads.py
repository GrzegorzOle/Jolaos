"""Katalog głów hydry. Każda głowa umie się sprawdzić, dać się ściąć i odrosnąć na życzenie."""

from __future__ import annotations

import struct
from dataclasses import dataclass, field
from enum import Enum

from . import notify, winapi
from .i18n import head_text, t
from .journal import Journal
from .winapi import RegValue

TASK_NAME = "Jolaos"


class Status(Enum):
    UNKNOWN = "unknown"
    PRESENT = "present"  # głowa jest na miejscu
    ABSENT = "absent"  # głowa ścięta
    PARTIAL = "partial"
    ERROR = "error"


@dataclass
class AuditResult:
    status: Status
    detail: str = ""


class HeadError(RuntimeError):
    """Operacja na głowie się nie powiodła. Komunikat jest przeznaczony dla użytkownika."""


@dataclass
class Head:
    id: str
    default_on: bool = True
    notes: tuple[str, ...] = ()
    needs_restart: bool = False
    needs_relogin: bool = False
    status_labels: dict[Status, str] = field(default_factory=dict)

    @property
    def title(self) -> str:
        return head_text(self.id, "title")

    @property
    def description(self) -> str:
        return head_text(self.id, "desc")

    @property
    def restore_description(self) -> str:
        return head_text(self.id, "restore")

    def status_label(self, status: Status) -> str:
        key = self.status_labels.get(status) or f"status.{status.value}"
        return t(key)

    def audit(self) -> AuditResult:  # pragma: no cover - nadpisywane
        raise NotImplementedError

    def apply(self, journal: Journal) -> None:  # pragma: no cover - nadpisywane
        raise NotImplementedError

    def restore(self, journal: Journal) -> None:  # pragma: no cover - nadpisywane
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Głowy oparte na rejestrze


REGISTRY_LABELS = {
    Status.PRESENT: "status.reg_present",
    Status.ABSENT: "status.reg_absent",
    Status.PARTIAL: "status.reg_partial",
}
APP_LABELS = {
    Status.PRESENT: "status.app_present",
    Status.ABSENT: "status.app_absent",
}


@dataclass
class RegistryHead(Head):
    values: tuple[RegValue, ...] = ()
    status_labels: dict[Status, str] = field(default_factory=lambda: dict(REGISTRY_LABELS))

    def audit(self) -> AuditResult:
        matched = 0
        lines = []
        for value in self.values:
            current = winapi.read_value(value.hive, value.path, value.name)
            ok = winapi.value_matches(current, value.kind, value.desired)
            matched += ok
            shown = "-" if current is None else current["data"]
            lines.append(f"{value.address} = {shown}")
        if matched == len(self.values):
            status = Status.ABSENT
        elif matched == 0:
            status = Status.PRESENT
        else:
            status = Status.PARTIAL
        return AuditResult(status, "\n".join(lines))

    def apply(self, journal: Journal) -> None:
        previous = {
            value.address: winapi.read_value(value.hive, value.path, value.name)
            for value in self.values
        }
        journal.record(self.id, previous)
        for value in self.values:
            try:
                winapi.write_value(value.hive, value.path, value.name, value.kind, value.desired)
            except OSError as exc:
                raise HeadError(f"{value.address}: {exc}") from exc

    def restore(self, journal: Journal) -> None:
        entry = journal.get(self.id)
        if entry is None:
            raise HeadError(t("log.not_in_journal"))
        previous = entry.get("previous") or {}
        for value in self.values:
            before = previous.get(value.address)
            try:
                if before is None:
                    winapi.delete_value(value.hive, value.path, value.name)
                else:
                    winapi.write_value(value.hive, value.path, value.name, before["kind"], before["data"])
            except OSError as exc:
                raise HeadError(f"{value.address}: {exc}") from exc
        journal.forget(self.id)


# ---------------------------------------------------------------------------
# Aplikacje ze sklepu (Appx)


@dataclass
class AppxHead(Head):
    package_names: tuple[str, ...] = ()
    store_id: str = ""
    status_labels: dict[Status, str] = field(default_factory=lambda: dict(APP_LABELS))

    def _query(self) -> tuple[list[dict], list[dict]]:
        names = ", ".join(f"'{n}'" for n in self.package_names)
        installed = winapi.powershell_json(
            f"Get-AppxPackage -AllUsers | Where-Object {{ $_.Name -in @({names}) }} | "
            "Select-Object Name, PackageFullName, "
            "@{n='Users';e={ @($_.PackageUserInformation).Count }}"
        )
        provisioned = winapi.powershell_json(
            f"Get-AppxProvisionedPackage -Online | Where-Object {{ $_.DisplayName -in @({names}) }} | "
            "Select-Object DisplayName, PackageName"
        )
        return installed, provisioned

    def audit(self) -> AuditResult:
        try:
            installed, provisioned = self._query()
        except Exception as exc:  # noqa: BLE001 - raportujemy błąd użytkownikowi
            return AuditResult(Status.ERROR, str(exc))
        lines = [f"{p['Name']} ({p.get('Users', '?')})" for p in installed]
        lines += [f"{p['DisplayName']} [provisioned]" for p in provisioned]
        if not lines:
            return AuditResult(Status.ABSENT, "-")
        return AuditResult(Status.PRESENT, "\n".join(lines))

    def apply(self, journal: Journal) -> None:
        installed, provisioned = self._query()
        journal.record(
            self.id,
            {
                "packages": [p["PackageFullName"] for p in installed],
                "provisioned": [p["PackageName"] for p in provisioned],
            },
        )
        errors = []
        for pkg in provisioned:
            result = winapi.run_powershell(
                f"Remove-AppxProvisionedPackage -Online -PackageName '{pkg['PackageName']}' | Out-Null"
            )
            if result.returncode != 0 and result.stderr.strip():
                errors.append(result.stderr.strip().splitlines()[0])
        for pkg in installed:
            result = winapi.run_powershell(
                f"Get-AppxPackage -AllUsers -Name '{pkg['Name']}' | Remove-AppxPackage -AllUsers"
            )
            if result.returncode != 0 and result.stderr.strip():
                errors.append(result.stderr.strip().splitlines()[0])
        if errors:
            raise HeadError("; ".join(errors))

    def restore(self, journal: Journal) -> None:
        if not journal.has(self.id):
            raise HeadError(t("log.not_in_journal"))
        if self.store_id:
            winapi.open_in_shell(f"ms-windows-store://pdp/?productid={self.store_id}")
        journal.forget(self.id)


# ---------------------------------------------------------------------------
# Klawisz Copilot (mapa skankodów)

SCANCODE_PATH = r"SYSTEM\CurrentControlSet\Control\Keyboard Layout"
SCANCODE_NAME = "Scancode Map"
COPILOT_KEY_SCANCODE = 0x6E  # klawisz Copilot wysyła Win+Shift+F23; F23 ma skankod 0x6E


def parse_scancode_map(raw: bytes | None) -> list[tuple[int, int]]:
    """Zwraca listę par (oryginalny skankod, nowy skankod)."""
    if not raw or len(raw) < 16 or len(raw) % 4:
        return []
    count = struct.unpack_from("<I", raw, 8)[0]
    entries = []
    for i in range(max(count - 1, 0)):
        offset = 12 + 4 * i
        if offset + 4 > len(raw):
            break
        new, original = struct.unpack_from("<HH", raw, offset)
        if original == 0 and new == 0:
            break
        entries.append((original, new))
    return entries


def build_scancode_map(entries: list[tuple[int, int]]) -> bytes:
    data = struct.pack("<III", 0, 0, len(entries) + 1)
    for original, new in entries:
        data += struct.pack("<HH", new, original)
    return data + struct.pack("<I", 0)


@dataclass
class CopilotKeyHead(Head):
    status_labels: dict[Status, str] = field(default_factory=lambda: dict(REGISTRY_LABELS))

    def _current(self) -> tuple[bytes | None, list[tuple[int, int]]]:
        current = winapi.read_value("HKLM", SCANCODE_PATH, SCANCODE_NAME)
        raw = bytes.fromhex(current["data"]) if current and current["kind"] == "binary" else None
        return raw, parse_scancode_map(raw)

    def audit(self) -> AuditResult:
        raw, entries = self._current()
        disabled = (COPILOT_KEY_SCANCODE, 0) in entries
        detail = f"HKLM\\{SCANCODE_PATH}\\{SCANCODE_NAME} = {raw.hex() if raw else '-'}"
        return AuditResult(Status.ABSENT if disabled else Status.PRESENT, detail)

    def apply(self, journal: Journal) -> None:
        raw, entries = self._current()
        journal.record(self.id, None if raw is None else raw.hex())
        entries = [e for e in entries if e[0] != COPILOT_KEY_SCANCODE]
        entries.append((COPILOT_KEY_SCANCODE, 0))
        winapi.write_value("HKLM", SCANCODE_PATH, SCANCODE_NAME, "binary", build_scancode_map(entries))

    def restore(self, journal: Journal) -> None:
        entry = journal.get(self.id)
        if entry is None:
            raise HeadError(t("log.not_in_journal"))
        previous = entry.get("previous")
        if previous is None:
            winapi.delete_value("HKLM", SCANCODE_PATH, SCANCODE_NAME)
        else:
            winapi.write_value("HKLM", SCANCODE_PATH, SCANCODE_NAME, "binary", previous)
        journal.forget(self.id)


# ---------------------------------------------------------------------------
# Strażnik (zadanie harmonogramu)


@dataclass
class GuardHead(Head):
    def audit(self) -> AuditResult:
        result = winapi.run_cmd(["schtasks", "/Query", "/TN", TASK_NAME])
        if result.returncode == 0:
            return AuditResult(Status.ABSENT, f"schtasks: {TASK_NAME}")
        return AuditResult(Status.PRESENT, "-")

    def apply(self, journal: Journal) -> None:
        journal.record(self.id, None)
        notify.register()
        command = f"{winapi.program_path()} --guard"
        result = winapi.run_cmd(
            [
                "schtasks", "/Create", "/F",
                "/TN", TASK_NAME,
                "/TR", command,
                "/SC", "ONLOGON",
                "/DELAY", "0001:00",
                "/RL", "HIGHEST",
            ]
        )
        if result.returncode != 0:
            raise HeadError((result.stderr or result.stdout).strip())

    def restore(self, journal: Journal) -> None:
        result = winapi.run_cmd(["schtasks", "/Delete", "/F", "/TN", TASK_NAME])
        if result.returncode != 0 and "ERROR" in (result.stderr + result.stdout).upper():
            text = (result.stderr or result.stdout).strip()
            if "nie można odnaleźć" not in text.lower() and "cannot find" not in text.lower():
                raise HeadError(text)
        journal.forget(self.id)


# ---------------------------------------------------------------------------
# Katalog

GUARD_ID = "guard"


def build_heads() -> list[Head]:
    return [
        AppxHead(
            id="copilot_app",
            notes=("note.store",),
            package_names=("Microsoft.Copilot", "Microsoft.Windows.Ai.Copilot.Provider"),
            store_id="9NHT9RB2F4HD",
        ),
        AppxHead(
            id="m365_copilot_app",
            default_on=False,
            notes=("note.store",),
            package_names=("Microsoft.MicrosoftOfficeHub",),
            store_id="9WZDNCRD29V9",
        ),
        RegistryHead(
            id="copilot_policy",
            notes=("note.relogin",),
            needs_relogin=True,
            values=(
                RegValue("HKCU", r"Software\Policies\Microsoft\Windows\WindowsCopilot", "TurnOffWindowsCopilot", "dword", 1),
                RegValue("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\WindowsCopilot", "TurnOffWindowsCopilot", "dword", 1),
            ),
        ),
        RegistryHead(
            id="taskbar_button",
            notes=("note.hkcu", "note.relogin"),
            needs_relogin=True,
            values=(
                RegValue("HKCU", r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "ShowCopilotButton", "dword", 0),
            ),
        ),
        CopilotKeyHead(
            id="copilot_key",
            default_on=False,
            notes=("note.hklm", "note.restart"),
            needs_restart=True,
        ),
        RegistryHead(
            id="edge_copilot",
            notes=("note.hklm",),
            values=(
                RegValue("HKLM", r"SOFTWARE\Policies\Microsoft\Edge", "HubsSidebarEnabled", "dword", 0),
            ),
        ),
        GuardHead(
            id=GUARD_ID,
            status_labels={Status.PRESENT: "status.guard_missing", Status.ABSENT: "status.guard_active"},
        ),
    ]


def heads_by_id(heads: list[Head] | None = None) -> dict[str, Head]:
    return {h.id: h for h in (heads or build_heads())}

