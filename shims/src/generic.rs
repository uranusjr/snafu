mod shims;

/// Entry point for a generic executable file's shim.
fn main() {
    println!(shims::exec());
    std::process::abort();
}
