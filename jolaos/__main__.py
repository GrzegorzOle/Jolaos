"""Punkt wejścia. Bez argumentów uruchamia okno, z argumentami pracuje w tle."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in (None, ""):  # uruchomienie jako skrypt: python jolaos/__main__.py
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    __package__ = "jolaos"  # noqa: A001

from . import __version__, i18n  # noqa: E402
from .journal import Journal  # noqa: E402


def _cli_audit() -> int:
    from .heads import build_heads

    print(i18n.t("cli.audit_header"))
    for head in build_heads():
        result = head.audit()
        print(f"- {head.title}: {head.status_label(result.status)}")
        for line in result.detail.splitlines():
            print(f"    {line}")
    return 0


def _cli_guard() -> int:
    from .guard import run_guard

    print(run_guard(), end="")
    return 0


def _cli_remove_guard() -> int:
    from .heads import GUARD_ID, heads_by_id

    journal = Journal()
    try:
        heads_by_id()[GUARD_ID].restore(journal)
    except Exception as exc:  # noqa: BLE001 - deinstalator nie ma gdzie tego pokazać
        print(exc, file=sys.stderr)
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="jolaos", add_help=True)
    parser.add_argument("--version", action="version", version=f"Jolaos {__version__}")
    parser.add_argument("--audit", action="store_true", help="wypisz stan i zakończ")
    parser.add_argument("--guard", action="store_true", help="sprawdź, czy głowy odrosły, i ścinaj ponownie")
    parser.add_argument("--remove-guard", action="store_true", help="usuń zadanie strażnika")
    parser.add_argument("--lang", choices=sorted(i18n.LANGUAGES), help="język komunikatów")
    args = parser.parse_args(argv)

    for stream in (sys.stdout, sys.stderr):
        if stream and hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    journal = Journal()
    i18n.set_language(args.lang or journal.get_config("language", i18n.DEFAULT_LANGUAGE))

    if args.audit:
        return _cli_audit()
    if args.guard:
        return _cli_guard()
    if args.remove_guard:
        return _cli_remove_guard()

    from .gui import run_gui

    return run_gui(journal)


if __name__ == "__main__":
    sys.exit(main())
