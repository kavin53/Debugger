from ctypes import *
from ctypes.wintypes import *

kernel32 = windll.kernel32

class MEMORY_BASIC_INFORMATION(Structure):
    _fields_ = [
        ("BaseAddress", c_void_p),
        ("AllocationBase", c_void_p),
        ("AllocationProtect", DWORD),
        ("RegionSize", c_size_t),
        ("State", DWORD),
        ("Protect", DWORD),
        ("Type", DWORD),
    ]

class Debugger:

    def __init__(self):
        self.hProcess = None

    def attach(self, pid):
        PROCESS_ALL_ACCESS = 0x1F0FFF
        self.hProcess = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
        return True

    def read_memory(self, address, size):
        buffer = create_string_buffer(size)
        bytes_read = c_size_t(0)
        kernel32.ReadProcessMemory(
            self.hProcess,
            c_void_p(address),
            buffer,
            size,
            byref(bytes_read)
        )
        return buffer.raw

    def scan_memory(self, value):
        address = 0
        mbi = MEMORY_BASIC_INFORMATION()
        search = value.to_bytes(4, 'little')

        while kernel32.VirtualQueryEx(
            self.hProcess,
            c_void_p(address),
            byref(mbi),
            sizeof(mbi)
        ):
            if mbi.State == 0x1000:
                if mbi.Protect in (0x04, 0x20):
                    try:
                        buffer = self.read_memory(mbi.BaseAddress, mbi.RegionSize)
                        offset = buffer.find(search)
                        if offset != -1:
                            found_address = mbi.BaseAddress + offset
                            print(hex(found_address))
                    except:
                        pass

            address += mbi.RegionSize

if __name__ == "__main__":
    dbg = Debugger()
    pid = int(input("PID: "))
    if dbg.attach(pid):
        value = int(input("Value: "))
        dbg.scan_memory(value)