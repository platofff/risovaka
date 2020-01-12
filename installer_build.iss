[Setup]
AppName="Рисовака"
AppVersion=0.1
WizardStyle=modern
DefaultDirName={autopf}\risovaka
DefaultGroupName="Рисовака"
Compression=lzma2
SolidCompression=yes
ArchitecturesInstallIn64BitMode="x64"

[Files]
Source: "dist\risovaka\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs; 

[Languages]
Name: "ru"; MessagesFile: "compiler:Languages\Russian.isl"

[Icons]
Name: "{group}\Рисовака (конфигурация)"; Filename: "{app}\risovaka.exe"; Parameters: "configurer"
Name: "{group}\Рисовака"; Filename: "{app}\risovaka.exe"; Parameters: "main"
