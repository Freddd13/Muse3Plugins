"""Launch the frozen server with Python removed from PATH and use its real stdio transport."""
import asyncio
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent / "mcp-musescore"
sys.path[:0] = [str(REPO), str(REPO / "tests")]
from fastmcp import Client
from mock_musescore import running_mock, demo_score


async def main():
    output = ROOT / "out/package-check-063"
    output.mkdir(parents=True, exist_ok=True)
    folder = output / "曲谱 程序" / "bin"
    folder.mkdir(parents=True, exist_ok=True)
    application = folder / "MuseScore3Evo.exe"
    application.write_bytes(b"test application identity")
    (folder / "kumo.ini").write_text("[features]\nenable_exp_feature=true\n", encoding="utf8")
    state = output / "state"; state.mkdir(exist_ok=True)
    executable = ROOT / "out/mcp-dist/MuseScoreMCP/MuseScoreMCP.exe"
    windows = os.environ.get("SystemRoot", "C:/Windows")
    environment = dict(os.environ, PATH=windows + ";" + windows + "/System32", PYTHONPATH="",
                       MCP_MUSESCORE_STATE_DIR=str(state), CODEX_HOME=str(output / "codex"))
    async with running_mock(demo_score()) as mock:
        value = {"schema": 1, "id": "package-test", "pid": os.getpid(), "port": int(mock.uri.rsplit(":", 1)[1]),
                 "application": str(application), "host": "127.0.0.1", "score": "演示乐谱"}
        (state / "instance-package-test.json").write_text(json.dumps(value), encoding="utf8")
        process = await asyncio.create_subprocess_exec(str(executable), "--diagnose", "--application", str(application),
            env=environment, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await process.communicate()
        if process.returncode:
            raise RuntimeError(stdout.decode("utf8", "replace") + stderr.decode("utf8", "replace"))
        diagnosis = json.loads(stdout.decode("utf8")); assert diagnosis["ok"], diagnosis
        async with Client({"mcpServers": {"musescore": {"command": str(executable),
                "args": ["--stdio", "--application", str(application)], "env": environment}}}) as client:
            names = [t.name for t in await client.list_tools()]
            assert len(names) == 40, names
            ping = await client.call_tool("ping_musescore", {})
            assert "pong" in str(ping)
            score = await client.call_tool("get_score_data", {"first_measure": 1, "last_measure": 1})
            assert score.data["measures"][0]["measure"] == 1
        registration = subprocess.run([str(executable), "--register-codex", "--application", str(application)],
            env=environment, capture_output=True, timeout=20, encoding="utf8")
        assert registration.returncode == 0, registration.stdout + registration.stderr
        assert json.loads(registration.stdout)["ok"]
        import tomllib
        config = tomllib.loads((output / "codex/config.toml").read_text("utf8"))
        assert Path(config["mcp_servers"]["musescore"]["command"]) == executable
        (folder / "kumo.ini").write_text("[features]\nenable_exp_feature=false\n", encoding="utf8")
        async with Client({"mcpServers": {"musescore": {"command": str(executable),
                "args": ["--stdio", "--application", str(application)], "env": environment}}}) as client:
            tools = [t.name for t in await client.list_tools()]
            assert tools == ["get_connection_status"], tools
            status = await client.call_tool("get_connection_status", {})
            assert status.data["enabled"] is False
        report = {"toolCount": len(names), "diagnosis": diagnosis, "frozenStdioRead": True,
                  "pythonRemovedFromPath": True, "unicodeApplicationPath": True, "registration": True,
                  "disabledConfigurationHidesMusicTools": True}
        (output / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf8")
        print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
