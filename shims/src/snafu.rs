extern crate winreg;

use std::io;
use std::path::PathBuf;

use self::winreg::RegKey;
use self::winreg::enums::{HKEY_CURRENT_USER, KEY_READ};

pub fn find_python() -> io::Result<PathBuf> {
    let hkcu = RegKey::predef(HKEY_CURRENT_USER);

    let key = try! {
        hkcu.open_subkey_with_flags("Software\\uranusjr\\SNAFU", KEY_READ)
    };
    let value: String = try! { key.get_value("InstallPath") };

    let mut path_buf = PathBuf::new();
    path_buf.push(value);
    path_buf.push("lib\\python\\python.exe");

    Ok(path_buf)
}
