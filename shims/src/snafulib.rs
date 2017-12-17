use std::env;
use std::io::Result;
use std::path::PathBuf;

pub fn find_python() -> Result<PathBuf> {
    let python = try! { env::current_exe() }
        .parent().unwrap_or(&PathBuf::new())
        .parent().unwrap_or(&PathBuf::new())
        .join("lib\\python\\python.exe");

    Ok(python)
}
