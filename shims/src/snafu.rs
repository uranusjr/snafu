mod procs;
mod snafulib;

/// Entry point for snafu.exe's shim.
fn main() {
    let python = match snafulib::find_python() {
        Ok(pb) => pb,
        Err(error) => {
            eprintln!("lookup failed: {}", error);
            std::process::abort();
        },
    };
    procs::setup();
    procs::run_and_end(python, vec!["-m", "snafu"], true);
}
