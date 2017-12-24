use std::{cmp, fmt};

type Code = Option<u16>;
type Arch = Option<u16>;

fn ou_from(digits: &Vec<u8>) -> Option<u16> {
    if digits.is_empty() {
        None
    } else {
        let mut i: u16 = 0;
        for &d in digits.iter().rev() {
            i = i * 10 + d as u16;
        }
        Some(i)
    }
}

pub struct Tag {
    major: Code,
    minor: Code,
    arch: Arch,
}

impl Tag {
    pub fn parse(name: &str) -> (Tag, usize) {
        let mut parts = vec![];
        let mut parts_i = 0;
        let mut suffix_len = 0;
        let mut arch_count = 0;
        for b in name.bytes().rev() {
            match b {
                0x2d => {   // Dash. Can be parsed as the first delimiter.
                    if parts_i == 0 && suffix_len > 0 {
                        arch_count = 1;
                        parts_i += 1;
                    } else {
                        // Eats the dash between shim name and version number.
                        // This handles names like "easy_install-3.6".
                        if parts_i > 0 {
                            suffix_len += 1;
                        }
                        break;
                    }
                },
                0x30 ... 0x39 => {  // ASCII number.
                    while parts.len() <= parts_i {
                        parts.push(vec![]);
                    }
                    parts[parts_i].push(b - 0x30);
                },
                0x2e => {   // Dot. Push to next part.
                    parts_i += 1;
                },
                _ => {
                    break;
                },
            };
            suffix_len += 1;
        }

        let tag = if parts.is_empty() {
            Tag {
                major: None,
                minor: None,
                arch: None,
            }
        } else {
            let arch = if arch_count == 0 {
                None
            } else {
                ou_from(&parts[0])
            };
            match parts_i - arch_count {
                0 => Tag {
                    major: ou_from(&parts[parts_i]),
                    minor: None,
                    arch: arch,
                },
                _ => Tag {
                    major: ou_from(&parts[parts_i]),
                    minor: ou_from(&parts[parts_i - 1]),
                    arch: arch,
                },
            }
        };

        (tag, suffix_len)
    }

    pub fn parse_strict(name: &str) -> Result<Tag, String> {
        let (tag, len) = Tag::parse(&name);
        if len == name.len() {
            Ok(tag)
        } else {
            Err(format!(
                "only parsed {} out of {} in {:?}",
                len, name.len(), name,
            ))
        }
    }

    pub fn from_name(name: &str) -> Tag {
        Tag::parse_strict(name).unwrap()
    }

    /// Whether this tag contain the other.
    ///
    /// This returns `true` if this tag contains `other`, i.e. `other` is
    /// equally with or more specific than `self`.
    pub fn contains(&self, other: &Tag) -> bool {
        // We specify an architecture, but it does not match theirs.
        if self.arch.is_some() && self.arch != other.arch {
            return false;
        }

        // If we don't specify a major, everything matches.
        if self.major.is_none() {
            return true;
        }
        if self.major != other.major {
            return false;
        }

        // Majors and archs match. So there's a match if we don't specify a
        // minor, or the minors also match.
        self.minor.is_none() || self.minor == other.minor
    }

    pub fn is_wildcard(&self) -> bool {
        self.major.is_none()
    }
}

impl fmt::Display for Tag {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        let major = match self.major {
            Some(v) => v,
            None => { return write!(f, ""); },
        };
        let ver = match self.minor {
            Some(v) => format!("{}.{}", major, v),
            None => format!("{}", major),
        };
        match self.arch {
            Some(b) => write!(f, "{}-{}", ver, b),
            None => write!(f, "{}", ver),
        }
    }
}

impl cmp::PartialEq for Tag {
    fn eq(&self, other: &Self) -> bool {
        self.major == other.major &&
        self.minor == other.minor &&
        self.arch == other.arch
    }
}

impl cmp::Eq for Tag {}

impl cmp::PartialOrd for Tag {
    fn partial_cmp(&self, other: &Self) -> Option<cmp::Ordering> {
        Some(self.cmp(other))
    }
}

// Compare an Optional value, where None is always less than Some(_).
fn cmp_opt<T: cmp::Ord>(lh: Option<T>, rh: Option<T>) -> cmp::Ordering {
    match lh {
        Some(lv) => match rh {
            Some(rv) => lv.cmp(&rv),
            None => cmp::Ordering::Greater,
        },
        None => match rh {
            Some(_) => cmp::Ordering::Less,
            None => cmp::Ordering::Equal,
        },
    }
}

impl cmp::Ord for Tag {
    fn cmp(&self, other: &Self) -> cmp::Ordering {
        let major_order = cmp_opt(self.major, other.major);
        if major_order != cmp::Ordering::Equal {
            return major_order;
        }
        let minor_order = cmp_opt(self.minor, other.minor);
        if minor_order != cmp::Ordering::Equal {
            return minor_order;
        }
        cmp_opt(self.arch, other.arch)
    }
}
