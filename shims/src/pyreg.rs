extern crate winreg;

use std::io;
use std::path::{Path, PathBuf};

use self::winreg::RegKey;
use self::winreg::enums::{HKEY_CURRENT_USER, KEY_READ};


pub fn find_python_install(name: &str) -> io::Result<PathBuf> {
    let hkcu = RegKey::predef(HKEY_CURRENT_USER);

    let key_path = Path::new("Software\\Python\\PythonCore")
        .join(name).join("InstallPath");
    let key = try! { hkcu.open_subkey_with_flags(key_path, KEY_READ) };

    let value: String = try! { key.get_value("") };
    Ok(PathBuf::from(value))
}
