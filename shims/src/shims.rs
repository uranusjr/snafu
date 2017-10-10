use std;
use std::error::Error;
use std::fmt::{self, Formatter, Display};
use std::io::ErrorKind;
use std::io::prelude::*;
use std::process::{Command, ExitStatus};
use std::string::String;

struct Shim {
    command: String,
    arguments: Vec<String>,
}

impl Shim {
    fn load() -> std::io::Result<Shim> {
        let exe = try! { std::env::current_exe() };
        let p = exe.with_extension("shim");
        let f = try! { std::fs::File::open(&p) };
        let reader = std::io::BufReader::new(&f);

        let mut lines = reader.lines();
        let command = try! { match lines.next() {
            Some(result) => result,
            None => { return Err(std::io::Error::new(
                    ErrorKind::InvalidData, "Could not read command"));
            },
        } };

        let mut arguments = Vec::new();
        for result in lines {
            let arg = match result {
                Ok(line) => line,
                Err(_) => { continue; },
            };
            arguments.push(arg);
        }

        let mut envargs = std::env::args();
        envargs.next();     // Skip args[0].
        for arg in envargs {
            arguments.push(arg);
        }

        Ok(Shim {
            command: command,
            arguments: arguments,
        })
    }
}

impl Display for Shim {
    fn fmt(&self, f: &mut Formatter) -> fmt::Result {
        write!(f, "{} {}", self.command, self.arguments.join(" "))
    }
}

pub fn run() -> Result<ExitStatus, String> {
    let shim = match Shim::load() {
        Ok(shim) => shim,
        Err(err) => { return Err(String::from(err.description())); },
    };
    match Command::new(&shim.command).args(&shim.arguments).status() {
        Ok(status) => Ok(status),
        Err(_) => {
            let mut s = String::from("failed to launch \"");
            s.push_str(&shim.command);
            s.push_str("\"");
            return Err(s);
        },
    }
}
