"""Installed configuration, process discovery and non-destructive registration."""
import json
import os
from pathlib import Path
import sys
import tomllib

from src import runtime
import pytest


def installation(tmp_path, value="true"):
    app = tmp_path / "曲谱 程序" / "bin" / "MuseScore3Evo.exe"
    app.parent.mkdir(parents=True, exist_ok=True)
    app.write_bytes(b"test")
    (app.parent / "kumo.ini").write_text("[features]\nenable_exp_feature=" + value, encoding="utf8")
    return app


def test_gate_requires_explicit_true(tmp_path):
    app = installation(tmp_path)
    assert runtime.enabled(app.parent / "kumo.ini")
    for value in ("false", "yes", "", "broken"):
        (app.parent / "kumo.ini").write_text("[features]\nenable_exp_feature=" + value)
        assert not runtime.enabled(app.parent / "kumo.ini")
    assert not runtime.enabled(tmp_path / "missing.ini")


def test_discovery_filters_dead_disabled_and_other_installations(tmp_path, monkeypatch):
    state = tmp_path / "state"; state.mkdir()
    monkeypatch.setenv("MCP_MUSESCORE_STATE_DIR", str(state))
    app = installation(tmp_path)
    value = {"schema": 1, "id": "one", "pid": os.getpid(), "port": 8765,
             "application": str(app), "host": "127.0.0.1", "updated": 1}
    (state / "instance-one.json").write_text(json.dumps(value))
    assert runtime.selected_instance(str(app))["id"] == "one"
    assert runtime.installed_connection(str(app)) == ("127.0.0.1", 8765)
    (state / "instance-dead.json").write_text(json.dumps(dict(value, id="dead", pid=0)))
    assert len(runtime.instances()) == 1
    (app.parent / "kumo.ini").write_text("[features]\nenable_exp_feature=false")
    assert runtime.instances() == []


def test_explicit_instance_selection(tmp_path, monkeypatch):
    state = tmp_path / "state"; state.mkdir()
    monkeypatch.setenv("MCP_MUSESCORE_STATE_DIR", str(state))
    app = installation(tmp_path)
    for name, port in (("one", 8765), ("two", 8766)):
        value = {"schema": 1, "id": name, "pid": os.getpid(), "port": port,
                 "application": str(app), "host": "127.0.0.1"}
        (state / ("instance-" + name + ".json")).write_text(json.dumps(value))
    import pytest
    with pytest.raises(RuntimeError, match="多个"):
        runtime.selected_instance(str(app))
    (state / "selection.json").write_text(json.dumps({"id": "two"}))
    assert runtime.installed_connection(str(app))[1] == 8766


def test_registration_preserves_other_configuration_and_backup(tmp_path, monkeypatch):
    monkeypatch.setenv("CODEX_HOME", str(tmp_path))
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    original = '# 我的设置\nmodel="example"\n[mcp_servers.other]\ncommand="keep"\n'
    (tmp_path / "config.toml").write_text(original, encoding="utf8")
    first = runtime.register_codex(str(installation(tmp_path)))
    assert Path(first["backup"]).read_text("utf8") == original
    content = (tmp_path / "config.toml").read_text("utf8")
    assert content.startswith('# 我的设置')
    document = tomllib.loads(content)
    assert document["model"] == "example"
    assert document["mcp_servers"]["other"]["command"] == "keep"
    assert document["mcp_servers"]["musescore"]["args"][0] == "--stdio"
    second = runtime.register_codex(str(installation(tmp_path)))
    assert second["backup"] != first["backup"]


def test_connected_client_follows_window_selection():
    import asyncio
    asyncio.run(check_window_selection())


async def check_window_selection():
    from mock_musescore import running_mock, demo_score
    from src.client import MuseScoreClient
    async with running_mock(demo_score()) as first, running_mock(demo_score()) as second:
        port = int(first.uri.rsplit(":", 1)[1])
        client = MuseScoreClient()
        client.connection_resolver = lambda: ("127.0.0.1", port)
        try:
            assert (await client.send_command("ping"))["result"] == "pong"
            first_socket = client.websocket
            port = int(second.uri.rsplit(":", 1)[1])
            assert (await client.send_command("ping"))["result"] == "pong"
            assert client.uri == second.uri
            assert client.websocket is not first_socket
        finally:
            await client.close()
