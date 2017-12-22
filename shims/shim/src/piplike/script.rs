extern crate snafu;

use snafu::{pythons, run};

fn main() {
    run::pymod_and_link(pythons::find_best_using);
}
