!include "MUI2.nsh"
!include "LogicLib.nsh"
!include "WinVer.nsh"
!include "x64.nsh"

!define MUI_PAGE_CUSTOMFUNCTION_SHOW Welcome
!define MUI_PAGE_CUSTOMFUNCTION_LEAVE WelcomeLeave
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

!ifndef PYTHONVERSION
    !error "PYTHONVERSION definition required."
!endif

!define SNAFU_SHIM_STRING "$INSTDIR\lib\python\python.exe$\r$\n-m$\r$\nsnafu"


ShowInstDetails hide
ManifestSupportedOS all

Name "${NAME}"
OutFile "snafu-setup.exe"
InstallDir "$LOCALAPPDATA\Programs\SNAFU"

Var InstallsPythonCheckbox
Var InstallsPython
Var PythonVersionsTxt
Var ActivePythonConfig

Function Welcome
    ${IfNot} ${AtLeastWinVista}
        MessageBox MB_OK "SNAFU only supports Windows Vista or above."
        Quit
    ${EndIf}

    ${NSD_CreateCheckbox} 120u -18u 50% 12u \
        "Set up Python ${PYTHONVERSION} (needs Internet connection)"
    Pop $InstallsPythonCheckbox
    SetCtlColors $InstallsPythonCheckbox "" ${MUI_BGCOLOR}
    ${NSD_SetState} $InstallsPythonCheckbox $InstallsPython
FunctionEnd

Function WelcomeLeave
    ${NSD_GetState} $InstallsPythonCheckbox $InstallsPython
FunctionEnd

Function InstallMSU
    ${If} ${AtLeastWin10}
        Return
    ${ElseIf} ${IsWin8.1}
        StrCpy $R0 '8.1'
    ${ElseIf} ${IsWin8}
        StrCpy $R0 '8-RT'
    ${ElseIf} ${IsWin7}
        StrCpy $R0 '6.1'
    ${ElseIf} ${IsWinVista}
        StrCpy $R0 '6.0'
    ${EndIf}

    ${If} ${RunningX64}
        StrCpy $R1 'x64'
    ${Else}
        StrCpy $R1 'x86'
    ${EndIf}

    DetailPrint "Installing Windows update ${KBCODE} for your system..."
    nsExec::ExecToLog "wusa /quiet /norestart \
        $\"$INSTDIR\lib\setup\Windows$R0-${KBCODE}-$R1.msu$\""
FunctionEnd

Section "SNAFU Python Manager"
    StrCpy $PythonVersionsTxt "$INSTDIR\scripts\.python-versions.txt"
    ${If} ${FileExists} $PythonVersionsTxt
        FileOpen $R0 $PythonVersionsTxt r
        FileRead $R0 $ActivePythonConfig
        FileClose $R0
    ${Else}
        StrCpy $ActivePythonConfig ''
    ${EndIf}

    # Clean up previous installation to prevent script name conflicts (e.g.
    # old package is used instead of new module), and clean up old files.
    Rmdir /r "$INSTDIR"

    CreateDirectory "$INSTDIR"
    SetOutPath "$INSTDIR"

    File /r 'snafu\*'
    CreateDirectory "$INSTDIR\cmd"
    CreateDirectory "$INSTDIR\scripts"

    # Ensure appropriate CRT is installed.
    Call InstallMSU

    # Install Py launcher.
    DetailPrint "Installing Python Launcher (py.exe)..."
    nsExec::ExecToLog "msiexec /i $\"$INSTDIR\lib\setup\py.msi$\" /quiet"

    # Setup environment.
    DetailPrint "Configuring environment..."
    nsExec::ExecToLog "$\"$INSTDIR\lib\python\python.exe$\" \
        $\"$INSTDIR\lib\setup\env.py$\" $\"$INSTDIR$\""

    # Link installed Python versions to \cmd.
    DetailPrint "Discovering existing Pythons..."
    nsExec::ExecToLog "$\"$INSTDIR\lib\python\python.exe$\" \
        $\"$INSTDIR\lib\setup\discovery.py$\""

    # Re-activate versions.
    ${If} $ActivePythonConfig != ''
        DetailPrint "Restoring active versions..."
        FileOpen $R0 $PythonVersionsTxt w
        FileWrite $R0 $ActivePythonConfig
        FileClose $R0
        nsExec::ExecToLog "$\"$INSTDIR\lib\python\python.exe$\" \
            $\"$INSTDIR\lib\setup\activation.py$\""
    ${Endif}

    # Run SNAFU to install Python (if told to).
    ${If} $InstallsPython == ${BST_CHECKED}
        DetailPrint "Installing Python ${PYTHONVERSION}..."
        nsExec::ExecToLog "$\"$INSTDIR\lib\python\python.exe$\" \
            -m snafu install --add ${PYTHONVERSION}"
    ${EndIf}

    # Copy snafu shim.
    CopyFiles "$INSTDIR\lib\shims\snafu.exe" "$INSTDIR\cmd"

    WriteUninstaller "${UNINSTALL_EXE}"
    WriteRegStr HKLM "${UNINSTALL_REGKEY}" "DisplayName" "${NAME}"
    WriteRegStr HKLM "${UNINSTALL_REGKEY}" "Publisher" "Tzu-ping Chung"
    WriteRegStr HKLM "${UNINSTALL_REGKEY}" "UninstallString" "${UNINSTALL_EXE}"
SectionEnd


Section "un.Uninstaller"
    nsExec::ExecToLog "$\"$INSTDIR\lib\python\python.exe$\" \
        $\"$INSTDIR\lib\setup\env.py$\" --uninstall $\"$INSTDIR$\""
    Rmdir /r "$INSTDIR"
    DeleteRegKey HKLM "${UNINSTALL_REGKEY}"
SectionEnd
