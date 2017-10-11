mod shims;

/// Entry point for shims of tools that perform setup, e.g. pip, easy_install.
///
/// This entry point hooks back to SNAFU to perform necessary script
/// activation after the installation completes.
fn main() {
    let code = match shims::run() {
        Ok(code) => code,
        Err(error) => {
            println!("Command failed: {}", error);
            std::process::abort();
        },
    };
    // TODO: Hook here.
    std::process::exit(code);
}
