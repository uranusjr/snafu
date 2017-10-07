!include "MUI2.nsh"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"


ShowInstDetails hide

Name "SNAFU Python Manager"
OutFile "snafu-setup.exe"
InstallDir "$LOCALAPPDATA\Programs\SNAFU"


!define SNAFU_CMD_STRING "@echo off$\r$\n\
IF [%SNAFU_JUST_TERMINATE%] == [OKAY] ($\r$\n\
  SET SNAFU_JUST_TERMINATE=$\r$\n\
  $\"$INSTDIR\lib\python\python.exe$\" -m snafu %*$\r$\n\
) ELSE ($\r$\n\
  SET SNAFU_JUST_TERMINATE=OKAY$\r$\n\
  CALL <NUL %0 %*$\r$\n\
)"

Section "SNAFU Python Manager"
    CreateDirectory "$INSTDIR"
    SetOutPath "$INSTDIR"

    File /r 'snafu\*'
    CreateDirectory "$INSTDIR\cmd"
    CreateDirectory "$INSTDIR\scripts"

    # Write snafu entry point.
    FileOpen $0 "$INSTDIR\cmd\snafu.cmd" w
    FileWrite $0 "${SNAFU_CMD_STRING}"
    FileClose $0

    # Install Py launcher.
    nsExec::ExecToLog "msiexec /i $\"$INSTDIR\lib\snafusetup\py.msi$\" /quiet"

    # Setup environment.
    # TODO: Add checkbox to disable this,
    nsExec::ExecToLog "$\"$INSTDIR\lib\python\python.exe$\" \
        $\"$INSTDIR\lib\snafusetup\env.py$\" $\"$INSTDIR$\""

    WriteUninstaller "$INSTDIR\Uninstall.exe"
SectionEnd

Section "un.Uninstaller"
    nsExec::ExecToLog "$\"$INSTDIR\lib\python\python.exe$\" \
        $\"$INSTDIR\lib\snafusetup\env.py$\" $\"$INSTDIR$\" \
        --uninstall"
    Rmdir /r "$INSTDIR"
SectionEnd
