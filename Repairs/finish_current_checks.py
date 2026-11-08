"""Check saved workspace migration and the extension switch in private copies."""
from pathlib import Path
import os
import subprocess
import sys
import zipfile

R = Path(__file__).resolve().parents[1]
O = R/'P2/out/usability-167'
runtime = R/'P1/out/final-regression/runtime/bin'
helper = R/'Repairs/check_current_features.py'
sys.stdout.reconfigure(encoding='utf8', errors='replace')

def check(name, cases, suite='pluginhost', extra=None):
    subprocess.run([sys.executable, str(helper), '--suite', suite, name, *cases],
                   cwd=R, env=dict(os.environ, **(extra or {})), check=True)

workspace = Path('C:/Users/Fred/AppData/Local/MuseScore/MuseScore3Evo/workspaces/kumo.workspace')
with zipfile.ZipFile(workspace) as archive:
    entry = next(name for name in archive.namelist() if name.endswith('workspace.xml'))
    copied = O/'user-workspace.xml'
    copied.write_bytes(archive.read(entry))
check('saved-tempo-palette', ['tempoWorkspaceImport135', 'ritFactoryTargetStyle135'],
      'p1native', {'D1_WORKSPACE_FIXTURE': str(copied)})

# The engraving fixture creates the full MuseScore window used by the following
# input/inspector operations; this suite otherwise starts with libmscore only.
check('notation-input-and-playback', ['freeSlurMixedSidesMouseAndReopen',
      'notationInputActions135', 'ritRangeLayout135',
      'notationInspectorSavedValues137', 'accentInspectorAndNativeDefault',
      'arpeggioInspectorScrubAndDeferredCommit', 'graceInspectorAndNativePreset'], 'performanceeditor')

config = runtime/'kumo.ini'
previous = config.read_bytes()
roundtrip = str(O/'feature-roundtrip')
try:
    check('extensions-before', ['sharePrepare145'], extra={'P2_GATE_ROUNDTRIP': roundtrip})
    config.write_text('[features]\nenable_exp_feature=false\n', encoding='utf8')
    check('extensions-disabled', ['featureDisabledStartup', 'shareDisabledRoundTrip145'],
          extra={'P2_FEATURE_GATE_OFF': '1', 'P2_GATE_ROUNDTRIP': roundtrip})
    config.write_bytes(previous)
    check('extensions-restored', ['shareEnabledRestore145'], extra={'P2_GATE_ROUNDTRIP': roundtrip})
finally:
    config.write_bytes(previous)

print('Saved workspace and on/off/save/reopen checks finished.')
