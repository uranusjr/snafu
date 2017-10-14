Set fso = WScript.CreateObject("Scripting.FileSystemObject")
Set sh = WScript.CreateObject("WScript.Shell")

scriptsDir = fso.GetParentFolderName(WScript.ScriptFullName)

' First argument is abosolute path to the source.
sourceName = WScript.Arguments.Item(0)

' Second argument is abosolute path to the target.
shortcutName = WScript.Arguments.Item(1)

' Pass arguments from third on to the target.
' TODO: Escape arguments better.
arguments = ""
For i = 2 To WScript.Arguments.Count - 1:
    arguments = arguments & """" & WScript.Arguments.Item(i) & """ "
Next

' Create the shortcut from what we have.
Set shortcut = sh.CreateShortcut(shortcutName)
shortcut.TargetPath = sourceName
shortcut.Arguments = arguments
shortcut.Description = """" & sourceName & """ " & arguments
shortcut.WorkingDirectory = ""
shortcut.Save
