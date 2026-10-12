"""Strażnik: sprawdza po logowaniu, czy ścięte głowy nie odrosły, i ścina je ponownie."""

from __future__ import annotations

from datetime import datetime

from .heads import GUARD_ID, Status, build_heads
from .i18n import t
from .journal import Journal, append_log, report_path


def run_guard(journal: Journal | None = None) -> str:
    """Wykonuje jedno sprawdzenie i zwraca treść raportu (zapisaną też do pliku)."""
    journal = journal or Journal()
    heads = {h.id: h for h in build_heads()}
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [f"{t('cli.guard_header')} {stamp}", ""]

    watched = [hid for hid in journal.applied_ids() if hid != GUARD_ID and hid in heads]
    if not watched:
        lines.append(t("cli.guard_not_configured"))
    for hid in watched:
        head = heads[hid]
        result = head.audit()
        if result.status in (Status.PRESENT, Status.PARTIAL):
            try:
                head.apply(journal)
                verdict = t("cli.guard_regrown")
            except Exception as exc:  # noqa: BLE001 - raport ma pokazać każdy błąd
                verdict = f"{t('cli.guard_failed')} ({exc})"
        elif result.status == Status.ERROR:
            verdict = f"{t('status.error')} ({result.detail})"
        else:
            verdict = t("cli.guard_ok")
        lines.append(f"- {head.title}: {verdict}")
        append_log(f"guard {hid}: {verdict}")

    report = "\n".join(lines) + "\n"
    try:
        report_path().write_text(report, encoding="utf-8")
    except OSError:
        pass
    return report


def last_report() -> str | None:
    path = report_path()
    if not path.exists():
        return None
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None
