!include "MUI2.nsh"
!include "LogicLib.nsh"
!include "WinVer.nsh"
!include "x64.nsh"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"


!define NAME 'SNAFU Python Manager'

!define UNINSTALL_REGKEY \
    'Software\Microsoft\Windows\CurrentVersion\Uninstall\SNAFU'

!define UNINSTALL_EXE "$INSTDIR\Uninstall.exe"

!define KBCODE 'KB2999226'

!define SNAFU_CMD_STRING "@echo off$\r$\n\
IF [%SNAFU_JUST_TERMINATE%] == [OKAY] ($\r$\n\
  SET SNAFU_JUST_TERMINATE=$\r$\n\
  $\"$INSTDIR\lib\python\python.exe$\" -m snafu %*$\r$\n\
) ELSE ($\r$\n\
  SET SNAFU_JUST_TERMINATE=OKAY$\r$\n\
  CALL <NUL %0 %*$\r$\n\
)"


ShowInstDetails hide
ManifestSupportedOS all

Name "${NAME}"
OutFile "snafu-setup.exe"
InstallDir "$LOCALAPPDATA\Programs\SNAFU"


Function .onInit
    ${IfNot} ${AtLeastWinVista}
        MessageBox MB_OK "SNAFU only supports Windows Vista or above."
        Quit
    ${EndIf}
FunctionEnd

Function InstallMCU
    ${If} ${AtLeastWin10}
        Return
    ${ElseIf} ${IsWin8.1}
        StrCpy $0 '8.1'
    ${ElseIf} ${IsWin8}
        StrCpy $0 '8-RT'
    ${ElseIf} ${IsWin7}
        StrCpy $0 '6.1'
    ${ElseIf} ${IsWinVista}
        StrCpy $0 '6.0'
    ${EndIf}

    ${If} ${RunningX64}
        StrCpy $1 'x64'
    ${Else}
        StrCpy $1 'x32'
    ${EndIf}

    nsExec::ExecToLog "wusa /quiet /norestart \
        $\"$INSTDIR\lib\snafusetup\mcu\Windows$0-${KBCODE}-$1.msu$\""
FunctionEnd

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

    # Ensure appropriate CRT is installed.
    Call InstallMCU

    # Setup environment.
    # Do this BEFORE py launcher installation to let it help publish the
    # environ registry. Don't know how they do it, but let's ride their back.
    # TODO: Add checkbox to disable this,
    nsExec::ExecToLog "$\"$INSTDIR\lib\python\python.exe$\" \
        $\"$INSTDIR\lib\snafusetup\env.py$\" $\"$INSTDIR$\""

    # Install Py launcher.
    DetailPrint "Installing Python Launcher (py.exe)..."
    nsExec::ExecToLog "msiexec /i $\"$INSTDIR\lib\snafusetup\py.msi$\" /quiet"

    WriteUninstaller "${UNINSTALL_EXE}"
    WriteRegStr HKLM "${UNINSTALL_REGKEY}" "DisplayName" "${NAME}"
    WriteRegStr HKLM "${UNINSTALL_REGKEY}" "Publisher" "Tzu-ping Chung"
    WriteRegStr HKLM "${UNINSTALL_REGKEY}" "UninstallString" "${UNINSTALL_EXE}"
SectionEnd


Section "un.Uninstaller"
    nsExec::ExecToLog "$\"$INSTDIR\lib\python\python.exe$\" \
        $\"$INSTDIR\lib\snafusetup\env.py$\" $\"$INSTDIR$\" \
        --uninstall"
    Rmdir /r "$INSTDIR"
    DeleteRegKey HKLM "${UNINSTALL_REGKEY}"
SectionEnd
