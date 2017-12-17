mod procs;
mod shims;
mod vers;

/// Entry point for a python.exe shim.
fn main() {
    let shim = shims::ShimInfo::from_current_name(true).unwrap();
    let python = match vers::best_python(shim.version) {
        Ok(pb) => pb,
        Err(error) => {
            eprintln!("lookup failed: {}", error);
            std::process::abort();
        },
    };
    procs::setup();
    procs::run_and_end(python, vec![], true);
}
