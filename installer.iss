; Inno Setup Script for SCRCPY by Sneak
#define MyAppName "SCRCPY by Sneak"
#define MyAppVersion "1.2"
#define MyAppPublisher "SayanRaut"
#define MyAppURL "https://github.com/SayanRaut/SCRCPY-by-SR"
#define MyAppExeName "SCRCPY by Sneak.exe"

[Setup]
; Unique AppId (generate your own or keep this constant)
AppId={{5D2E1467-3F7B-4B79-A12B-0F14D8F32C01}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
; Output location and filename
OutputDir=installer_output
OutputBaseFilename=SCRCPY_by_Sneak_Setup_v{#MyAppVersion}
SetupIconFile=sneak.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Copy all files compiled by PyInstaller in dist/SCRCPY by Sneak
Source: "dist\SCRCPY by Sneak\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\sneak.ico"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\sneak.ico"; Tasks: desktopicon

[Run]
; Option to launch the application immediately after setup finishes
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
