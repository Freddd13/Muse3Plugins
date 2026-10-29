"""The installed MCP executable. stdout is reserved for its chosen protocol."""
from __future__ import annotations
import argparse
import asyncio
import json
import os
import sys
os.environ.setdefault("FASTMCP_CHECK_FOR_UPDATES", "off")


def main() -> None:
    parser = argparse.ArgumentParser(description="MuseScore 与 Codex 的本机连接")
    from src.version import VERSION
    parser.add_argument("--version", action="version", version="MuseScoreMCP " + VERSION)
    parser.add_argument("--stdio", action="store_true")
    parser.add_argument("--diagnose", action="store_true")
    parser.add_argument("--register-codex", action="store_true")
    parser.add_argument("--enable-codex", action="store_true")
    parser.add_argument("--disable-codex", action="store_true")
    parser.add_argument("--sessions", action="store_true")
    parser.add_argument("--end-session")
    parser.add_argument("--application", help="要连接的 MuseScore 程序路径")
    options = parser.parse_args()
    from src.runtime import configuration_path, enabled, instances, installed_connection, register_codex, set_codex_enabled
    try:
        if options.sessions or options.end_session:
            from src.sessions import sessions, end_session
            value = end_session(options.end_session, options.application) if options.end_session else sessions(options.application)
            print(json.dumps(value, ensure_ascii=False))
        elif options.enable_codex or options.disable_codex:
            print(json.dumps(set_codex_enabled(options.enable_codex), ensure_ascii=False))
        elif options.register_codex:
            print(json.dumps(register_codex(options.application), ensure_ascii=False))
        elif options.diagnose or not options.stdio:
            config = configuration_path(options.application)
            result = {"configuration": str(config), "enabled": enabled(config),
                      "instances": instances(options.application)}
            if result["enabled"] and result["instances"]:
                from src.client import MuseScoreClient
                host, port = installed_connection(options.application)
                async def ping():
                    client = MuseScoreClient(host, port, timeout=5)
                    try:
                        reply = await client.send_command("ping")
                        value = {"connection": reply}
                        if reply.get("result") == "pong":
                            identity = await client.send_command("getScoreIdentity")
                            body = identity.get("result", identity)
                            if isinstance(body, dict) and "hasScore" in body:
                                value["identity"] = body
                        return value
                    finally:
                        await client.close()
                result.update(asyncio.run(ping()))
                result["ok"] = result["connection"].get("result") == "pong"
                if result["ok"] and "identity" in result:
                    identity = result["identity"]
                    result["message"] = ("已连接：" + identity["displayTitle"] +
                        (" · 总谱" if identity.get("isMaster") else " · 分谱：" + identity.get("partName", ""))) if identity.get("hasScore") else "连接成功，打开乐谱即可读取。"
            else:
                result["ok"] = False
                result["error"] = "个人扩展功能已关闭，请检查程序旁的 kumo.ini。" if not result["enabled"] else "请打开 MuseScore，在 AI 连接中检查当前窗口。"
            print(json.dumps(result, ensure_ascii=False))
        else:
            from src.sessions import ClientSession
            config = configuration_path(options.application)
            if not enabled(config):
                from fastmcp import FastMCP
                disabled = FastMCP("MuseScore", instructions="个人扩展功能已关闭。需要使用时，在程序旁 kumo.ini 中开启 enable_exp_feature，再重启程序并重新连接。")
                @disabled.tool
                def get_connection_status() -> dict:
                    """查看 MuseScore 扩展开关和配置文件位置。"""
                    return {"enabled": False, "configuration": str(config), "message": "个人扩展功能已关闭。"}
                with ClientSession(options.application) as session:
                    disabled.add_middleware(session.middleware())
                    disabled.run(show_banner=False)
                return
            import server
            server.client.connection_resolver = lambda: installed_connection(options.application)
            with ClientSession(options.application) as session:
                server.mcp.add_middleware(session.middleware())
                server.mcp.run(show_banner=False)
    except Exception as error:
        if options.stdio:
            raise
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False))
        raise SystemExit(1)


if __name__ == "__main__":
    if sys.platform == "win32":
        for stream in (sys.stdout, sys.stderr):
            if stream is not None and hasattr(stream, "reconfigure"):
                stream.reconfigure(encoding="utf-8")
    main()
