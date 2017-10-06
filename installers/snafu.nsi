!include "MUI.nsh"

!define MUI_PAGE_CUSTOMFUNCTION_SHOW ModifyWelcome
!define MUI_PAGE_CUSTOMFUNCTION_LEAVE LeaveWelcome

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"


ShowInstDetails hide

Name "SNAFU Python Manager"
OutFile "snafu-setup.exe"
InstallDir "$LOCALAPPDATA\Programs\SNAFU"


Function ModifyWelcome
    ${NSD_CreateCheckbox} 120u -18u 50% 12u "Append PATH environment variable."
    Pop $1
    SetCtlColors $1 "" ${MUI_BGCOLOR}
FunctionEnd

Section "SNAFU Python Manager"
    CreateDirectory "$INSTDIR"
    SetOutPath "$INSTDIR"

    File /r 'snafu\*'
    CreateDirectory "$INSTDIR\cmd"
    CreateDirectory "$INSTDIR\scripts"

    # Write snafu entry point.
    FileOpen $0 "$INSTDIR\cmd\snafu.cmd" w
    FileWrite $0 "@$\"$INSTDIR\lib\python\python.exe$\" -m snafu %*"
    FileClose $0

    # Install Py launcher.
    nsExec::ExecToLog "msiexec /i $\"$INSTDIR\lib\snafusetup\py.msi$\" /quiet"

    WriteUninstaller "$INSTDIR\Uninstall.exe"
SectionEnd

Function LeaveWelcome
    # Setup environment if the user wishes.
    ${NSD_GetState} $1 $0
    ${If} $0 <> 0
        nsExec::ExecToLog "$\"$INSTDIR\lib\python\python.exe$\" \
            $\"$INSTDIR\lib\snafusetup\env.py$\" $\"$INSTDIR$\""
    ${EndIf}
FunctionEnd


Section "un.Uninstaller"
    nsExec::ExecToLog "$\"$INSTDIR\lib\python\python.exe$\" \
        $\"$INSTDIR\lib\snafusetup\env.py$\" $\"$INSTDIR$\" \
        --uninstall"
    Rmdir /r "$INSTDIR"
SectionEnd
