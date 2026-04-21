from ctypes import *
from ctypes.wintypes import *

kernel32 = windll.kernel32

INFINITE = 0xFFFFFFFF
DEBUG_PROCESS = 0x00000001
CREATE_NEW_CONSOLE = 0x00000010

DBG_CONTINUE = 0x00010002

EXCEPTION_DEBUG_EVENT = 1
CREATE_PROCESS_DEBUG_EVENT = 3
EXIT_PROCESS_DEBUG_EVENT = 5

class STARTUPINFO(Structure):
        _fields_ = [
            ("cb", DWORD),
            ("lpReserved", LPSTR),
            ("lpDesktop", LPSTR),
            ("lpTitle", LPSTR),
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
            ("hProcess",HANDLE),
            ("hThread",HANDLE),
            ("dwProcessId",DWORD),
            ("dwThreadId",DWORD),
        ]

class CREATE_PROCESS_DEBUG_INFO(Structure):
        _fields_ = [
            ("hFile", HANDLE),
            ("hProcess", HANDLE),
            ("hThread", HANDLE),
            ("lpBaseOfImage", LPVOID),
            ("dwDebugInfoFileOffset", DWORD),
            ("nDebugInfoSize", DWORD),
            ("lpThreadLocalBase", LPVOID),
            ("lpStartAddress", LPVOID),
            ("lpImageName", LPVOID),
            ("fUnicode", WORD),
        ]

class DEBUG_EVENT_UNION(Union):
    _fields_ = [
        ("CreateProcessInfo", CREATE_PROCESS_DEBUG_INFO),
    ]

class DEBUG_EVENT(Structure):
    _fields_ = [
        ("dwDebugEventCode",DWORD),
        ("dwProcessId",DWORD),
        ("dwThreadId",DWORD),
        ("u",DEBUG_EVENT_UNION),
    ]

class Debugger:
    def __init__(self):
        self.hProcess = None
        self.pid = None
        self.base_address = None

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
            byref(pi),
        )

        if not success:
            print(f"Launch Failed: {kernel32.GetLastError()}")
            return False

        self.hProcess = pi.hProcess
        self.pid = pi.dwProcessId

        print(f"pid = {self.pid}")
        return True

    def run(self):
        debug_event = DEBUG_EVENT()

        while True:

            if kernel32.WaitForDebugEvent(byref(debug_event),INFINITE):

                code = debug_event.dwDebugEventCode

                if code == CREATE_PROCESS_DEBUG_EVENT:
                    print("process created")
                    self.base_address = debug_event.u.CreateProcessInfo.lpBaseOfImage
                    print(f"base_address : {hex(self.base_address)}")

                elif code == EXIT_PROCESS_DEBUG_EVENT:
                    print("process exited")
                    break

                else:
                    print(f"Event code : {code}")

                kernel32.ContinueDebugEvent(
                    debug_event.dwProcessId,
                    debug_event.dwThreadId,
                    DBG_CONTINUE,
                )

if __name__ == "__main__":
    dbg = Debugger()
    if dbg.load("C:\\Windows\\SysWow64\\notepad.exe"):
        dbg.run()
