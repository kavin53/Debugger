from ctypes import *
from ctypes.wintypes import *

kernel32 = windll.kernel32

DEBUG_PROCESS = 0x00000001
CREATE_NEW_CONSOLE = 0x00000010

DBG_CONTINUE = 0x00010002

EXCEPTION_DEBUG_EVENT = 1
CREATE_THREAD_DEBUG_EVENT = 2
CREATE_PROCESS_DEBUG_EVENT = 3
EXIT_THREAD_DEBUG_EVENT = 4
EXIT_PROCESS_DEBUG_EVENT = 5
LOAD_DLL_DEBUG_EVENT = 6
UNLOAD_DLL_DEBUG_EVENT = 7

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
        ("hProcess", HANDLE),
        ("hThread",HANDLE),
        ("dwProcessId",DWORD),
        ("dwThreadId", DWORD)
    ]
class DEBUG_EVENT(Structure):
    _fields_ = [
        ("dwDebugEventCode", DWORD),
        ("dwProcessId",DWORD),
        ("dwThreadId",DWORD),
        ("u",c_byte*160)
    ]

class Debugger():
    def __init__(self):
        self.hProcess = None
        self.pid = None
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
            print("Launch Failed ")
            return False

        self.hProcess = pi.hProcess
        self.pid = pi.dwProcessId
        self.active = True

        print (f"Process ID: {self.pid}")
        return True

    def run(self):

        debug_event = DEBUG_EVENT()

        while self.active:
            if kernel32.WaitForDebugEvent(byref(debug_event),1000):

                code = debug_event.dwDebugEventCode


                if code == CREATE_PROCESS_DEBUG_EVENT:
                    print("[+] Process Created Event")

                elif code == CREATE_THREAD_DEBUG_EVENT:
                    print("[+] Thread Created")

                elif code == LOAD_DLL_DEBUG_EVENT:
                    print("[+] DLL Loaded")

                elif code == EXCEPTION_DEBUG_EVENT:
                    print("[!] Exception Event")

                    kernel32.ContinueDebugEvent(
                        debug_event.dwProcessId,
                        debug_event.dwThreadId,
                        0x80010001
                    )


                elif code == EXIT_PROCESS_DEBUG_EVENT:
                    print("[!] Process Exited")
                    self.active = False

                kernel32.ContinueDebugEvent(
                    debug_event.dwProcessId,
                    debug_event.dwThreadId,
                    DBG_CONTINUE
                )

if __name__ == "__main__":
    dbg = Debugger()

    if dbg.load("C:\\Windows\\SysWow64\\notepad.exe"):
        dbg.run()