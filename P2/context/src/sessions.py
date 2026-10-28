"""Inspect this installation's MCP sessions and end an explicitly selected one."""
from __future__ import annotations
from contextlib import contextmanager
import json
import os
from pathlib import Path
import sys
import threading
import time
import uuid
from .runtime import state_directory, codex_status


def _windows_api():
    import ctypes as c
    from ctypes import wintypes as w
    k = c.WinDLL("kernel32", use_last_error=True)
    k.OpenProcess.argtypes = (w.DWORD, w.BOOL, w.DWORD); k.OpenProcess.restype = w.HANDLE
    k.CloseHandle.argtypes = (w.HANDLE,); k.CloseHandle.restype = w.BOOL
    k.QueryFullProcessImageNameW.argtypes = (w.HANDLE, w.DWORD, w.LPWSTR, c.POINTER(w.DWORD)); k.QueryFullProcessImageNameW.restype = w.BOOL
    k.GetProcessTimes.argtypes = (w.HANDLE, c.POINTER(w.FILETIME), c.POINTER(w.FILETIME), c.POINTER(w.FILETIME), c.POINTER(w.FILETIME)); k.GetProcessTimes.restype = w.BOOL
    k.GetExitCodeProcess.argtypes = (w.HANDLE, c.POINTER(w.DWORD)); k.GetExitCodeProcess.restype = w.BOOL
    k.TerminateProcess.argtypes = (w.HANDLE, w.UINT); k.TerminateProcess.restype = w.BOOL
    k.WaitForSingleObject.argtypes = (w.HANDLE, w.DWORD); k.WaitForSingleObject.restype = w.DWORD
    return c, w, k


def _identity(handle, api):
    c, w, k = api
    size = w.DWORD(32768); name = c.create_unicode_buffer(size.value)
    created, exited, kernel, user = (w.FILETIME() for _ in range(4))
    code = w.DWORD()
    if not k.GetExitCodeProcess(handle, c.byref(code)) or code.value != 259:
        return None
    if not k.QueryFullProcessImageNameW(handle, 0, name, c.byref(size)):
        return None
    if not k.GetProcessTimes(handle, c.byref(created), c.byref(exited), c.byref(kernel), c.byref(user)):
        return None
    marker = (created.dwHighDateTime << 32) | created.dwLowDateTime
    return {"program": name.value, "created": str(marker), "started": marker / 10000000 - 11644473600}


def _process_identity(pid):
    if os.name != "nt":
        return {"program": sys.executable, "created": "", "started": time.time()}
    api = _windows_api(); k = api[2]
    handle = k.OpenProcess(0x1000, False, pid)
    if not handle:
        return None
    try:
        return _identity(handle, api)
    finally:
        k.CloseHandle(handle)


def _same_path(a, b):
    return os.path.normcase(os.path.realpath(a)) == os.path.normcase(os.path.realpath(b))


def _programs(application):
    allowed = {os.path.normcase(os.path.realpath(sys.executable))}
    if not getattr(sys, 'frozen', False):
        current = _process_identity(os.getpid())
        if current:allowed.add(os.path.normcase(os.path.realpath(current['program'])))
    if getattr(sys, "frozen", False) and application:
        root = Path(application).resolve().parent / 'tools/mcp'
        try:
            Path(sys.executable).resolve().relative_to(root)
        except ValueError:
            return allowed
        # An update can coexist with the old MCP while its Codex sessions finish.
        for path in [root/'MuseScoreMCP.exe', *root.glob('*/MuseScoreMCP.exe')]:
            if path.is_file():allowed.add(os.path.normcase(os.path.realpath(path)))
    return allowed


def _records():
    result = {}
    for path in state_directory().glob("session-*.json"):
        try:
            value = json.loads(path.read_text("utf8"))
            if value.get("schema") == 1 and isinstance(value.get("pid"), int) and isinstance(value.get("created"), str) and isinstance(value.get("application", ""), str):
                result[(value["pid"], value.get("created"))] = value
        except (OSError, ValueError):
            continue
    return result


def sessions(application=None):
    records = _records(); values = []; allowed = _programs(application)
    if os.name == "nt":
        c, w, k = api = _windows_api()
        class Entry(c.Structure):
            _fields_ = [("size", w.DWORD), ("usage", w.DWORD), ("pid", w.DWORD),
                        ("heap", c.c_size_t), ("module", w.DWORD), ("threads", w.DWORD),
                        ("parent", w.DWORD), ("priority", w.LONG), ("flags", w.DWORD), ("exe", w.WCHAR * 260)]
        k.CreateToolhelp32Snapshot.argtypes = (w.DWORD, w.DWORD); k.CreateToolhelp32Snapshot.restype = w.HANDLE
        k.Process32FirstW.argtypes = (w.HANDLE, c.POINTER(Entry)); k.Process32FirstW.restype = w.BOOL
        k.Process32NextW.argtypes = (w.HANDLE, c.POINTER(Entry)); k.Process32NextW.restype = w.BOOL
        snapshot = k.CreateToolhelp32Snapshot(2, 0)
        if snapshot == c.c_void_p(-1).value:
            raise OSError("无法读取当前 MCP 进程，请重新刷新。")
        try:
            row = Entry(); row.size = c.sizeof(row)
            more = k.Process32FirstW(snapshot, c.byref(row))
            while more:
                if row.pid != os.getpid() and (any(key[0] == row.pid for key in records) or (getattr(sys, "frozen", False) and row.exe.lower() == Path(sys.executable).name.lower())):
                    value = _process_identity(row.pid)
                    if value and os.path.normcase(os.path.realpath(value["program"])) in allowed:
                        record = records.get((row.pid, value["created"]), {})
                        if not record or not application or not record.get("application") or _same_path(record["application"], application):
                            values.append(dict(record, **value, pid=row.pid, parent=row.parent,
                                               token=f'{row.pid}:{value["created"]}', known=bool(record)))
                more = k.Process32NextW(snapshot, c.byref(row))
        finally:
            k.CloseHandle(snapshot)
    values.sort(key=lambda v: v["started"])
    return {"ok": True, "sessions": values, "codex": codex_status()}


def end_session(token, application=None):
    if os.name != "nt":
        raise RuntimeError("此平台请从 Codex 结束对应的 MCP 连接。")
    try:
        pid_text, created = token.split(":", 1); pid = int(pid_text)
    except (ValueError, AttributeError):
        raise RuntimeError("请刷新列表，再选择需要结束的连接。") from None
    if pid <= 0 or pid == os.getpid():
        raise RuntimeError("请在列表中选择另一个 MCP 连接。")
    api = _windows_api(); k = api[2]
    handle = k.OpenProcess(0x1000 | 0x1 | 0x100000, False, pid)
    if not handle:
        raise RuntimeError("该连接已退出或无法访问，请刷新列表。")
    try:
        identity = _identity(handle, api)
        if not identity or identity["created"] != created or os.path.normcase(os.path.realpath(identity["program"])) not in _programs(application):
            raise RuntimeError("该连接已经变化，请刷新列表。")
        record = _records().get((pid, created), {})
        # Source mode shares python.exe with unrelated tools: require our own record.
        if not getattr(sys, "frozen", False) and (record.get("created") != created or record.get("kind") != "musescore-stdio"):
            raise RuntimeError("该进程未登记为 MuseScore MCP 连接。")
        if record.get("created") == created:
            if application and record.get("application") and not _same_path(record["application"], application):
                raise RuntimeError("该连接正在使用另一份 MuseScore 程序。")
            if record.get("active", 0):
                raise RuntimeError("该连接正在处理任务，请等任务结束后再操作。")
        if not k.TerminateProcess(handle, 0) or k.WaitForSingleObject(handle, 5000) != 0:
            raise RuntimeError("连接尚未结束，请重新刷新查看。")
        for path in state_directory().glob("session-*.json"):
            try:
                value = json.loads(path.read_text('utf8'))
                if value.get('pid') == pid and value.get('created') == created:
                    path.unlink(missing_ok=True)
            except (OSError, ValueError):
                continue
    finally:
        k.CloseHandle(handle)
    return dict(sessions(application), message="已结束所选 MCP 连接。需要继续使用时，在 Codex 重新连接。")


class ClientSession:
    def __init__(self, application):
        self.application = str(Path(application).resolve()) if application else ""
        self.id = uuid.uuid4().hex
        self.path = state_directory() / f"session-{self.id}.json"
        self.value = dict(_process_identity(os.getpid()) or {}, schema=1, kind="musescore-stdio",
                          id=self.id, pid=os.getpid(), parent=os.getppid(), application=self.application,
                          active=0, requests=0, phase="starting", lastRequest=0)
        self._lock = threading.Lock()

    def _save(self):
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            temporary = self.path.with_suffix('.tmp')
            temporary.write_text(json.dumps(self.value, ensure_ascii=False), encoding="utf8")
            os.replace(temporary, self.path)
        except OSError as error:
            print(f"MuseScore MCP: {error}", file=sys.stderr)

    def __enter__(self):
        self._save()
        return self

    def __exit__(self, *args):
        try:
            self.path.unlink(missing_ok=True)
        except OSError as error:
            print(f"MuseScore MCP: {error}", file=sys.stderr)

    @contextmanager
    def request(self, method):
        with self._lock:
            self.value.update(active=self.value['active'] + 1, requests=self.value['requests'] + 1,
                              phase="working", method=method, lastRequest=time.time())
            self._save()
        try:
            yield
        finally:
            with self._lock:
                self.value.update(active=self.value['active'] - 1, phase="waiting", lastRequest=time.time())
                self._save()

    def middleware(self):
        from fastmcp.server.middleware import Middleware
        session = self
        class Activity(Middleware):
            async def on_request(self, context, call_next):
                if context.source != "client":
                    return await call_next(context)
                with session.request(context.method):
                    return await call_next(context)
        return Activity()
