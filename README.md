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

## Co robi

<!-- Dopasuj tę listę do faktycznej implementacji przed publikacją. -->

- **Tryb audytu.** Pokazuje, gdzie Copilot jest obecny, i niczego nie zmienia. Od tego warto zacząć.
- **Usuwa aplikację Copilot** dla istniejących użytkowników oraz z obrazu systemu, żeby nie instalowała się nowym kontom.
- **Ustawia polityki w rejestrze** tam, gdzie wersja Home je respektuje.
- **Ukrywa przycisk Copilota** na pasku zadań i opcjonalnie przypisuje klawiszowi Copilot inną funkcję.
- **Wyłącza Copilota w Edge** przez polityki przeglądarki.
- **Przypala kikuty.** Zakłada zadanie, które po aktualizacji systemu sprawdza, czy coś nie odrosło, i zapisuje raport.
- **Przywracanie.** Każda zmiana jest zapisywana, więc da się ją cofnąć jednym poleceniem.

## Użycie

<!-- Nazwy parametrów są przykładowe. -->

```powershell
# Najpierw zobacz, z czym walczysz
.\jolaos.ps1 -Audit

# Zetnij i przypal
.\jolaos.ps1 -Apply

# Gdyby jednak hydra była ci potrzebna
.\jolaos.ps1 -Restore
```

Wymaga uruchomienia jako administrator.

## Czego Jolaos nie zrobi

Nieśmiertelnej głowy Herakles nie zabił. Przywalił ją kamieniem i poszedł dalej. Uczciwie więc:

- Nie usuwa składników wbudowanych w system tak, że ich usunięcie grozi awarią. Te tylko ukrywa.
- Nie gwarantuje, że następna wersja Windows nie przyniesie Copilota w nowym miejscu. Gwarantuje, że to zauważy.
- Nie zastępuje zasad grupy ani Intune w firmie. Jeśli zarządzasz flotą komputerów, użyj narzędzi do tego przeznaczonych.

## Zanim uruchomisz

Eurysteusz już zapowiedział, że tej pracy nie zaliczy.

- Projekt nie jest powiązany z firmą Microsoft. Windows, Copilot i Microsoft Edge są znakami towarowymi Microsoft Corporation.
- Microsoft nie wspiera takich zmian. Aktualizacja może je odwrócić albo coś zepsuć.
- Uruchamiasz na własną odpowiedzialność. Zacznij od trybu audytu i utwórz punkt przywracania systemu.
- Niektóre programy antywirusowe oznaczają narzędzia tego typu jako potencjalnie niechciane. Przeczytaj kod, zanim mu zaufasz.

## Zasada dla współtwórców

Herakles zanurzył strzały we krwi hydry. Były przez to zabójcze, a po latach ta sama trucizna zabiła jego samego.

Nie dopisuj do Jolaosa niczego „przy okazji”. Każdy wyłączony składnik, którego działania nie rozumiesz, wróci kiedyś w postaci zepsutej aktualizacji. Jedna hydra, jedna pochodnia.

## Podziękowania

Szymonowi Szcześniakowi za hydrę. Nazwa jest jego zasługą, błędy moją.
