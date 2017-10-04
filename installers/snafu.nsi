!include "MUI.nsh"

!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"


ShowInstDetails hide

Name "SNAFU Python Manager"
OutFile "snafu-setup.exe"
InstallDir "$LOCALAPPDATA\Programs\SNAFU"


Section "SNAFU Python Manager"
    CreateDirectory "$INSTDIR"
    SetOutPath "$INSTDIR"

    File /r "snafu\*"

    nsExec::ExecToLog '$INSTDIR\python-setup.exe /quiet LauncherOnly=1'

    WriteUninstaller "$INSTDIR\Uninstall.exe"
SectionEnd


Section "un.Uninstaller"
    Rmdir /r "$INSTDIR"
SectionEnd
