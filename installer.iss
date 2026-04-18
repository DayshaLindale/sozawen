[Setup]
AppName=Sozawen
AppVersion=1.0.0
AppPublisher=Daysha Lindale
AppPublisherURL=https://sozawen.com
AppSupportURL=https://sozawen.com
AppUpdatesURL=https://sozawen.com/features.html
DefaultDirName={autopf}\Sozawen
DefaultGroupName=Sozawen
UninstallDisplayIcon={app}\Sozawen.exe
OutputDir=E:\sozawen\installer_output
OutputBaseFilename=SozawenSetup_v1.0.0
Compression=lzma2
SolidCompression=yes
SetupIconFile=E:\sozawen\static\sozawen.ico
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
LicenseFile=E:\sozawen\LICENSE.txt

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "E:\sozawen\dist\Sozawen\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Sozawen"; Filename: "{app}\Sozawen.exe"; IconFilename: "{app}\static\sozawen.ico"
Name: "{group}\Uninstall Sozawen"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Sozawen"; Filename: "{app}\Sozawen.exe"; IconFilename: "{app}\static\sozawen.ico"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Run]
Filename: "{app}\Sozawen.exe"; Description: "Launch Sozawen"; Flags: postinstall nowait skipifsilent
