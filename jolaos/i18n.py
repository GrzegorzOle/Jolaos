"""Teksty interfejsu. Domyślnie po polsku, z angielskim jako drugim językiem."""

from __future__ import annotations

DEFAULT_LANGUAGE = "pl"
LANGUAGES = {"pl": "Polski", "en": "English"}

_PL = {
    # Okno i menu
    "app.title": "Jolaos",
    "app.subtitle": "Herakles ścinał hydrze głowy. Jolaos pilnował, żeby nie odrastały.",
    "menu.language": "Język",
    "menu.help": "Pomoc",
    "menu.about": "O programie",
    "menu.license": "Licencja MIT (GitHub)",
    "theme.light": "Motyw jasny",
    "theme.dark": "Motyw ciemny",
    "menu.open_journal": "Otwórz folder z dziennikiem",
    "about.text": (
        "Jolaos {version}\n\n"
        "Wyłącza Copilota w Windows 11 Home i pilnuje, żeby nie wrócił po kolejnej "
        "aktualizacji.\n\n"
        "Projekt nie jest powiązany z firmą Microsoft. Windows, Copilot i Microsoft Edge "
        "są znakami towarowymi Microsoft Corporation.\n\n"
        "Licencja MIT."
    ),
    # Zakładki
    "tab.audit": "Audyt",
    "tab.disable": "Wyłączenie",
    "tab.restore": "Przywrócenie",
    "audit.intro": (
        "Tu niczego nie zmieniamy. Program tylko sprawdza, w których miejscach Copilot "
        "jest obecny na tym komputerze. Od tego warto zacząć."
    ),
    "audit.run": "Sprawdź teraz",
    "audit.running": "Sprawdzanie…",
    "audit.guard_report": "Ostatni raport strażnika",
    "audit.no_report": "Strażnik nie zostawił jeszcze żadnego raportu.",
    "disable.intro": (
        "Zaznacz, które głowy hydry mają zostać ścięte. Każda zmiana jest zapisywana "
        "w dzienniku, więc da się ją cofnąć w zakładce Przywrócenie."
    ),
    "disable.run": "Zastosuj zaznaczone",
    "disable.running": "Wprowadzanie zmian…",
    "disable.confirm_title": "Potwierdzenie",
    "disable.confirm": (
        "Zastosować {count} zmian na tym komputerze?\n\n"
        "Zalecamy wcześniejsze utworzenie punktu przywracania systemu."
    ),
    "disable.nothing": "Nie zaznaczono żadnej opcji.",
    "restore.intro": (
        "Tu cofasz zmiany wprowadzone przez Jolaosa. Na liście są tylko te elementy, "
        "które program faktycznie zmienił. Przywrócenie odtwarza stan sprzed zmiany."
    ),
    "restore.run": "Przywróć zaznaczone",
    "restore.running": "Przywracanie…",
    "restore.confirm_title": "Potwierdzenie",
    "restore.confirm": "Przywrócić {count} elementów do stanu sprzed zmiany?",
    "restore.empty": "Dziennik jest pusty. Jolaos niczego jeszcze nie zmienił na tym komputerze.",
    "restore.nothing": "Nie zaznaczono żadnej opcji.",
    "restore.applied_on": "Zmieniono: {when}",
    # Statusy
    "status.unknown": "Nie sprawdzono",
    "status.present": "Obecny",
    "status.absent": "Wyłączony",
    "status.partial": "Częściowo",
    "status.error": "Błąd sprawdzania",
    "status.guard_missing": "Nie założony",
    "status.guard_active": "Czuwa",
    "status.ready": "Gotowy.",
    "status.need_restart": "Niektóre zmiany zadziałają dopiero po ponownym uruchomieniu komputera.",
    "status.need_relogin": "Niektóre zmiany zobaczysz po ponownym zalogowaniu lub restarcie Eksploratora.",
    "status.done": "Zakończono.",
    "status.restart_explorer": "Uruchom ponownie Eksplorator Windows",
    "status.explorer_restarted": "Eksplorator uruchomiony ponownie.",
    # Komunikaty
    "msg.admin_title": "Potrzebne uprawnienia administratora",
    "msg.admin": (
        "Jolaos zmienia ustawienia systemowe, więc musi działać jako administrator. "
        "Uruchomić ponownie z podniesionymi uprawnieniami?"
    ),
    "msg.admin_failed": "Nie udało się uruchomić programu jako administrator.",
    "msg.busy": "Poczekaj, aż bieżąca operacja się zakończy.",
    "log.start_audit": "Rozpoczynam audyt.",
    "log.start_apply": "Rozpoczynam wprowadzanie zmian.",
    "log.start_restore": "Rozpoczynam przywracanie.",
    "log.head": "[{title}] {text}",
    "log.skipped_present": "pominięto, bo już wyłączone",
    "log.applied": "wyłączono",
    "log.restored": "przywrócono",
    "log.failed": "nie udało się: {error}",
    "log.not_in_journal": "brak wpisu w dzienniku, nie ma czego przywracać",
    "note.restart": "Wymaga ponownego uruchomienia komputera.",
    "note.relogin": "Zadziała po ponownym zalogowaniu albo restarcie Eksploratora.",
    "note.store": "Przywrócenie otworzy stronę aplikacji w sklepie Microsoft Store, skąd zainstalujesz ją ponownie.",
    "note.hklm": "Dotyczy wszystkich użytkowników tego komputera.",
    "note.hkcu": "Dotyczy tylko bieżącego konta użytkownika.",
    # CLI
    "cli.audit_header": "Jolaos, audyt",
    "cli.guard_header": "Jolaos, raport strażnika",
    "cli.guard_regrown": "odrosło, ścięto ponownie",
    "cli.guard_ok": "w porządku",
    "cli.guard_failed": "odrosło, nie udało się ściąć ponownie",
    "cli.guard_not_configured": "strażnik nie ma czego pilnować (dziennik pusty)",
}

_EN = {
    "app.title": "Jolaos",
    "app.subtitle": "Heracles cut off the Hydra's heads. Iolaus made sure they did not grow back.",
    "menu.language": "Language",
    "menu.help": "Help",
    "menu.about": "About",
    "menu.license": "MIT License (GitHub)",
    "theme.light": "Light theme",
    "theme.dark": "Dark theme",
    "menu.open_journal": "Open journal folder",
    "about.text": (
        "Jolaos {version}\n\n"
        "Turns Copilot off on Windows 11 Home and makes sure it stays off after the "
        "next update.\n\n"
        "This project is not affiliated with Microsoft. Windows, Copilot and Microsoft "
        "Edge are trademarks of Microsoft Corporation.\n\n"
        "MIT License."
    ),
    "tab.audit": "Audit",
    "tab.disable": "Disable",
    "tab.restore": "Restore",
    "audit.intro": (
        "Nothing is changed here. The program only checks where Copilot is present on "
        "this computer. This is the place to start."
    ),
    "audit.run": "Check now",
    "audit.running": "Checking…",
    "audit.guard_report": "Latest guard report",
    "audit.no_report": "The guard has not left a report yet.",
    "disable.intro": (
        "Select which heads of the Hydra should be cut off. Every change is written to a "
        "journal, so it can be undone on the Restore tab."
    ),
    "disable.run": "Apply selected",
    "disable.running": "Applying changes…",
    "disable.confirm_title": "Confirmation",
    "disable.confirm": (
        "Apply {count} changes to this computer?\n\n"
        "We recommend creating a system restore point first."
    ),
    "disable.nothing": "No option selected.",
    "restore.intro": (
        "Undo the changes made by Jolaos. The list only shows items the program actually "
        "changed. Restoring brings back the state from before the change."
    ),
    "restore.run": "Restore selected",
    "restore.running": "Restoring…",
    "restore.confirm_title": "Confirmation",
    "restore.confirm": "Restore {count} items to their previous state?",
    "restore.empty": "The journal is empty. Jolaos has not changed anything on this computer yet.",
    "restore.nothing": "No option selected.",
    "restore.applied_on": "Changed: {when}",
    "status.unknown": "Not checked",
    "status.present": "Present",
    "status.absent": "Disabled",
    "status.partial": "Partially",
    "status.error": "Check failed",
    "status.guard_missing": "Not set up",
    "status.guard_active": "Watching",
    "status.ready": "Ready.",
    "status.need_restart": "Some changes take effect after a restart of the computer.",
    "status.need_relogin": "Some changes appear after signing in again or restarting Explorer.",
    "status.done": "Finished.",
    "status.restart_explorer": "Restart Windows Explorer",
    "status.explorer_restarted": "Explorer restarted.",
    "msg.admin_title": "Administrator rights required",
    "msg.admin": (
        "Jolaos changes system settings, so it has to run as administrator. "
        "Restart with elevated rights?"
    ),
    "msg.admin_failed": "Could not restart the program as administrator.",
    "msg.busy": "Please wait for the current operation to finish.",
    "log.start_audit": "Starting audit.",
    "log.start_apply": "Starting to apply changes.",
    "log.start_restore": "Starting restore.",
    "log.head": "[{title}] {text}",
    "log.skipped_present": "skipped, already disabled",
    "log.applied": "disabled",
    "log.restored": "restored",
    "log.failed": "failed: {error}",
    "log.not_in_journal": "no journal entry, nothing to restore",
    "note.restart": "Requires a restart of the computer.",
    "note.relogin": "Takes effect after signing in again or restarting Explorer.",
    "note.store": "Restoring opens the app page in Microsoft Store, where you can install it again.",
    "note.hklm": "Applies to all users of this computer.",
    "note.hkcu": "Applies to the current user account only.",
    "cli.audit_header": "Jolaos, audit",
    "cli.guard_header": "Jolaos, guard report",
    "cli.guard_regrown": "grew back, cut off again",
    "cli.guard_ok": "fine",
    "cli.guard_failed": "grew back, could not cut off again",
    "cli.guard_not_configured": "nothing to guard (journal is empty)",
}

# Opisy głów hydry. Klucz: identyfikator głowy.
_HEADS_PL = {
    "copilot_app": {
        "title": "Aplikacja Copilot",
        "desc": (
            "Program „Copilot” z menu Start. Jolaos odinstaluje go dla wszystkich "
            "użytkowników i usunie z obrazu systemu, żeby nie instalował się nowym kontom."
        ),
        "restore": "Otwiera stronę aplikacji Copilot w Microsoft Store, żebyś mógł zainstalować ją ponownie.",
    },
    "m365_copilot_app": {
        "title": "Aplikacja Microsoft 365 Copilot",
        "desc": (
            "Program „Microsoft 365 Copilot” (dawniej „Office” lub „Microsoft 365”). "
            "Służy też do otwierania dokumentów Word i Excel w przeglądarce, dlatego "
            "domyślnie nie jest zaznaczony. Zaznacz, jeśli z niego nie korzystasz."
        ),
        "restore": "Otwiera stronę aplikacji Microsoft 365 Copilot w Microsoft Store.",
    },
    "copilot_policy": {
        "title": "Polityka „Wyłącz Windows Copilot”",
        "desc": (
            "Wpis w rejestrze, którym firmy wyłączają Copilota w całym systemie. "
            "W wersji Home nie ma do niego okienka, ale system go czyta. Zapisujemy go "
            "dla bieżącego konta i dla całego komputera."
        ),
        "restore": "Usuwa wpisy polityki z rejestru (albo przywraca poprzednie, jeśli były).",
    },
    "taskbar_button": {
        "title": "Przycisk Copilota na pasku zadań",
        "desc": (
            "Ikona Copilota obok przycisku Start. To samo, co odznaczenie jej w "
            "Ustawieniach, tylko zapisane bezpośrednio w rejestrze."
        ),
        "restore": "Przywraca poprzednie ustawienie widoczności przycisku.",
    },
    "copilot_key": {
        "title": "Klawisz Copilot na klawiaturze",
        "desc": (
            "Nowe laptopy mają osobny klawisz Copilot. Jolaos wyłącza go na poziomie "
            "sterownika klawiatury, więc naciśnięcie go nie zrobi nic. Nie dotyka "
            "innych klawiszy. Zaznacz tylko wtedy, gdy twoja klawiatura ma ten klawisz."
        ),
        "restore": "Przywraca poprzednią mapę klawiatury.",
    },
    "edge_copilot": {
        "title": "Copilot w przeglądarce Edge",
        "desc": (
            "Panel boczny Copilota w Microsoft Edge wraz z jego przyciskiem na pasku "
            "narzędzi. Edge respektuje tę politykę także w wersji Home."
        ),
        "restore": "Usuwa politykę przeglądarki (albo przywraca poprzednią, jeśli była).",
    },
    "guard": {
        "title": "Strażnik (pochodnia Jolaosa)",
        "desc": (
            "Zadanie w Harmonogramie zadań, które przy każdym logowaniu sprawdza, czy "
            "ścięte głowy nie odrosły po aktualizacji, i w razie potrzeby ścina je ponownie. "
            "Raport z każdego sprawdzenia znajdziesz w zakładce Audyt."
        ),
        "restore": "Usuwa zadanie z Harmonogramu zadań.",
    },
}

_HEADS_EN = {
    "copilot_app": {
        "title": "Copilot app",
        "desc": (
            "The \"Copilot\" program in the Start menu. Jolaos uninstalls it for all "
            "users and removes it from the system image so new accounts do not get it."
        ),
        "restore": "Opens the Copilot app page in Microsoft Store so you can install it again.",
    },
    "m365_copilot_app": {
        "title": "Microsoft 365 Copilot app",
        "desc": (
            "The \"Microsoft 365 Copilot\" program (formerly \"Office\" or \"Microsoft 365\"). "
            "It is also used to open Word and Excel documents in the browser, which is why "
            "it is unselected by default. Select it if you do not use it."
        ),
        "restore": "Opens the Microsoft 365 Copilot app page in Microsoft Store.",
    },
    "copilot_policy": {
        "title": "\"Turn off Windows Copilot\" policy",
        "desc": (
            "The registry entry companies use to turn Copilot off system-wide. Home "
            "edition has no settings page for it, but the system still reads it. It is "
            "written for the current account and for the whole computer."
        ),
        "restore": "Removes the policy entries from the registry (or restores previous ones if present).",
    },
    "taskbar_button": {
        "title": "Copilot button on the taskbar",
        "desc": (
            "The Copilot icon next to the Start button. Same as unticking it in Settings, "
            "only written directly to the registry."
        ),
        "restore": "Restores the previous visibility setting of the button.",
    },
    "copilot_key": {
        "title": "Copilot key on the keyboard",
        "desc": (
            "New laptops have a dedicated Copilot key. Jolaos disables it at the keyboard "
            "driver level, so pressing it does nothing. No other key is touched. Select "
            "only if your keyboard has this key."
        ),
        "restore": "Restores the previous keyboard map.",
    },
    "edge_copilot": {
        "title": "Copilot in Microsoft Edge",
        "desc": (
            "The Copilot side panel in Microsoft Edge together with its toolbar button. "
            "Edge honours this policy on Home edition too."
        ),
        "restore": "Removes the browser policy (or restores the previous one if present).",
    },
    "guard": {
        "title": "Guard (Iolaus' torch)",
        "desc": (
            "A Task Scheduler job that checks at every sign-in whether the severed heads "
            "grew back after an update and cuts them off again if needed. The report of "
            "every check is shown on the Audit tab."
        ),
        "restore": "Removes the job from Task Scheduler.",
    },
}

_TABLES = {"pl": _PL, "en": _EN}
_HEAD_TABLES = {"pl": _HEADS_PL, "en": _HEADS_EN}

_current = DEFAULT_LANGUAGE


def set_language(code: str) -> None:
    global _current
    _current = code if code in _TABLES else DEFAULT_LANGUAGE


def language() -> str:
    return _current


def t(key: str, **kwargs) -> str:
    table = _TABLES.get(_current, _PL)
    text = table.get(key) or _PL.get(key) or key
    return text.format(**kwargs) if kwargs else text


def head_text(head_id: str, field: str) -> str:
    table = _HEAD_TABLES.get(_current, _HEADS_PL)
    entry = table.get(head_id) or _HEADS_PL.get(head_id) or {}
    return entry.get(field, f"{head_id}.{field}")
