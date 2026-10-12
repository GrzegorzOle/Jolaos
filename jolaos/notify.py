"""Powiadomienia systemowe Windows (dymki w centrum powiadomień) bez zewnętrznych bibliotek."""

from __future__ import annotations

import sys
from pathlib import Path
from xml.sax.saxutils import escape

from . import winapi

# Identyfikator aplikacji dla centrum powiadomień. Program nie jest pakietem MSIX,
# więc rejestruje go sam w HKCU\Software\Classes\AppUserModelId.
AUMID = "GrzegorzOleksy.Jolaos"
AUMID_PATH = rf"Software\Classes\AppUserModelId\{AUMID}"

CONFIG_KEY = "notify"


def icon_path() -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
    return base / "build" / "jolaos.png"


def register() -> None:
    """Rejestruje nazwę i ikonę, pod którymi Windows pokazuje powiadomienia Jolaosa."""
    try:
        winapi.write_value("HKCU", AUMID_PATH, "DisplayName", "sz", "Jolaos")
        icon = icon_path()
        if icon.exists():
            winapi.write_value("HKCU", AUMID_PATH, "IconUri", "sz", str(icon))
        winapi.write_value("HKCU", AUMID_PATH, "ShowInSettings", "dword", 1)
    except OSError:
        pass


def unregister() -> None:
    try:
        import winreg

        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, AUMID_PATH)
    except OSError:
        pass


def toast(title: str, body: str) -> bool:
    """Pokazuje powiadomienie. Zwraca False, gdy system odmówił (bez wyjątku)."""
    register()
    xml = (
        '<toast><visual><binding template="ToastGeneric">'
        f"<text>{escape(title)}</text><text>{escape(body)}</text>"
        "</binding></visual></toast>"
    )
    script = (
        "[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null; "
        "[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null; "
        "$doc = New-Object Windows.Data.Xml.Dom.XmlDocument; "
        f"$doc.LoadXml('{xml.replace(chr(39), chr(39) * 2)}'); "
        "$toast = New-Object Windows.UI.Notifications.ToastNotification $doc; "
        f"[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('{AUMID}').Show($toast)"
    )
    try:
        result = winapi.run_powershell(script, timeout=30)
    except Exception:  # noqa: BLE001 - brak powiadomienia nie może przerwać strażnika
        return False
    return result.returncode == 0 and not result.stderr.strip()
