mod inst;
mod procs;
mod pyreg;
mod shims;

/// Entry point for a python.exe shim.
fn main() {
    let shim = shims::ShimInfo::from_current_name(true).unwrap();
    let python = match inst::best_python(shim.version) {
        Ok(pb) => pb,
        Err(error) => {
            eprintln!("lookup failed: {}", error);
            std::process::abort();
        },
    };
    procs::setup();
    procs::run_and_end(python, vec![], true);
}
