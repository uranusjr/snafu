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
    /// Collect information from shim file.
    ///
    /// A shim file is a file with .shim extension that has the same stem, and
    /// resides at the same location as the executable. For example, for an
    /// executable names foo.exe, foo.shim in the same directory is the shim
    /// file.
    ///
    /// The shim file should be text of one or more lines. The first line is
    /// the full path of command to call, and all following non-empty lines
    /// are arguments to pass to the command.
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

/// Run the shim.
///
/// This collects information from the shim file, combines arguments specified
/// in the shim and arguments passed to this program, invokes the program with
/// combined arguments, waits for it, and collects the result.
pub fn run() -> Result<ExitStatus, String> {
    let shim = match Shim::load() {
        Ok(shim) => shim,
        Err(err) => { return Err(String::from(err.description())); },
    };
    let cmd = shim.command;
    let mut args = shim.arguments;

    let mut envargs = std::env::args();
    envargs.next();     // Skip args[0].
    for arg in envargs {
        args.push(arg);
    }

    match Command::new(&cmd).args(&args).status() {
        Ok(status) => Ok(status),
        Err(_) => {
            let mut s = String::from("failed to launch \"");
            s.push_str(&cmd);
            s.push_str("\"");
            return Err(s);
        },
    }
}
