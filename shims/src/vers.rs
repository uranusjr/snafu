extern crate winapi;
extern crate winreg;

use std::io::{Error, ErrorKind, Result};
use std::path::{Path, PathBuf};

use self::winreg::RegKey;
use self::winreg::enums::{HKEY_CURRENT_USER, KEY_READ};

use shims::ShimVersion;


fn find_python_install(name: &str) -> Result<PathBuf> {
    let hkcu = RegKey::predef(HKEY_CURRENT_USER);

    let key_path = Path::new("Software\\Python\\PythonCore")
        .join(name).join("InstallPath");
    let key = try! { hkcu.open_subkey_with_flags(key_path, KEY_READ) };

    let value: String = try! { key.get_value("") };
    Ok(PathBuf::from(value))
}

fn best_python_version_match(shimver: Option<ShimVersion>) -> Result<String> {
    let hkcu = RegKey::predef(HKEY_CURRENT_USER);
    let key = try! {
        hkcu.open_subkey_with_flags("Software\\uranusjr\\SNAFU", KEY_READ)
    };
    let value: String = try! { key.get_value("ActivePythonVersions") };

    for name in value.split(';') {
        match shimver {
            Some(ref v) => {
                if v.match_name(name) {
                    return Ok(String::from(name));
                }
            },
            None => {
                return Ok(String::from(name));
            },
        }
    }
    Err(Error::new(ErrorKind::InvalidData, "not match for python version"))
}

pub fn best_python(shimver: Option<ShimVersion>) -> Result<PathBuf> {
    let name = try! { best_python_version_match(shimver) };
    Ok(try! { find_python_install(&name)}.join("python.exe"))
}
