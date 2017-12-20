use std::{env, fmt};

use tags::Tag;


pub struct Shim {
    name: String,
    tag: Tag,
}

impl Shim {
    pub fn from_name(name: &str) -> Shim {
        let (tag, len) = Tag::parse(name);

        let shim_name = name.split_at(name.len() - len).0;
        Shim {
            name: shim_name.to_owned(),
            tag: tag,
        }
    }

    pub fn from_current_name() -> Result<Shim, String> {
        let exe = try!(env::current_exe().map_err(|e| {
            format!("failed to get current command name: {}", e)
        }));
        let name = try! {
            try! {
                exe.extension().map(|ext| {
                    if ext == "exe" {
                        exe.file_stem()
                    } else {
                        exe.file_name()
                    }
                }).unwrap_or(None).ok_or("failed to read command name")
            }.to_str().ok_or("failed to convert command name")
        };
        Ok(Shim::from_name(name))
    }

    pub fn name(&self) -> &str {
        self.name.as_str()
    }

    pub fn tag(&self) -> &Tag {
        &self.tag
    }
}

impl fmt::Display for Shim {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        if self.tag.is_wildcard() {
            write!(f, "{}", self.name)
        } else {
            write!(f, "{} {}", self.name, self.tag)
        }
    }
}
