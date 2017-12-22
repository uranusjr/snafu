extern crate snafu;

use snafu::procs::{setup, run_and_end};
use snafu::pythons::find_of_snafu;
use snafu::run::print_and_abort;

fn main() {
    let python = find_of_snafu().unwrap_or_else(print_and_abort);
    setup().unwrap_or_else(print_and_abort);
    run_and_end(python, vec!["-m", "snafu"], true);
}
