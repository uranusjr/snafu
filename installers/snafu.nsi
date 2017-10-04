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

    # TODO: Add option to automatically append snafu to user's PATH.
    # This should be done with registry I guess.
    # The values are at `HKEY_CURRENT_USER\Environment`.

    WriteUninstaller "$INSTDIR\Uninstall.exe"
SectionEnd


Section "un.Uninstaller"
    Rmdir /r "$INSTDIR"
SectionEnd
