extern crate kernel32;
extern crate winapi;

use std::{env, mem, process};
use std::io::Result;
use std::os::windows::io::AsRawHandle;
use std::path::PathBuf;
use std::process::{Child, Command};

use self::winapi::*;
use self::kernel32::*;


static mut PID: u32 = 0;

unsafe extern "system" fn handle_ctrl(etype: DWORD) -> BOOL {
    if etype == CTRL_C_EVENT && PID != 0 {
        GenerateConsoleCtrlEvent(PID, CTRL_C_EVENT);
    }
    TRUE
}

unsafe fn setup_child(child: &mut Child) {
    PID = child.id();

    let job = CreateJobObjectW(0 as *mut _, 0 as *const _);
    let mut info: JOBOBJECT_EXTENDED_LIMIT_INFORMATION;
    info = mem::zeroed();

    let mut ok;

    ok = QueryInformationJobObject(
        job, JobObjectExtendedLimitInformation,
        &mut info as *mut _ as LPVOID,
        mem::size_of_val(&info) as DWORD,
        0 as *mut _,
    );
    assert!(ok == TRUE, "job information query error");

    info.BasicLimitInformation.LimitFlags =
        info.BasicLimitInformation.LimitFlags |
        JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE |
        JOB_OBJECT_LIMIT_SILENT_BREAKAWAY_OK;
    ok = SetInformationJobObject(
        job, JobObjectExtendedLimitInformation,
        &mut info as *mut _ as LPVOID,
        mem::size_of_val(&info) as DWORD,
    );
    assert!(ok == TRUE, "job information set error");

    AssignProcessToJobObject(job, child.as_raw_handle());
}

pub fn run(exe: PathBuf, args: Vec<&str>) -> Result<i32> {
    // Hand over arguments passed to the shim.
    let mut envargs = env::args();
    envargs.next();     // Skip args[0].

    let mut child = try! {
        Command::new(exe).args(&args).args(envargs).spawn()
    };
    unsafe { setup_child(&mut child) };

    match try! { child.wait() }.code() {
        Some(code) => Ok(code),
        // Doc seems to suggest this won't happen on Windows.
        // 137 is a common value seen with SIGKILL terminated programs.
        None => Ok(137),
    }
}

pub fn run_and_end(exe: PathBuf, args: Vec<&str>) {
    let code = match run(exe, args) {
        Ok(code) => code,
        Err(error) => {
            eprintln!("launch failed: {}", error);
            process::abort();
        },
    };
    process::exit(code);
    // Won't reach here.
}

pub fn setup() {
    unsafe {
        let ok = SetConsoleCtrlHandler(Some(handle_ctrl), TRUE);
        assert!(ok == TRUE, "control handler set error");
    }
}
