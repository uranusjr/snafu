use std::env;
use std::ffi::OsStr;
use std::fmt::{self, Formatter, Display};
use std::io::{Error, ErrorKind, Result};

#[derive(PartialEq)]
enum Bitness {
    Any,
    Win32,
}

pub struct ShimVersion {
    major: String,
    minor: Option<String>,
    bitness: Bitness,
}

impl ShimVersion {
    fn from_parts(p0: &Vec<u8>, p1: &Vec<u8>, bitness: Bitness)
            -> Option<ShimVersion> {
        let v0 = String::from_utf8(p0.clone()).unwrap();
        if v0.is_empty() {
            return None;
        }
        Some(if p1.is_empty() {
            ShimVersion {
                major: v0,
                minor: None,
                bitness: bitness,
            }
        } else {
            ShimVersion {
                major: String::from_utf8(p1.clone()).unwrap(),
                minor: Some(v0),
                bitness: bitness,
            }
        })
    }

    pub fn match_name(&self, value: &str) -> bool {
        let parts: Vec<&str> = value.rsplitn(2, '-').collect();
        if self.bitness == Bitness::Win32 &&
                (parts.len() < 2 || parts[1] != "32") {
            return false;
        }
        let mut part_iter = parts[0].split('.');
        if part_iter.next().unwrap() != &self.major {
            return false;
        }
        match self.minor {
            Some(ref minor) => part_iter.next().unwrap() == minor,
            None => true,
        }
    }
}

impl Display for ShimVersion {
    fn fmt(&self, f: &mut Formatter) -> fmt::Result {
        match self.minor.as_ref() {
            Some(mi) => write!(f, "{}.{}", self.major, mi),
            None => write!(f, "{}", self.major),
        }
    }
}


pub struct ShimInfo {
    pub name: String,
    pub version: Option<ShimVersion>,
}

impl ShimInfo {
    pub fn from_name(name: &str, parse_version: bool) -> Result<ShimInfo> {
        if !parse_version {
            return Ok(ShimInfo {
                name: String::from(name),
                version: None,
            })
        }

        let mut cleaned_name = String::from(name);
        let bitness = if cleaned_name.ends_with("-32") {
            let new_len = cleaned_name.len() - 3;
            cleaned_name.truncate(new_len);
            Bitness::Win32
        } else {
            Bitness::Any
        };

        let mut parts = vec![Vec::new(), Vec::new()];
        let mut parts_i = 0;
        let mut suffix_len = 0;
        for b in cleaned_name.bytes().rev() {
            if b == 0x2e {  // Dot. Push to next part.
                parts_i += 1;
                if parts_i >= parts.len() {
                    break;
                }
            } else if b >= 0x30 && b <= 0x39 {  // ASCII number.
                parts[parts_i].push(b);
            } else if b != 0x2d {   // Ignore dashes; otherwise done.
                break;
            }
            suffix_len += 1;
        }

        let new_len = cleaned_name.len() - suffix_len;
        cleaned_name.truncate(new_len);
        Ok(ShimInfo {
            name: cleaned_name,
            version: ShimVersion::from_parts(&parts[0], &parts[1], bitness),
        })
    }

    pub fn from_current_name(parse_version: bool) -> Result<ShimInfo> {
        let exe = try! { env::current_exe() };
        let exe_os_op = if exe.extension().unwrap_or(OsStr::new("")) == "exe" {
            exe.file_stem()
        } else {
            exe.file_name()
        };

        let exe_os_name = match exe_os_op {
            Some(result) => result,
            None => {
                return Err(Error::new(
                    ErrorKind::InvalidData, "executable name read error",
                ));
            },
        };
        let exe_name = match exe_os_name.to_str() {
            Some(result) => result,
            None => {
                return Err(Error::new(
                    ErrorKind::InvalidData, "executable name convert error",
                ));
            },
        };
        return ShimInfo::from_name(exe_name, parse_version);
    }

    pub fn to_string(&self) -> String {
        match self.version.as_ref() {
            Some(v) => format!("{} {}", self.name, v),
            None => self.name.clone(),
        }
    }
}

impl Display for ShimInfo {
    fn fmt(&self, f: &mut Formatter) -> fmt::Result {
        write!(f, "{}", self.to_string())
    }
}
