mod shims;

/// Entry point for a generic executable file's shim.
fn main() {
    match shims::run() {
        Ok(status) => match status.code() {
            Some(code) => std::process::exit(code),
            None => std::process::exit(0),
        },
        Err(error) => {
            println!("Command failed: {}", error);
            std::process::exit(1);
        },
    };
}
