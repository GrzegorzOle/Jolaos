; Instalator Jolaosa. Kompilacja: ISCC.exe build\installer.iss /DAppVersion=0.1.0
; Z podpisem: build\build.ps1 -Sign (dodaje /DSign i /Ssigntool=...).
; Oczekuje gotowego katalogu dist\Jolaos\ z PyInstallera.

#ifndef AppVersion
  #define AppVersion "0.1.0"
#endif
#define AppName "Jolaos"
#define AppPublisher "Grzegorz Oleksy"
#define AppURL "https://github.com/GrzegorzOle/Jolaos"
#define AppExe "Jolaos.exe"

[Setup]
AppId={{6D2A7E2B-6A4E-4B9B-9A3B-7F3F0D1C5E21}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
LicenseFile=..\LICENSE
PrivilegesRequired=admin
OutputDir=..\dist
OutputBaseFilename={#AppName}-Setup-{#AppVersion}
SetupIconFile=jolaos.ico
UninstallDisplayIcon={app}\{#AppExe}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
ShowLanguageDialog=auto
#ifdef Sign
; Polecenie "signtool" przekazuje build.ps1 przez /Ssigntool=...; $f to podpisywany plik.
SignTool=signtool $f
SignedUninstaller=yes
SignToolRetryCount=3
SignToolMinimumTimeBetween=1000
#endif

[Languages]
Name: "polish"; MessagesFile: "compiler:Languages\Polish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Messages]
polish.WelcomeLabel2=Instalator zainstaluje [name/ver] na tym komputerze.%n%nJolaos wymaga uprawnień administratora i prosi o nie przy każdym uruchomieniu, bo zmienia rejestr całego komputera, usuwa aplikacje i zakłada zadanie w harmonogramie.%n%nPrzed kontynuacją zalecane jest zamknięcie innych programów.
english.WelcomeLabel2=Setup will install [name/ver] on this computer.%n%nJolaos requires administrator rights and asks for them at every start, because it changes machine-wide registry entries, removes apps and creates a scheduled task.%n%nIt is recommended that you close all other applications before continuing.

[Files]
Source: "..\dist\{#AppName}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExe}"
Name: "{group}\{cm:UninstallProgram,{#AppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"

[Run]
Filename: "{app}\{#AppExe}"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall skipifsilent unchecked shellexec

[UninstallRun]
; Zadanie strażnika nie może przeżyć programu, który ma uruchamiać.
Filename: "{app}\{#AppExe}"; Parameters: "--remove-guard"; Flags: runhidden waituntilterminated; RunOnceId: "RemoveGuard"
