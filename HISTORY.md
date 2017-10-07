# Release History

## Next (not released)

### UI Changes

* `uninstall` now attempts to use Windows’s uninstall feature to avoid re-download.
* `install` and `uninstall` receives a `--file` option to allow using local installers without re-downloading.  
  **IMPORTANT:** Correctness of the installer is not checked. The user is responsible for choosing the correct and valid installer file. Results of installing a faulty installer is undefined.
* New command `where` to show where the actual interpreter is. This is useful if you need to pass it to another command (e.g. `pipenv --python`).
* `list` shows activeness.

### Behavioural Changes

* `activate` writes a pin file showing the current active versions.
* Symbols in `snafu list` are changed.

### Installer Changes

* Environment variables are now set up automatically during installation.
* Extract the py launcher MSI to make the distribution substentially smaller.
* The installer now comes with both 64- and 32-bit flavours.


## Version 0.1

Initial release. Features I want the most are largely implemented. Only 64-bit Pythons are supported for now, and the installer is 64-bit-only.

An all-in-one installer that installs SNAFU into
`%LOCALAPPDATA%\Programs\SNAFU`, and sets up the py launcher.

* `snafu install/uninstall <version>`
* `snafu list [--all]`
* `snafu activate/deactivate <version> [<version> ...]`
