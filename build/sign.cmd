@echo off
rem Podpisuje plik %1. Ustawienia przekazuje build.ps1 w zmiennych srodowiskowych.
"%JOLAOS_SIGNTOOL%" sign /sha1 %JOLAOS_SIGN_THUMBPRINT% /fd sha256 /tr %JOLAOS_SIGN_TSA% /td sha256 /d Jolaos %1
