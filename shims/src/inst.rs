extern crate winreg;

use std::{cmp, io};
use std::collections::BTreeSet;
use std::path::PathBuf;

use pyreg;
use shims::ShimVersion;

use self::winreg::RegKey;
use self::winreg::enums::{HKEY_CURRENT_USER, KEY_READ};


struct PythonVersion {
    major: u8,
    minor: u8,
    bitct: u16,
}

impl PythonVersion {
    fn from(name: &str) -> PythonVersion {
        let parts: Vec<&str> = name.rsplitn(2, '-').collect();
        let bitct: u16 = if parts.len() < 2 {
            64
        } else {
            parts[0].parse().unwrap_or(0)
        };
        let mut part_iter = parts[parts.len() - 1].split('.');
        let major: u8 = part_iter.next().unwrap_or("").parse().unwrap_or(0);
        let minor: u8 = part_iter.next().unwrap_or("").parse().unwrap_or(0);
        PythonVersion {
            major: major,
            minor: minor,
            bitct: bitct,
        }
    }

    fn to_string(&self) -> String {
        if self.bitct == 64 {
            format!("{}.{}", self.major, self.minor)
        } else {
            format!("{}.{}-{}", self.major, self.minor, self.bitct)
        }
    }
}

impl cmp::PartialEq for PythonVersion {
    fn eq(&self, other: &Self) -> bool {
        self.major == other.major &&
        self.minor == other.minor &&
        self.bitct == other.bitct
    }
}

impl cmp::Eq for PythonVersion {}

impl cmp::PartialOrd for PythonVersion {
    fn partial_cmp(&self, other: &Self) -> Option<cmp::Ordering> {
        Some(self.cmp(other))
    }
}

impl cmp::Ord for PythonVersion {
    fn cmp(&self, other: &Self) -> cmp::Ordering {
        if self.major != other.major {
            self.major.cmp(&other.major)
        } else if self.minor != other.minor {
            self.major.cmp(&other.major)
        } else {
            self.bitct.cmp(&other.bitct)
        }
    }
}

fn collect_python_installs() -> BTreeSet<PythonVersion> {
    let mut versions = BTreeSet::new();

    let hkcu = RegKey::predef(HKEY_CURRENT_USER);
    let key = match hkcu.open_subkey_with_flags(
            "Software\\Python\\PythonCore", KEY_READ) {
        Ok(k) => k,
        Err(_) => {
            return versions;
        },
    };

    for name in key.enum_keys() {
        match name {
            Ok(n) => {
                versions.insert(PythonVersion::from(&n));
            },
            Err(_) => {},
        }
    }
    versions
}

pub fn best_python(shimver: Option<ShimVersion>) -> io::Result<PathBuf> {
    for version in collect_python_installs().iter().rev() {
        let name = version.to_string();
        match shimver {
            Some(ref sv) => {
                if !sv.match_name(&name) {
                    continue;
                }
            },
            None => {},
        }
        match pyreg::find_python_install(&name) {
            Ok(pb) => {
                return Ok(pb.join("python.exe"));
            },
            Err(_) => {},
        }
    }
    Err(io::Error::new(io::ErrorKind::InvalidData, match shimver {
        Some(v) => format!("no match for python version {}", v),
        None => String::from("no default python version"),
    }))
}
