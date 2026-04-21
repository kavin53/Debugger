from ctypes import *
from ctypes.wintypes import *

from GrayHat.ghpython_src.py312.my_debugger_defines import DEBUG_PROCESS

kernel32 = windll.kernel32

DEBUG_PROCESS = 0x00000001
CREATE_NEW_CONSOLE = 0x00000010

class STARTUPINFO(Structure):
    _fields_ = [
        ("cb", DWORD),
        ("lpReserved", LPWSTR),
        ("lpDesktop", LPWSTR),
        ("lpTitle", LPWSTR),
        ("dwX", DWORD),
        ("dwY", DWORD),
        ("dwXSize", DWORD),
        ("dwYSize", DWORD),
        ("dwXCountChars", DWORD),
        ("dwYCountChars", DWORD),
        ("dwFillAttribute", DWORD),
        ("dwFlags", DWORD),
        ("wShowWindow", WORD),
        ("cbReserved2", WORD),
        ("lpReserved2", LPBYTE),
        ("hStdInput", HANDLE),
        ("hStdOutput", HANDLE),
        ("hStdError", HANDLE),
    ]

class PROCESS_INFORMATION(Structure):
    _fields_ = [
        ("hProcess", HANDLE),
        ("hThread", HANDLE),
        ("dwProcessId", DWORD),
        ("dwThreadId", DWORD),
    ]

class Debugger:
    def __init__(self):
        self.hProcess = None
        self.hThread = None
        self.pid = None
        self.dwProcessId = None
        self.tid = None
        self.active = False

    def load(self,path):
        si = STARTUPINFO()
        si.cb = sizeof(si)
        pi = PROCESS_INFORMATION()

        success = kernel32.CreateProcessA(
            path.encode(),
            None,
            None,
            None,
            False,
            DEBUG_PROCESS | CREATE_NEW_CONSOLE,
            None,
            None,
            byref(si),
            byref(pi)
        )

        if not success:
            err = kernel32.GetLastError()
            print(f"! Launch failed: {err}")
            return False

        self.hProcess = pi.hProcess
        self.hThread = pi.hThread
        self.pid = pi.dwProcessId
        self.tid = pi.dwThreadId
        self.active = True

if __name__ == "__main__":
    dbg = Debugger()
    dbg.load("C:\\Windows\\SysWow64\\notepad.exe")
    print("Done. No debug loop yet")