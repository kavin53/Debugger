from ctypes import *
from ctypes.wintypes import *

kernel32 = windll.kernel32

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

class PROCESSINFO(Structure):
    _fields_ = [
        ("hProcess", HANDLE),
        ("hThread", HANDLE),
        ("dwProcessId",DWORD),
        ("dwThreadId",DWORD)
    ]

class DEBUG_EVENT(Structure):
    _fields_ = [
        ("dwDebugEventCode", DWORD),
        ("dwProcessId", DWORD),
        ("dwThreadId", DWORD),
        ("u", c_byte * 160),
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

class Debugger:

    def __init__(self):
        self.hProcess = None
        self.hThread = None
        self.base_address = None
        self.breakpoints = {}

    def load(self,path):

        si = STARTUPINFO()
        si.cb = sizeof(si)

        pi = PROCESSINFO()

        success = kernel32.CreateProcessA(
            path.encode(),
            None,
            None,
            None,
            False,
            0x00000001,
            None,
            None,
            byref(si),
            byref(pi),
        )

        if not success:
            print("Launch failed")
            return False

        self.hProcess = pi.hProcess
        self.hThread = pi.hThread
        self.pid = pi.dwProcessId

        print(f"pid: {self.pid}")
        return True

    def read_memory(self,address,size):
        buffer = create_string_buffer(size)
        bytes_read = c_size_t(0)

        kernel32.ReadProcessMemory(
            self.hProcess,
            c_void_p(address),
            buffer,
            size,
            byref(bytes_read),
        )
        return buffer.raw

    def WriteProcessMemory(self,address, data):
        count = c_size_t(0)

        kernel32.WriteProcessMemory(
            self.hProcess,
            c_void_p(address),
            data,
            len(data),
            byref(count),
        )

    def set_breakpoint(self,address):
        original = self.read_memory(address,1)
        self.breakpoints[address] = original
        self.WriteProcessMemory(address, b'\xCC')

        print(f"Breakpoint at : {hex(address)}")

    def run(self):
        debug_event = DEBUG_EVENT()

        while True:
            if kernel32.WaitForDebugEvent(byref(debug_event),1000):
                code = debug_event.dwDebugEventCode

                if code == 3:
                    print("process created")
                    info = cast(
                        debug_event.u,
                        POINTER(CREATE_PROCESS_DEBUG_INFO)
                    ).contents

                    self.base_address = info.lpBaseOfImage
                    print(f"base_address : {hex(self.base_address)}")

                    bp_address = self.base_address + 0x1000
                    self.set_breakpoint(bp_address)

                    continue_status = 0x00010002

                elif code == 1:

                    exception_code = cast(
                        debug_event.u,
                        POINTER(DWORD)
                    )[0]

                    if exception_code == 0x80000003:
                        print("[🔥] Breakpoint hit")
                        continue_status = 0x00010002
                    else:
                        continue_status = 0x80010001

                elif code == 5:
                    print("process exited")
                    break

                else:
                    continue_status = 0x00010002

                kernel32.ContinueDebugEvent(
                    debug_event.dwProcessId,
                    debug_event.dwThreadId,
                    continue_status
                )

if __name__ == "__main__":

        dbg = Debugger()

        if dbg.load("C:\\Windows\\System32\\notepad.exe"):
                dbg.run()