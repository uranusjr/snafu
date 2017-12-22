extern crate snafu;

use snafu::{pythons, run};

fn main() {
    run::python(pythons::find_best_installed);
}
