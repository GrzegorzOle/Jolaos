"""Sprawdzanie nowej wersji w wydaniach na GitHubie. Jedyne połączenie z internetem w programie."""

from __future__ import annotations

import json
import re
import urllib.request
from dataclasses import dataclass

from . import __version__

RELEASES_API = "https://api.github.com/repos/GrzegorzOle/Jolaos/releases/latest"
RELEASES_PAGE = "https://github.com/GrzegorzOle/Jolaos/releases/latest"
CONFIG_KEY = "check_updates"
TIMEOUT = 6


@dataclass(frozen=True)
class UpdateInfo:
    version: str
    page_url: str
    download_url: str


def parse_version(text: str) -> tuple[int, ...]:
    numbers = re.findall(r"\d+", text or "")
    return tuple(int(n) for n in numbers[:4]) or (0,)


def is_newer(candidate: str, current: str = __version__) -> bool:
    return parse_version(candidate) > parse_version(current)


def fetch_latest() -> UpdateInfo | None:
    """Zwraca informację o najnowszym wydaniu albo None, gdy nie udało się jej pobrać."""
    request = urllib.request.Request(
        RELEASES_API,
        headers={"Accept": "application/vnd.github+json", "User-Agent": f"Jolaos/{__version__}"},
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception:  # noqa: BLE001 - brak sieci, limit API, zły JSON: wszystko znaczy "nie wiadomo"
        return None
    if not isinstance(data, dict) or data.get("draft") or data.get("prerelease"):
        return None
    tag = str(data.get("tag_name") or "")
    page = str(data.get("html_url") or RELEASES_PAGE)
    download = page
    for asset in data.get("assets") or []:
        name = str(asset.get("name") or "")
        if name.lower().endswith(".exe") and "setup" in name.lower():
            download = str(asset.get("browser_download_url") or page)
            break
    version = ".".join(str(n) for n in parse_version(tag))
    return UpdateInfo(version=version, page_url=page, download_url=download)


def check_for_update() -> UpdateInfo | None:
    """Zwraca informację tylko wtedy, gdy wydanie jest nowsze niż uruchomiony program."""
    info = fetch_latest()
    if info and is_newer(info.version):
        return info
    return None
