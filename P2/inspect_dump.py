"""Read a Windows minidump and resolve its stack with local PDB files."""
from pathlib import Path
import ctypes as c
from ctypes import wintypes as w
import struct
import sys

b = Path(sys.argv[1]).read_bytes()
count, directory = struct.unpack_from("<II", b, 8)
streams = {struct.unpack_from("<I", b, directory+i*12)[0]: struct.unpack_from("<II", b, directory+i*12+4)
           for i in range(count)}
exception = streams[6][1]
tid = struct.unpack_from("<I", b, exception)[0]
context = struct.unpack_from("<I", b, exception+164)[0]
rsp, rip = struct.unpack_from("<Q", b, context+152)[0], struct.unpack_from("<Q", b, context+248)[0]
modules = []
location = streams[4][1]
for i in range(struct.unpack_from("<I", b, location)[0]):
    at = location+4+i*108
    base, size = struct.unpack_from("<QI", b, at)
    name_at = struct.unpack_from("<I", b, at+20)[0]
    length = struct.unpack_from("<I", b, name_at)[0]
    modules.append((base, size, b[name_at+4:name_at+4+length].decode("utf-16-le")))
dbg = c.WinDLL("dbghelp", use_last_error=True)
process = c.c_void_p(-1)
dbg.SymInitializeW.argtypes = [w.HANDLE, w.LPCWSTR, w.BOOL]
dbg.SymInitializeW(process, str(Path("../muse3_dev/MuseScore/msvc.build_harmony_release_x64/main/Release").resolve()), False)
dbg.SymLoadModuleExW.argtypes = [w.HANDLE, w.HANDLE, w.LPCWSTR, w.LPCWSTR, c.c_uint64, w.DWORD, c.c_void_p, w.DWORD]
dbg.SymLoadModuleExW.restype = c.c_uint64
for base, size, name in modules:
    if Path(name).name in ("MuseScore3Evo.exe", "Qt5Widgets.dll", "Qt5Core.dll", "Qt5Qml.dll"):
        dbg.SymLoadModuleExW(process, None, name, None, base, size, None, 0)

class Symbol(c.Structure):
    _fields_ = [("size", w.ULONG), ("type", w.ULONG), ("reserved", c.c_uint64*2),
                ("index", w.ULONG), ("length", w.ULONG), ("base", c.c_uint64), ("flags", w.ULONG),
                ("value", c.c_uint64), ("address", c.c_uint64), ("register", w.ULONG), ("scope", w.ULONG),
                ("tag", w.ULONG), ("name_length", w.ULONG), ("maximum", w.ULONG), ("name", w.WCHAR*512)]
dbg.SymFromAddrW.argtypes = [w.HANDLE, c.c_uint64, c.POINTER(c.c_uint64), c.POINTER(Symbol)]
def describe(address):
    module = next((m for m in modules if m[0] <= address < m[0]+m[1]), None)
    if not module:
        return None
    result = Path(module[2]).name + "+" + hex(address-module[0])
    symbol = Symbol(); symbol.size = 88; symbol.maximum = 512; displacement = c.c_uint64()
    if dbg.SymFromAddrW(process, address, c.byref(displacement), c.byref(symbol)):
        result += " " + symbol.name + "+" + hex(displacement.value)
    return result
print("Exception:", describe(rip))
threads = streams[3][1]
for i in range(struct.unpack_from("<I", b, threads)[0]):
    at = threads+4+i*48
    if struct.unpack_from("<I", b, at)[0] != tid:
        continue
    start, size, data = struct.unpack_from("<QII", b, at+24)
    offset = rsp-start
    for delta in range(0, min(size-offset, 16384), 8):
        address = struct.unpack_from("<Q", b, data+offset+delta)[0]
        name = describe(address)
        if name:
            print(hex(delta), name)
