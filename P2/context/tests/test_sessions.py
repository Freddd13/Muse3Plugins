"""MCP process controls exercise only subprocesses created by each test."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import pytest
from src import sessions, runtime


def test_codex_switch_preserves_launch_fields_and_other_settings(tmp_path, monkeypatch):
    monkeypatch.setenv('CODEX_HOME', str(tmp_path))
    config = tmp_path / 'config.toml'
    original = '# 我的设置\n[mcp_servers.other]\ncommand="keep"\n[mcp_servers.musescore]\ncommand="mcp.exe"\nargs=["--stdio"]\n'
    config.write_text(original, 'utf8')
    assert runtime.codex_status()['enabled']
    off = runtime.set_codex_enabled(False)
    assert Path(off['backup']).read_text('utf8') == original
    assert not runtime.codex_status()['enabled']
    import tomllib
    changed = tomllib.loads(config.read_text('utf8'))
    assert changed['mcp_servers']['other']['command'] == 'keep'
    assert changed['mcp_servers']['musescore']['args'] == ['--stdio']
    off_bytes = config.read_bytes()
    assert 'backup' not in runtime.set_codex_enabled(False)
    assert config.read_bytes() == off_bytes
    assert runtime.set_codex_enabled(True)['codex']['enabled']
    runtime.set_codex_enabled(False)
    assert not runtime.register_codex('updated.exe')['codex']['enabled']
    config.write_text('[broken', 'utf8'); before = config.read_bytes()
    with pytest.raises(Exception):runtime.set_codex_enabled(False)
    assert config.read_bytes() == before


def test_missing_codex_registration_is_clear(tmp_path, monkeypatch):
    monkeypatch.setenv('CODEX_HOME', str(tmp_path))
    assert not runtime.codex_status()['configured']
    with pytest.raises(RuntimeError, match='先点击'):runtime.set_codex_enabled(True)
    assert not (tmp_path / 'config.toml').exists()


def test_versioned_package_keeps_program_configuration(tmp_path, monkeypatch):
    for folder in ('tools/mcp', 'tools/mcp/2.4.0'):
        monkeypatch.setattr(sys, 'executable', str(tmp_path/'bin'/folder/'MuseScoreMCP.exe'))
        assert runtime.configuration_path()==tmp_path/'bin/kumo.ini'


@pytest.mark.skipif(os.name != 'nt', reason='Windows installed process control')
@pytest.mark.parametrize('busy', [False, True])
def test_only_selected_process_can_end(tmp_path, monkeypatch, busy):
    monkeypatch.setenv('MCP_MUSESCORE_STATE_DIR', str(tmp_path/'state'))
    monkeypatch.setenv('CODEX_HOME', str(tmp_path/'codex'))
    app = str(tmp_path/'乐谱 程序.exe')
    source = ('from src.sessions import ClientSession\nimport time,sys\n'
              'with ClientSession(sys.argv[1]) as session:\n' +
              (' with session.request("tools/call"):\n  time.sleep(60)\n' if busy else ' time.sleep(60)\n'))
    interpreter=sessions._process_identity(os.getpid())['program']
    process = subprocess.Popen([interpreter, '-c', source, app], cwd=Path(__file__).resolve().parents[1], creationflags=0x08000000)
    try:
        deadline=time.monotonic()+8; row=None
        while time.monotonic()<deadline:
            row=next((r for r in sessions.sessions(app)['sessions'] if r['pid']==process.pid), None)
            if row and (not busy or row.get('active')):break
            time.sleep(.05)
        assert row and row['known']
        assert row['parent']==os.getpid()
        with pytest.raises(RuntimeError, match='已经变化'):
            sessions.end_session(f"{process.pid}:{int(row['created'])+1}", app)
        with pytest.raises(RuntimeError, match='另一份'):
            sessions.end_session(row['token'], str(tmp_path/'different.exe'))
        assert process.poll() is None
        if busy:
            with pytest.raises(RuntimeError, match='正在处理'):sessions.end_session(row['token'], app)
            assert process.poll() is None
        else:
            result=sessions.end_session(row['token'], app)
            assert result['ok'] and process.wait(timeout=3)==0
            assert not any(r['pid']==process.pid for r in result['sessions'])
    finally:
        if process.poll() is None:process.kill();process.wait(timeout=5)


def test_activity_records_and_cleanup(tmp_path, monkeypatch):
    monkeypatch.setenv('MCP_MUSESCORE_STATE_DIR', str(tmp_path))
    with sessions.ClientSession('example.exe') as session:
        assert json.loads(session.path.read_text('utf8'))['active']==0
        with session.request('tools/call'):
            record=json.loads(session.path.read_text('utf8'))
            assert record['active']==1 and record['requests']==1
        assert json.loads(session.path.read_text('utf8'))['active']==0
    assert not session.path.exists()
