!include "MUI.nsh"

!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"


ShowInstDetails hide

Name "SNAFU Python Manager"
OutFile "snafu-setup.exe"
InstallDir "$LOCALAPPDATA\Programs\SNAFU"

Var LIB
Var PYTHON

Section "SNAFU Python Manager"
    CreateDirectory "$INSTDIR"
    SetOutPath "$INSTDIR"

    File /r 'snafu\*'
    CreateDirectory "$INSTDIR\cmd"
    CreateDirectory "$INSTDIR\scripts"

    StrCpy $LIB = "$INSTDIR\lib"
    StrCpy $PYTHON "$LIB\python\python.exe"

    # Write snafu entry point.
    FileOpen $0 "$INSTDIR\cmd\snafu.cmd" w
    FileWrite $0 "@$\"$PYTHON$\" -m snafu %*"
    FileClose $0

    # Install Py launcher.
    nsExec::ExecToLog "msiexec /i $\"$LIB\snafusetup\py.msi$\" /quiet"

    # Setup environment.
    # TODO: Add option whether to perform this.
    nsExec::ExecToLog "$\"$PYTHON$\" $\"$LIB\snafusetup\env.py$\" $\"$INSTDIR$\""

    WriteUninstaller "$INSTDIR\Uninstall.exe"
SectionEnd


Section "un.Uninstaller"
    StrCpy $LIB = "$INSTDIR\lib"
    StrCpy $PYTHON "$LIB\python\python.exe"

    nsExec::ExecToLog "$\"$PYTHON$\" $\"$LIB\snafusetup\env.py$\" $\"$INSTDIR$\" --uninstall"

    Rmdir /r "$INSTDIR"
SectionEnd
