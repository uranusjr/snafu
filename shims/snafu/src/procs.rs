extern crate winapi;

use std::{env, mem};
use std::os::windows::io::AsRawHandle;
use std::path::PathBuf;
use std::process::{Child, Command, abort, exit};

use self::winapi::ctypes::c_void;
use self::winapi::shared::minwindef::{BOOL, DWORD, LPVOID, TRUE};
use self::winapi::um::consoleapi::SetConsoleCtrlHandler;
use self::winapi::um::jobapi2::{
    AssignProcessToJobObject, CreateJobObjectW, QueryInformationJobObject,
    SetInformationJobObject};
use self::winapi::um::wincon::{CTRL_C_EVENT, GenerateConsoleCtrlEvent};
use self::winapi::um::winnt::{
    JOBOBJECT_EXTENDED_LIMIT_INFORMATION,
    JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE, JOB_OBJECT_LIMIT_SILENT_BREAKAWAY_OK,
    JobObjectExtendedLimitInformation};


static mut PID: u32 = 0;

unsafe extern "system" fn handle_ctrl(etype: DWORD) -> BOOL {
    if etype == CTRL_C_EVENT && PID != 0 {
        GenerateConsoleCtrlEvent(PID, CTRL_C_EVENT);
    }
    TRUE
}

unsafe fn setup_child(child: &mut Child) -> Result<(), &'static str> {
    PID = child.id();

    let job = CreateJobObjectW(0 as *mut _, 0 as *const _);
    let mut info: JOBOBJECT_EXTENDED_LIMIT_INFORMATION = mem::zeroed();

    let mut ok;

    ok = QueryInformationJobObject(
        job, JobObjectExtendedLimitInformation,
        &mut info as *mut _ as LPVOID,
        mem::size_of_val(&info) as DWORD,
        0 as *mut _,
    );
    if ok != TRUE {
        return Err("job information query error");
    }

    info.BasicLimitInformation.LimitFlags =
        info.BasicLimitInformation.LimitFlags |
        JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE |
        JOB_OBJECT_LIMIT_SILENT_BREAKAWAY_OK;
    ok = SetInformationJobObject(
        job, JobObjectExtendedLimitInformation,
        &mut info as *mut _ as LPVOID,
        mem::size_of_val(&info) as DWORD,
    );
    if ok != TRUE {
        return Err("job information set error");
    }

    AssignProcessToJobObject(job, child.as_raw_handle() as *mut c_void);

    Ok(())
}

pub fn run(exe: PathBuf, args: Vec<&str>, with_own_args: bool)
        -> Result<i32, String> {

    let mut cmd = Command::new(exe);
    cmd.args(&args);

    // Hand over arguments passed to the shim (args[0] not included).
    if with_own_args {
        cmd.args(env::args().skip(1));
    }

    let mut child = try!(cmd.spawn().map_err(|e| {
        format!("failed to spawn child: {}", e)
    }));

    unsafe { try!(setup_child(&mut child)) };

    let result = try!(child.wait().map_err(|e| {
        format!("failed to wait for child: {}", e)
    }));

    // Doc seems to suggest this won't happen on Windows, but I'm not sure.
    // 137 is a common value seen with SIGKILL terminated programs.
    Ok(result.code().unwrap_or(137))
}

pub fn run_and_end(exe: PathBuf, args: Vec<&str>, own_args: bool) {
    let code = run(exe, args, own_args).unwrap_or_else(|e| {
        eprintln!("{}", e);
        abort();
    });
    exit(code);
    // Won't reach here.
}

pub fn setup() -> Result<(), &'static str> {
    unsafe {
        let ok = SetConsoleCtrlHandler(Some(handle_ctrl), TRUE);
        if ok == TRUE {
            Ok(())
        } else {
            Err("control handler set error")
        }
    }
}
