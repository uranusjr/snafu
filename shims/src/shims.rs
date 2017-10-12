use std;
use std::error::Error;
use std::fmt::{self, Formatter, Display};
use std::io::ErrorKind;
use std::io::prelude::*;
use std::process::Command;
use std::string::String;

struct ExecInfo {
    command: String,
    arguments: Vec<String>,
}

impl ExecInfo {
    /// Collect information from the shim file and current invocation.
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
        let f = try! { std::fs::File::open(&exe.with_extension("shim")) };
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

        Ok(ExecInfo {
            command: command,
            arguments: arguments,
        })
    }
}

impl Display for ExecInfo {
    fn fmt(&self, f: &mut Formatter) -> fmt::Result {
        write!(f, "{} {}", self.command, self.arguments.join(" "))
    }
}

/// Run the shim.
///
/// This collects information, invokes the program, waits for it, and
/// collects the result.
pub fn run() -> Result<i32, String> {
    let info = match ExecInfo::load() {
        Ok(info) => info,
        Err(err) => { return Err(String::from(err.description())); },
    };

    match Command::new(&info.command).args(&info.arguments).status() {
        // Doc seems to suggest this won't ever fail on Windows.
        // 137 is a common value seen with SIGKILL terminated programs.
        Ok(status) => match status.code().unwrap_or(137),
        Err(_) => {
            let mut s = String::from("failed to launch \"");
            s.push_str(&cmd);
            s.push_str("\"");
            Err(s)
        },
    }
}

/// Execute the shim.
///
/// his collects information, invokes the program, waits for it, and swaps out
/// self for the child, never returning (unless there is and error).
pub fn exec() -> &str {
    let info = match ExecInfo::load() {
        Ok(info) => info,
        Err(err) => { return err.description(); },
    };
    match exec::Command::new(&info.command).args(&info.arguments).exec() {
        BadArgument(_) => "Invalid arguments",
        Errno(errno) => format!("Command failed with {}", errno),
    }
}
