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

!define VCRUNTIME 'vcruntime140.dll'

!ifndef PYTHONVERSION
    !error "PYTHONVERSION definition required."
!endif


ShowInstDetails hide
ManifestSupportedOS all

Name "${NAME}"
OutFile "snafu-setup.exe"
InstallDir "$LOCALAPPDATA\Programs\SNAFU"

Var InstallsPythonCheckbox
Var InstallsPython

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

Function InstallCRTUpdate
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

    DetailPrint "Installing Windows update ${KBCODE}..."
    nsExec::ExecToLog "wusa /quiet /norestart \
        $\"$INSTDIR\lib\setup\Windows$R0-${KBCODE}-$R1.msu$\""
FunctionEnd

Section "SNAFU Python Manager"
    # Clean up previous installation to prevent script name conflicts (e.g.
    # old package is used instead of new module), and clean up old files.
    Rmdir /r "$INSTDIR"

    CreateDirectory "$INSTDIR"
    SetOutPath "$INSTDIR"

    File /r 'snafu\*'
    CreateDirectory "$INSTDIR\scripts"

    # Ensure appropriate Windows Update for CRT is installed.
    Call InstallCRTUpdate

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
    DetailPrint "Restoring active versions..."
    nsExec::ExecToLog "$\"$INSTDIR\lib\python\python.exe$\" \
        $\"$INSTDIR\lib\setup\activation.py$\""

    # Run SNAFU to install Python (if told to).
    ${If} $InstallsPython == ${BST_CHECKED}
        DetailPrint "Installing Python ${PYTHONVERSION}..."
        nsExec::ExecToLog "$\"$INSTDIR\lib\python\python.exe$\" \
            -m snafu install ${PYTHONVERSION}"
    ${EndIf}

    # Copy DLL required by Rust executables.
    # We just use whatever Python provides, for convinience's sake.
    CopyFiles "$INSTDIR\lib\python\${VCRUNTIME}" "$INSTDIR\cmd"

    # Write SNAFU install information.
    WriteRegStr HKCU "Software\\uranusjr\\SNAFU" "InstallPath" "$INSTDIR"

    # Write uninstaller and register it to Windows.
    WriteUninstaller "${UNINSTALL_EXE}"
    WriteRegStr HKLM "${UNINSTALL_REGKEY}" "DisplayName" "${NAME}"
    WriteRegStr HKLM "${UNINSTALL_REGKEY}" "Publisher" "Tzu-ping Chung"
    WriteRegStr HKLM "${UNINSTALL_REGKEY}" "UninstallString" "${UNINSTALL_EXE}"
SectionEnd


Section "un.Uninstaller"
    nsExec::ExecToLog "$\"$INSTDIR\lib\python\python.exe$\" \
        $\"$INSTDIR\lib\setup\env.py$\" --uninstall $\"$INSTDIR$\""
    Rmdir /r "$INSTDIR"
    DeleteRegKey HKCU "Software\\uranusjr\\SNAFU"
    DeleteRegKey HKLM "${UNINSTALL_REGKEY}"
SectionEnd
