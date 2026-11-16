; Script generated for Casino App
#define MyAppName "Casino App"
#define MyAppVersion "1.0"
#define MyAppPublisher "Cooper"
#define MyAppExeName "CasinoApp.exe"

[Setup]
AppId={{E5D93B3C-8A9F-4D2B-8E42-B962A5210D31}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
; Installs to user AppData so SQLite writes never trigger permission errors
DefaultDirName={userappdata}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
; Prevents UAC admin elevation prompts
PrivilegesRequired=lowest
OutputDir=Output
OutputBaseFilename=CasinoApp_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Pulls everything compiled by PyInstaller in dist\CasinoApp
Source: "dist\CasinoApp\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent