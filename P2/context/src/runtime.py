"""Installed MuseScore discovery and the configuration shared with its native panel."""
from __future__ import annotations
import configparser
import json
import os
from pathlib import Path
import sys
import time


def state_directory() -> Path:
    override = os.environ.get("MCP_MUSESCORE_STATE_DIR")
    if override:
        return Path(override)
    base = Path(os.environ.get("LOCALAPPDATA", Path.home() / ".local/share"))
    return base / "Freddd13" / "MuseScoreMCP"


def configuration_path(application: str | None = None) -> Path:
    if application:
        return Path(application).resolve().parent / "kumo.ini"
    # tools/mcp/MuseScoreMCP.exe -> bin/kumo.ini
    return Path(sys.executable).resolve().parents[2] / "kumo.ini"


def enabled(path: Path) -> bool:
    parser = configparser.ConfigParser(interpolation=None)
    try:
        parser.read_string(path.read_text("utf-8-sig"))
        return parser.get("features", "enable_exp_feature").strip().lower() == "true"
    except (OSError, ValueError, configparser.Error):
        return False


def process_running(pid: int) -> bool:
    if pid <= 0:
        return False
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
        kernel.OpenProcess.restype = wintypes.HANDLE
        kernel.GetExitCodeProcess.argtypes = (wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD))
        kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
        handle = kernel.OpenProcess(0x1000, False, pid)
        if not handle:
            return False
        code = wintypes.DWORD()
        try:
            return bool(kernel.GetExitCodeProcess(handle, ctypes.byref(code))) and code.value == 259
        finally:
            kernel.CloseHandle(handle)
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def instances(application: str | None = None) -> list[dict]:
    result = []
    for path in state_directory().glob("instance-*.json"):
        try:
            value = json.loads(path.read_text("utf-8"))
            if value.get("schema") != 1 or not process_running(int(value["pid"])):
                continue
            if not 1 <= int(value["port"]) <= 65535 or value.get("host") != "127.0.0.1":
                continue
            exe = Path(value["application"]).resolve()
            if application and os.path.normcase(str(exe)) != os.path.normcase(str(Path(application).resolve())):
                continue
            if not enabled(exe.parent / "kumo.ini"):
                continue
            result.append(value)
        except (OSError, KeyError, ValueError, TypeError):
            continue
    return sorted(result, key=lambda v: (bool(v.get("active")), v.get("updated", 0)), reverse=True)


def selected_instance(application: str | None = None) -> dict:
    available = instances(application)
    try:
        selection = json.loads((state_directory() / "selection.json").read_text("utf-8"))
    except (OSError, ValueError):
        selection = {}
    chosen = next((v for v in available if v["id"] == selection.get("id")), None)
    if chosen:
        return chosen
    if len(available) == 1:
        return available[0]
    if len(available) > 1:
        raise RuntimeError("打开了多个 MuseScore 窗口，请在“AI 连接”中选择本次使用的窗口。")
    raise RuntimeError("请打开 MuseScore，并在“AI 连接”中检查扩展功能和连接状态。")


def installed_connection(application: str | None = None) -> tuple[str, int]:
    config = configuration_path(application)
    if not enabled(config):
        raise RuntimeError(f"个人扩展功能已关闭。开启 {config} 中的 enable_exp_feature 后重启 MuseScore。")
    value = selected_instance(application)
    return "127.0.0.1", int(value["port"])


def codex_configuration() -> Path:
    return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "config.toml"


def register_codex(application: str | None = None) -> dict:
    import tomlkit
    import tempfile
    import uuid
    config = codex_configuration()
    old = config.read_bytes() if config.exists() else b""
    document = tomlkit.parse(old.decode("utf-8-sig")) if old else tomlkit.document()
    servers = document.setdefault("mcp_servers", tomlkit.table())
    server = servers.setdefault("musescore", tomlkit.table())
    arguments = ([] if getattr(sys, "frozen", False) else [str(Path(__file__).resolve().parents[1] / "launcher.py")]) + ["--stdio"]
    if application:
        arguments += ["--application", str(Path(application).resolve())]
    # Only this server's launch fields change. Other tables and comments remain.
    server["command"] = str(Path(sys.executable).resolve())
    server["args"] = arguments
    for key in ("url", "auth", "bearer_token_env_var", "http_headers", "env_http_headers"):
        if key in server:
            del server[key]
    server["enabled"] = True
    server["startup_timeout_sec"] = 20
    server["tool_timeout_sec"] = 60
    config.parent.mkdir(parents=True, exist_ok=True)
    backup = None
    if old:
        backup = config.with_name(config.name + ".musescore-" + time.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:8] + ".bak")
        with backup.open("xb") as file:
            file.write(old)
    fd, temporary = tempfile.mkstemp(prefix=".musescore-", suffix=".toml", dir=config.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as file:
            file.write(tomlkit.dumps(document))
            file.flush()
            os.fsync(file.fileno())
        os.replace(temporary, config)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise
    return {"ok": True, "configuration": str(config), "backup": str(backup) if backup else "",
            "message": "已配置 MuseScore。重新连接 Codex 或新建对话后，可以读取当前乐谱。"}
