"""Record the committed native increment and matching deployment hashes."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

base = Path(__file__).resolve().parents[1]
repo = Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
git = r'E:\Git\cmd\git.exe'
commit = subprocess.check_output([git, '-C', str(repo), 'rev-parse', 'personal-v0.3.0']).decode('ascii').strip()
patch = subprocess.check_output([git, '-C', str(repo), 'format-patch', '-1', '--stdout', commit])
(base / 'native/score-observer-0.3.0.patch').write_bytes(patch)
snapshot = base / 'native/v0.3.0'
paths = ['mscore/notepreview.h', 'mscore/plugin/api/scoreobserver.cpp',
         'mscore/plugin/api/scoreobserver.h', 'mscore/plugin/qmlplugin.cpp',
         'mscore/plugin/qmlplugin.h', 'mscore/plugin/mscorePlugins.cpp',
         'mscore/plugin/pluginManager.cpp', 'mscore/scoreview.cpp',
         'mtest/mscore/pluginhost/tst_pluginhost.cpp', 'mtest/mscore/pluginhost/CMakeLists.txt',
         'mtest/mscore/scoreobserver/tst_scoreobserver.cpp', 'mtest/mscore/scoreobserver/arpeggio.mscx',
         'personal/tools/test_harmony_gui.py', 'personal/tools/test_harmony_host.py']
for path in paths:
    destination = snapshot / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(str(repo / path), str(destination))
names = ['HarmonyAssistant_MS3.qml', 'Harmony.js', 'Preferences.js', 'Analysis.js',
         'ConfigurationEditor.qml', 'SettingsStore.qml', 'PanelCard.qml', 'UiLabel.qml', 'README.md']
manifest = {'pluginVersion':'1.1.0', 'personalVersion':'0.3.0', 'commit':commit,
            'parent':'b878200db892d62c0481f9d06ae58753cfc6738b', 'files':{}}
locations = {'source':base, 'repository':repo / 'share/plugins/HarmonyAssistant',
             'installed':repo / 'msvc.install_harmony_1_1_x64/plugins/HarmonyAssistant',
             'enabledUserCopy':Path(r'C:\Users\Fred\Documents\MuseScore3\插件\HarmonyAssistant')}
for name in names:
    digests = {key:hashlib.sha256((directory / name).read_bytes()).hexdigest() for key, directory in locations.items()}
    assert len(set(digests.values())) == 1, name
    manifest['files'][name] = digests['source']
for path in [base / 'dist/HarmonyAssistant-1.1.0.zip', repo / 'msvc.install_harmony_1_1_x64/bin/MuseScore3Evo.exe']:
    manifest[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
(base / 'dist/release-1.1.0.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
images = base / 'tests/native-gui-1-1'
images.mkdir(parents=True, exist_ok=True)
for name in ['ribbon.png', 'floating-panel.png', 'gui.txt']:
    shutil.copy2(str(repo / 'msvc.build_harmony_release_x64/harmony-gui-final' / name), str(images / name))
print(json.dumps({'commit':commit,'patchBytes':len(patch),'matchingRuntimeCopies':4}))
