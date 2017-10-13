mod shims;

/// Entry point for a generic executable file's shim.
fn main() {
    let code = match shims::run() {
        Ok(code) => code,
        Err(error) => {
            println!("Command failed: {}", error);
            std::process::abort();
        },
    };
    std::process::exit(code);
}
