/// Interface to provide functionailties for shims.
///
/// Things in this module only make sense to the shim executables. They are
/// provided here to avoid boilerplate code in the shims.

use std::path::PathBuf;
use std::process::{abort, exit};

use super::pythons::find_of_snafu;
use super::procs::{setup, run, run_and_end};
use super::shims::Shim;
use super::tags::Tag;

pub fn print_and_abort<S: ToString, T>(e: S) -> T {
    eprintln!("{}", e.to_string());
    abort();
}

pub fn python(find_python: fn(&Tag) -> Result<PathBuf, String>) {
    let shim = Shim::from_current_name().unwrap_or_else(print_and_abort);
    let python = find_python(shim.tag()).unwrap_or_else(print_and_abort);
    setup().unwrap_or_else(print_and_abort);
    run_and_end(&python, &vec![], true);
}

pub fn pymod_and_link(find_python: fn(&Tag) -> Result<PathBuf, String>) {
    let shim = Shim::from_current_name().unwrap_or_else(print_and_abort);
    let python = find_python(shim.tag()).unwrap_or_else(print_and_abort);

    setup().unwrap_or_else(print_and_abort);

    // Run easy_install or pip.
    let code = run(
        &python,
        &vec!["-m", shim.name()],
        true,
    ).unwrap_or_else(print_and_abort);
    if code != 0 {
        exit(code);
    }

    // TODO: Only relink when needed. How does Pyenv do this?;
    run_and_end(
        &find_of_snafu().unwrap_or_else(print_and_abort),
        &vec!["-m", "snafu", "link", "--all", "--overwrite=smart"],
        false,
    );
}
