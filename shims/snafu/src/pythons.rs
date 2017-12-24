extern crate winreg;

use std::collections::BTreeSet;
use std::path::{Path, PathBuf};

use super::tags::Tag;

use self::winreg::RegKey;
use self::winreg::enums::{HKEY_CURRENT_USER, KEY_READ};


fn get(tag: &Tag) -> Result<PathBuf, String> {
    let key_path = Path::new("Software\\Python\\PythonCore")
        .join(tag.to_string()).join("InstallPath");

    let hkcu = RegKey::predef(HKEY_CURRENT_USER);
    let key = try! {
        hkcu.open_subkey_with_flags(&key_path, KEY_READ).map_err(|e| {
            let key_path_string = key_path.to_string_lossy();
            format!("failed to open {}: {}", key_path_string, e)
        })
    };

    let value: String = try! {
        key.get_value("").map_err(|e| {
            let key_path_string = key_path.to_string_lossy();
            format!("failed to read {}: {}", key_path_string, e)
        })
    };
    Ok(PathBuf::from(value).join("python.exe"))
}

fn find_installed() -> BTreeSet<Tag> {
    let mut tags = BTreeSet::new();

    let hkcu = RegKey::predef(HKEY_CURRENT_USER);
    let key_path_str = "Software\\Python\\PythonCore";
    let key = match hkcu.open_subkey_with_flags(key_path_str, KEY_READ) {
        Ok(key) => key,
        Err(e) => {
            eprintln!("failed to read {}: {}", key_path_str, e);
            return tags;
        },
    };

    for enum_result in key.enum_keys() {
        match enum_result
                .map_err(|e| e.to_string())
                .and_then(|name| Tag::parse_strict(&name)) {
            Ok(tag) => {
                tags.insert(tag);
            },
            Err(e) => {
                eprintln!("ignored entry: {}", e);
            },
        }
    }
    tags
}

/// Find a best Python possible to use.
///
/// This collects all installed Pythons from the registry, and select the best
/// match to the tag. Higher version is better, and the 64-bit is preferred
/// when both 64- and 32-bit are installed, but the tag doesn't specify which.
pub fn find_best_installed(tag: &Tag) -> Result<PathBuf, String> {
    for installed_tag in find_installed().iter().rev() {
        if tag.contains(installed_tag) {
            return get(installed_tag);
        }
    }
    Err(format!("failed to find installed Python for {}", tag))
}

/// Find which of the "using" Pythons should be used.
///
/// This collects "using" Pythons in the registry, set by the `snafu use`
/// command, and look at them one by one until one of those match what the
/// tag asks for.
pub fn find_best_using(tag: &Tag) -> Result<PathBuf, String> {
    let key_path_str = "Software\\uranusjr\\SNAFU";

    let hkcu = RegKey::predef(HKEY_CURRENT_USER);
    let key = try! {
        hkcu.open_subkey_with_flags(&key_path_str, KEY_READ).map_err(|e| {
            format!("failed to open {}: {}", key_path_str, e)
        })
    };
    let value: String = try! {
        key.get_value("ActivePythonVersions").map_err(|e| e.to_string())
    };

    for name in value.split(';') {
        match Tag::parse_strict(name) {
            Ok(ref using_tag) => {
                if tag.contains(using_tag) {
                    return get(using_tag);
                }
            },
            Err(e) => {
                eprintln!("ignored used version: {}", e);
            },
        }
    }
    Err(format!("failed to find used Python for {}", tag))
}

/// Find the Python SNAFU is distributed with.
///
/// This should be the embedded Python library bundled with SNAFU, not one of
/// the user's Python distributions.
pub fn find_of_snafu() -> Result<PathBuf, String> {
    let key_path = "Software\\uranusjr\\SNAFU";

    let hkcu = RegKey::predef(HKEY_CURRENT_USER);
    let key = try! {
        hkcu.open_subkey_with_flags(key_path, KEY_READ).map_err(|e| {
            format!("failed to open {}: {}", key_path, e)
        })
    };

    let value: String = try! {
        key.get_value("InstallPath").map_err(|e| {
            format!("failed to read InstallPath of {}: {}", key_path, e)
        })
    };

    let mut path_buf = PathBuf::new();
    path_buf.push(value);
    path_buf.push("lib\\python\\python.exe");
    Ok(path_buf)
}
