extern crate snafu;

use snafu::{pythons, run};

fn main() {
    run::pymod(pythons::find_of_snafu);
}
