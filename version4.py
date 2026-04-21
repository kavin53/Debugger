from ctypes import *
from ctypes.wintypes import *

kernel32 = windll.kernel32

DEBUG_PROCESS = 0x00000001
CREATE_NEW_CONSOLE = 0x00000010

DBG_CONTINUE = 0x00010002
DBG_EXCEPTION_NOT_HANDLED = 0x80010001

EXCEPTION_DEBUG_EVENT =1
CREATE_PROCESS_DEBUG_EVENT = 3
EXIT_PROCESS_DEBUG_EVENT = 5

EXCEPTION_BREAKPOINT = 0x80000003

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
        ("hProcess" , HANDLE),
        ("hThread",HANDLE),
        ("dwProcessId", DWORD),
        ("dwThreadId" , DWORD),
    ]

class DEBUG_EVENT(Structure):
    _fields_ = [
        ("dwDebugEventCode", DWORD),
        ("dwProcessId", DWORD),
        ("dwThreadId", DWORD),
        ("u", c_byte * 160),
    ]

class CREATE_PROCESS_DEBUG_INFO(Structure):
    _pack_ = 1
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

class Debugger:
    def __init__(self):
        self.hProcess = None
        self.pid = None
        self.base_address = None
        self.breakpoints = {}

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
            DEBUG_PROCESS | CREATE_NEW_CONSOLE ,
            None,
            None,
            byref(si),
            byref(pi)
        )

        if not success:
            err = kernel32.GetLastError()
            print("Failed to Launch : {err}")
            return False

        self.hProcess = pi.hProcess
        self.pid = pi.dwProcessId

        print(f"PID: {self.pid}")
        return True


    def read_memory(self,address,size):
        buffer = create_string_buffer(size)
        count = c_size_t(0)

        kernel32.ReadProcessMemory(
            self.hProcess,
            address,
            buffer,
            size,
            byref(count)
        )
        return buffer.raw

    def write_memory(self,address,data):
        count = c_size_t(0)

        kernel32.WriteProcessMemory(
            self.hProcess,
            address,
            data,
            len(data),
            byref(count)
        )

    def set_breakpoint(self , address):
        original = self.read_memory(address,1)
        self.breakpoints[address] = original

        self.write_memory(address, b'\xCC')
        print(f"Breakpoint Address: {address}")

    def run(self):
        debug_event = DEBUG_EVENT()

        while True:
            if kernel32.WaitForDebugEvent(byref(debug_event),1000):
                code = debug_event.dwDebugEventCode

                if code == CREATE_PROCESS_DEBUG_EVENT:
                    print("process created")

                    info = cast(
                        debug_event.u,
                        POINTER(CREATE_PROCESS_DEBUG_INFO)
                    ).contents

                    self.base_address = info.lpBaseOfImage

                    print(f"Base Address: {hex(self.base_address)}")

                   # bp_address = self.base_address + 0x1000
                   # self.set_breakpoint(bp_address)

                    continue_status = DBG_CONTINUE

                elif code ==EXCEPTION_DEBUG_EVENT:
                    exception_code = cast(
                        debug_event.u,
                        POINTER(DWORD)
                    )[0]

                    if exception_code == EXCEPTION_BREAKPOINT:
                        print("Breakpoint hit")
                        continue_status = DBG_CONTINUE
                    else:
                        continue_status = DBG_EXCEPTION_NOT_HANDLED

                elif code == EXIT_PROCESS_DEBUG_EVENT:
                    print("process exited")
                    break

                else:
                    continue_status = DBG_CONTINUE

                kernel32.ContinueDebugEvent(
                    debug_event.dwProcessId,
                    debug_event.dwThreadId,
                    continue_status
                )

if __name__ == "__main__":
    dbg = Debugger()

    if dbg.load('C:\\Windows\\SysWow64\\notepad.exe'):
        dbg.run()