# Instrukcja wdrożenia

Dokument ma dwie części. Pierwsza jest dla osoby, która chce zainstalować Jolaosa na swoim komputerze albo na kilku komputerach w domu lub małej firmie. Druga jest dla opiekuna projektu i opisuje, jak zbudować, podpisać i opublikować nową wersję.

## Część 1. Instalacja na komputerze

### Wymagania

- Windows 11 (projekt powstał z myślą o wersji Home, działa też na Pro).
- Konto z uprawnieniami administratora. Instalator i program proszą o podniesienie uprawnień.
- Około 40 MB miejsca na dysku.

### Krok po kroku

1. Wejdź na stronę [Releases](https://github.com/GrzegorzOle/Jolaos/releases) i pobierz najnowszy plik `Jolaos-Setup-<wersja>.exe`.
2. Sprawdź podpis. Kliknij plik prawym przyciskiem, wybierz „Właściwości”, zakładka „Podpisy cyfrowe”. Podpis ma być wystawiony na „Open Source Developer Grzegorz Robert Oleksy”, a w szczegółach ma być napisane, że jest prawidłowy. Jeśli zakładki nie ma albo podpis jest nieprawidłowy, usuń plik i pobierz go ponownie ze strony projektu.
3. Opcjonalnie sprawdź sumę kontrolną. Obok instalatora w Releases leży plik `.sha256`. W PowerShellu:

   ```powershell
   Get-FileHash .\Jolaos-Setup-<wersja>.exe -Algorithm SHA256
   ```

   Wynik ma być identyczny z zawartością pliku `.sha256`.

4. Utwórz punkt przywracania systemu. Start, wpisz „Utwórz punkt przywracania”, przycisk „Utwórz…”.
5. Uruchom instalator. Windows pokaże okno kontroli konta użytkownika z nazwą wydawcy, potwierdź. Instalator kopiuje program do `C:\Program Files\Jolaos`, dodaje skrót na pulpicie i w menu Start.
6. Uruchom Jolaosa ze skrótu. Program ponownie poprosi o uprawnienia administratora.
7. Zacznij od zakładki **Audyt**. Program sam sprawdza stan przy starcie. Czerwona kropka oznacza, że dany element Copilota jest obecny, zielona, że jest wyłączony.
8. Przejdź do zakładki **Wyłączenie**, przeczytaj opisy, zostaw włączone tylko te przełączniki, które rozumiesz, i kliknij „Zastosuj zaznaczone”. Program zapyta o potwierdzenie.
9. Jeśli pasek stanu u dołu prosi o ponowne uruchomienie komputera albo Eksploratora, zrób to.

### Co się dzieje po instalacji

- Dziennik zmian, dziennik zdarzeń i raporty strażnika leżą w `C:\ProgramData\Jolaos`. Menu „Pomoc” ma skrót do tego folderu.
- Jeśli włączysz strażnika, w Harmonogramie zadań pojawi się zadanie `Jolaos`. Uruchamia się minutę po zalogowaniu, sprawdza, czy ścięte głowy nie odrosły, i w razie potrzeby ścina je ponownie. Wynik każdego sprawdzenia widać w zakładce Audyt. Gdy coś odrosło, strażnik pokazuje też zwykłe powiadomienie Windows; gdy wszystko jest w porządku, milczy. Powiadomienia wyłącza przełącznik na dole zakładki Wyłączenie.
- Program nie łączy się z internetem. Jedyny wyjątek to przywracanie aplikacji ze sklepu, które otwiera Microsoft Store.

### Cofanie zmian

Zakładka **Przywrócenie** pokazuje tylko to, co Jolaos faktycznie zmienił, i odtwarza stan sprzed zmiany. Aplikacji usuniętych ze sklepu program nie potrafi zainstalować sam, otwiera ich stronę w Microsoft Store.

### Odinstalowanie

Ustawienia, „Aplikacje”, „Aplikacje zainstalowane”, Jolaos, „Odinstaluj”. Deinstalator usuwa program i zadanie strażnika. Nie cofa wprowadzonych zmian. Jeśli chcesz wrócić do stanu sprzed Jolaosa, najpierw użyj zakładki Przywrócenie, a dopiero potem odinstaluj.

Folder `C:\ProgramData\Jolaos` z dziennikiem zostaje. Możesz go usunąć ręcznie, ale wtedy przywracanie przestanie być możliwe.

### Instalacja cicha

Instalator jest zrobiony w Inno Setup i rozumie jego standardowe przełączniki:

```powershell
.\Jolaos-Setup-<wersja>.exe /VERYSILENT /SUPPRESSMSGBOXES /NORESTART
```

Cicha instalacja nie uruchamia programu i niczego nie zmienia w systemie. Ścinanie głów wymaga świadomej decyzji użytkownika w oknie programu. Odinstalowanie po cichu:

```powershell
"C:\Program Files\Jolaos\unins000.exe" /VERYSILENT
```

### Kilka komputerów

Jolaos jest narzędziem dla pojedynczych komputerów z Windows Home. Jeśli zarządzasz flotą z Windows Pro lub Enterprise, użyj zasad grupy albo Intune, które robią to samo w sposób wspierany przez Microsoft. Jeśli mimo to chcesz wdrożyć Jolaosa na kilku domowych komputerach, powtórz kroki z tej instrukcji na każdym z nich. Dziennik jest lokalny i nie da się go przenieść między maszynami.

### Antywirus

Program zmienia rejestr, usuwa aplikacje ze sklepu i zakłada zadanie harmonogramu. Niektóre programy antywirusowe traktują takie zachowanie jako podejrzane i mogą poddać instalator kwarantannie. Podpis cyfrowy i suma kontrolna pozwalają sprawdzić, że plik jest tym, który opublikował autor. Kod jest otwarty i można go przeczytać przed uruchomieniem.

## Część 2. Wydanie nowej wersji

### Narzędzia

- Python 3.11 lub nowszy, `pip install -r requirements-dev.txt`.
- Inno Setup 6 (`winget install --source winget JRSoftware.InnoSetup`).
- Windows SDK z `signtool.exe` (składnik „Windows SDK Signing Tools for Desktop Apps”).
- Certyfikat code signing Certum na karcie kryptograficznej, czytnik oraz proCertum CardManager, który udostępnia certyfikat w magazynie `CurrentUser\My`.
- `gh` (GitHub CLI) zalogowany na konto z prawem zapisu do repozytorium.

### Przygotowanie

1. Podnieś numer wersji w `jolaos/__init__.py` oraz w `build/version_info.txt` (cztery pola `filevers` i `prodvers`, a także `FileVersion` i `ProductVersion`).
2. Uzupełnij README, jeśli zmienił się zestaw głów.
3. Zacommituj te zmiany na `main`.

### Odcisk certyfikatu

Włóż kartę do czytnika i uruchom proCertum CardManager. Odcisk SHA-1 aktualnego certyfikatu znajdziesz poleceniem:

```powershell
certutil -user -silent -store My | Select-String -Pattern "Open Source Developer" -Context 4,3
```

Szukaj wpisu, którego `NotAfter` jest w przyszłości. Przełącznik `-silent` jest ważny, bez niego certutil próbuje użyć klucza z karty i czeka na PIN.

### Budowanie i podpis

```powershell
powershell -ExecutionPolicy Bypass -File build\build.ps1 -Sign -Thumbprint <odcisk>
```

Odcisk można też ustawić raz w zmiennej `JOLAOS_SIGN_THUMBPRINT`. Skrypt:

1. generuje ikonę i uruchamia testy,
2. buduje `dist\Jolaos\Jolaos.exe` i podpisuje go (karta zapyta o PIN),
3. buduje instalator; Inno Setup podpisuje osobno deinstalator i sam instalator, więc PIN może być potrzebny jeszcze dwa razy,
4. weryfikuje podpisy i zapisuje `dist\Jolaos-Setup-<wersja>.exe.sha256`.

Podpis ma znacznik czasu z `http://time.certum.pl`, dzięki czemu pozostaje ważny po wygaśnięciu certyfikatu. Jeśli serwer czasu nie odpowiada, signtool ponawia próbę trzykrotnie; można też podać inny serwer parametrem `-TimestampUrl`.

Przed publikacją obejrzyj podpis ręcznie:

```powershell
signtool verify /pa /v dist\Jolaos-Setup-<wersja>.exe
```

### Publikacja

```powershell
git tag -a v<wersja> -m "Jolaos <wersja>"
git push origin v<wersja>
gh release create v<wersja> dist\Jolaos-Setup-<wersja>.exe dist\Jolaos-Setup-<wersja>.exe.sha256 --title "Jolaos <wersja>" --notes-file <plik z opisem>
```

Opis wydania pisz po polsku, w punktach: co doszło, co się zmieniło, co trzeba zrobić po aktualizacji (na przykład restart). Katalog `dist` nie trafia do gita.

### Aktualizacja u użytkowników

Nowy instalator uruchomiony na komputerze ze starszą wersją nadpisuje pliki w miejscu. Dziennik w `ProgramData` zostaje, więc zakładka Przywrócenie nadal działa. Zadanie strażnika wskazuje na stałą ścieżkę `C:\Program Files\Jolaos\Jolaos.exe`, więc po aktualizacji uruchamia już nową wersję.
