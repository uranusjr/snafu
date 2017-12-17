extern crate winreg;

use std::io;
use std::path::PathBuf;

use pyreg;
use shims::ShimVersion;

use self::winreg::RegKey;
use self::winreg::enums::{HKEY_CURRENT_USER, KEY_READ};

fn best_python_version(shimver: Option<ShimVersion>) -> io::Result<String> {
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
    Err(io::Error::new(
        io::ErrorKind::InvalidData, "not match for python version",
    ))
}

pub fn best_python(shimver: Option<ShimVersion>) -> io::Result<PathBuf> {
    let name = try! { best_python_version(shimver) };
    Ok(try! { pyreg::find_python_install(&name)}.join("python.exe"))
}
