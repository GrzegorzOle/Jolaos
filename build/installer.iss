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

[Files]
Source: "..\dist\{#AppName}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExe}"
Name: "{group}\{cm:UninstallProgram,{#AppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"

[Run]
Filename: "{app}\{#AppExe}"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
; Zadanie strażnika nie może przeżyć programu, który ma uruchamiać.
Filename: "{app}\{#AppExe}"; Parameters: "--remove-guard"; Flags: runhidden waituntilterminated; RunOnceId: "RemoveGuard"
