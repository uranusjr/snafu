use std::process::{abort, exit};

mod procs;
mod pyreg;
mod shims;
mod snafu;
mod used;

/// Entry point for a shim of hookable tools such as pip and easy_install.
/// Theses are launched as "python -m <module>" instead, and hooks back to
/// SNAFU after completion to perform rehashing.
fn main() {
    let shim = shims::ShimInfo::from_current_name(true).unwrap();
    let python = match used::best_python(shim.version) {
        Ok(pb) => pb,
        Err(error) => {
            eprintln!("lookup failed: {}", error);
            abort();
        },
    };

    procs::setup();
    let code = match procs::run(python, vec!["-m", &shim.name], true) {
        Ok(code) => code,
        Err(error) => {
            eprintln!("launch failed: {}", error);
            abort();
        },
    };
    if code != 0 {
        exit(code);
    }

    let snafu_python = match snafu::find_python() {
        Ok(pb) => pb,
        Err(error) => {
            eprintln!("lookup failed: {}", error);
            abort();
        },
    };

    procs::run_and_end(
        snafu_python,
        vec!["-m", "snafu", "link", "--all", "--overwrite=smart"],
        false,
    );
}
