# Jolaos

> Herakles ścinał hydrze głowy. Jolaos pilnował, żeby nie odrastały.

Jolaos wyłącza Copilota w Windows 11 Home i pilnuje, żeby nie wrócił po kolejnej aktualizacji.

## Skąd nazwa

Pod jednym z moich wpisów na LinkedIn Szymon Szcześniak (CodeTwo) napisał:

> „Odpinanie Copilot w środowiskach zarządzanych również nie jest ani proste, ani w pełni możliwe dzisiaj. Na razie wyskakuje on wszystkim niemal wszędzie niczym mityczna hydra.”

Trudno o trafniejszy opis. Hydra lernejska miała tę przykrą właściwość, że w miejsce ściętej głowy wyrastały dwie. Herakles sam sobie z nią nie poradził. Dopiero jego bratanek Jolaos wpadł na to, żeby przypalać kikuty pochodnią, i głowy przestały odrastać.

Z Copilotem jest podobnie. Odinstalować go potrafi każdy. Kłopot w tym, że po następnej aktualizacji funkcji wraca, czasem w miejscu, w którym wcześniej go nie było. To narzędzie nie jest więc mieczem, tylko pochodnią.

## Dlaczego akurat Home

W środowiskach zarządzanych, administrator ma przynajmniej zasady grupy i Intune. W wersji Home nie ma edytora zasad grupy, więc użytkownik zostaje z Ustawieniami i dobrą wolą Microsoftu. Jolaos zapisuje bezpośrednio w rejestrze to, co da się zapisać, a po każdej aktualizacji sprawdza, czy coś nie odrosło.

## Bestiariusz

| W micie | W Windows |
|---|---|
| Hydra | Copilot: aplikacja, przycisk na pasku zadań, klawisz na klawiaturze, panel w Edge i kolejne aplikacje systemowe |
| Głowy, które odrastają | Ponowna instalacja po aktualizacji funkcji |
| Krab wysłany przez Herę | Windows Update, który zawsze przychodzi w najmniej odpowiednim momencie |
| Pochodnia Jolaosa | Wpisy polityk w rejestrze i zadanie, które sprawdza stan po aktualizacji |
| Nieśmiertelna głowa pod kamieniem | To, czego nie da się usunąć, a jedynie ukryć (lista niżej) |
| Eurysteusz | Microsoft, który tej pracy nie uzna i nie udzieli na nią wsparcia |

## Jak to wygląda

Jolaos jest zwykłym programem z oknem, nie skryptem. Nie trzeba znać PowerShella ani rejestru. Okno ma trzy zakładki:

1. **Audyt.** Niczego nie zmienia. Pokazuje, w których miejscach Copilot jest obecny na tym komputerze, i wyświetla ostatni raport strażnika.
2. **Wyłączenie.** Lista głów hydry. Każda ma przełącznik i opis napisany dla osoby, która nie jest informatykiem. Zaznaczasz, co ma zostać ścięte, i klikasz „Zastosuj zaznaczone”.
3. **Przywrócenie.** Lista tego, co Jolaos faktycznie zmienił. Każdą zmianę da się cofnąć osobno. Program pamięta stan sprzed zmiany i odtwarza dokładnie jego.

Program jest domyślnie po polsku. W menu „Język” można przełączyć na angielski. Przełącznik w prawym górnym rogu zmienia motyw na ciemny, a menu „Pomoc” prowadzi do dziennika zmian i do treści licencji.

## Co robi

| Głowa | Jak Jolaos ją ścina |
|---|---|
| Aplikacja Copilot | Odinstalowuje pakiet dla wszystkich użytkowników i usuwa go z obrazu systemu, żeby nie instalował się nowym kontom |
| Aplikacja Microsoft 365 Copilot | Jak wyżej. Domyślnie niezaznaczona, bo ten program służy też do otwierania dokumentów Office w przeglądarce |
| Polityka „Wyłącz Windows Copilot” | Wpis `TurnOffWindowsCopilot` w rejestrze, dla bieżącego konta i dla całego komputera |
| Przycisk Copilota na pasku zadań | Wpis `ShowCopilotButton`, czyli to samo, co w Ustawieniach |
| Klawisz Copilot na klawiaturze | Wyłączenie klawisza w mapie skankodów sterownika. Domyślnie niezaznaczone, wymaga restartu |
| Copilot w Edge | Polityka przeglądarki `HubsSidebarEnabled`, którą Edge respektuje także w wersji Home |
| Strażnik (pochodnia) | Zadanie w Harmonogramie zadań, uruchamiane po zalogowaniu. Sprawdza, czy ścięte głowy nie odrosły, i w razie potrzeby ścina je ponownie. Każde sprawdzenie zostawia raport |

Każda zmiana trafia do dziennika w `C:\ProgramData\Jolaos\journal.json` razem ze stanem sprzed zmiany. Tam też jest dziennik zdarzeń i raport strażnika.

## Instalacja

1. Pobierz `Jolaos-Setup-<wersja>.exe` z sekcji Releases.
2. Uruchom instalator. Zapyta o uprawnienia administratora i utworzy skrót na pulpicie.
3. Uruchom Jolaosa ze skrótu. Zacznij od zakładki Audyt.

Odinstalowanie przez „Aplikacje zainstalowane” usuwa program i zadanie strażnika. Wprowadzonych zmian nie cofa. Jeśli chcesz je cofnąć, zrób to wcześniej w zakładce Przywrócenie.

## Czego Jolaos nie zrobi

Nieśmiertelnej głowy Herakles nie zabił. Przywalił ją kamieniem i poszedł dalej. Uczciwie więc:

- Nie usuwa składników wbudowanych w system tak, że ich usunięcie grozi awarią. Te tylko ukrywa.
- Nie gwarantuje, że następna wersja Windows nie przyniesie Copilota w nowym miejscu. Gwarantuje, że to zauważy.
- Nie zastępuje zasad grupy ani Intune w firmie. Jeśli zarządzasz flotą komputerów, użyj narzędzi do tego przeznaczonych.
- Nie potrafi ponownie zainstalować usuniętej aplikacji ze sklepu. Przy przywracaniu otwiera jej stronę w Microsoft Store, resztę robisz sam.

## Zanim uruchomisz

Eurysteusz już zapowiedział, że tej pracy nie zaliczy.

- Projekt nie jest powiązany z firmą Microsoft. Windows, Copilot i Microsoft Edge są znakami towarowymi Microsoft Corporation.
- Microsoft nie wspiera takich zmian. Aktualizacja może je odwrócić albo coś zepsuć.
- Uruchamiasz na własną odpowiedzialność. Zacznij od trybu audytu i utwórz punkt przywracania systemu.
- Niektóre programy antywirusowe oznaczają narzędzia tego typu jako potencjalnie niechciane. Przeczytaj kod, zanim mu zaufasz.

## Budowanie ze źródeł

Potrzebne: Python 3.11 lub nowszy, [Inno Setup 6](https://jrsoftware.org/isinfo.php) oraz pakiety z `requirements-dev.txt`.

```powershell
pip install -r requirements-dev.txt
powershell -ExecutionPolicy Bypass -File build\build.ps1
```

Skrypt generuje ikonę, uruchamia testy, buduje `dist\Jolaos\Jolaos.exe` PyInstallerem i pakuje go do `dist\Jolaos-Setup-<wersja>.exe`.

Bez budowania program uruchomisz poleceniem `python -m jolaos`. Opcja `--audit` wypisuje stan w konsoli, `--guard` wykonuje jedno sprawdzenie strażnika.

Program nie ma zależności poza biblioteką standardową Pythona. Okno jest zrobione w tkinter, zmiany w rejestrze przez `winreg`, aplikacje ze sklepu przez PowerShell.

## Zasada dla współtwórców

Herakles zanurzył strzały we krwi hydry. Były przez to zabójcze, a po latach ta sama trucizna zabiła jego samego.

Nie dopisuj do Jolaosa niczego „przy okazji”. Każdy wyłączony składnik, którego działania nie rozumiesz, wróci kiedyś w postaci zepsutej aktualizacji. Jedna hydra, jedna pochodnia.

Nowa głowa to jeden wpis w `jolaos/heads.py` plus tytuł, opis i opis przywracania w `jolaos/i18n.py`, po polsku i po angielsku. Opis ma być zrozumiały dla osoby, która nigdy nie otwierała rejestru.

## Podziękowania

Szymonowi Szcześniakowi za hydrę. Nazwa jest jego zasługą, błędy moją.
