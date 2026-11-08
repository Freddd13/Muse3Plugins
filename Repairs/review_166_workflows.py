"""Revisit the edited workflows using the existing application controls."""
from pathlib import Path
import os
import subprocess

R = Path(__file__).resolve().parents[1]
H = R.parent / 'muse3_dev/MuseScore'
O = R / 'P2/out/repair-166'
runtime = R / 'P1/out/final-regression/runtime/bin'
env = dict(os.environ, QT_QPA_PLATFORM='offscreen', QT_QUICK_BACKEND='software',
           QML_DISABLE_DISK_CACHE='1', KUMO_MCP_AUTOSTART='0',
           HARMONY_TEST_ARTIFACTS=str(O), PERFORMANCE_NO_SYSTEM_CLIPBOARD='1',
           P0_TEST_SOUNDFONT=str(H / 'msvc.install_repair_current_x64/sound/MuseScore_General.sf3'))
log = O / 'continuous-workflows.txt'
tasks = ['midiTracksEditor160', 'performanceTimingEditor161',
         'spectrumSharedTimeline162', 'referenceControlsPlayback163', 'scoreVideoExport164']
result = subprocess.run([str(runtime / 'tst_pluginhost.exe'), *tasks, '-o', str(log) + ',txt'],
                        cwd=runtime, env=env, timeout=180)
print('\n'.join(line for line in log.read_text('utf8', errors='replace').splitlines()
                if line.startswith(('PASS', 'FAIL', 'QFATAL', 'Totals:'))))
raise SystemExit(result.returncode)
