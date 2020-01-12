; -- Example1.iss --
; Demonstrates copying 3 files and creating an icon.

; SEE THE DOCUMENTATION FOR DETAILS ON CREATING .ISS SCRIPT FILES!

[Setup]
AppName="��������"
AppVersion=0.1
WizardStyle=modern
DefaultDirName={autopf}\risovaka
DefaultGroupName="��������"
Compression=lzma2
SolidCompression=yes
OutputDir="C:\risovaka"
ArchitecturesInstallIn64BitMode="x64"

[Code]
procedure InitializeWizard;
begin
  MsgBox(ExpandConstant('{#SourcePath}'), mbInformation, MB_OK);  
end;

[Files]
Source: "{SourcePath}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs; 

[Languages]
Name: "ru"; MessagesFile: "compiler:Languages\Russian.isl"

[Icons]
Name: "{group}\�������� (������������)"; Filename: "{app}\risovaka.exe"; Parameters: "configurer"
Name: "{group}\��������"; Filename: "{app}\risovaka.exe"; Parameters: "main"
