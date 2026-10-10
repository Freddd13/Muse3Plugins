# -*- coding: utf-8 -*-
"""Deploy task runtime with exact-baseline guards; never delete old files."""
from pathlib import Path
import shutil,hashlib,json
repo=Path('E:/programming/funcodes/muse3_dev/MuseScore');base=Path(__file__).resolve().parents[1]
installed=repo/'msvc.install_harmony_1_5_x64'
enabled=Path('C:/Users/Fred/Documents/MuseScore3/插件/HarmonyAssistant')
runtime=sorted(p for p in base.iterdir() if p.suffix in ('.qml','.js') or p.name=='README.md')
assert len(runtime)==21
assert (installed/'bin/MuseScore3Evo.exe').exists()
for p in runtime:
    target=enabled/p.name;old=base/'backups/1.4.0'/(p.name+'.bak')
    if target.exists():
        assert old.exists() and target.read_bytes()==old.read_bytes(),'Enabled copy independently changed: '+p.name
for p in runtime:
    target=enabled/p.name
    if target.exists():
        backup=enabled/(p.name+'.pre-1.5.0.bak')
        assert not backup.exists() or backup.read_bytes()==target.read_bytes()
        if not backup.exists():shutil.copy2(str(target),str(backup))
    for dest in (repo/'share/plugins/HarmonyAssistant',installed/'plugins/HarmonyAssistant',enabled):
        dest.mkdir(parents=True,exist_ok=True);shutil.copy2(str(p),str(dest/p.name))
sdk=repo/'dependencies/qt5.15.2/msvc2019_64/bin'
for name in ('Qt5QmlModels.dll','Qt5QmlWorkerScript.dll'):
    shutil.copy2(str(sdk/name),str(installed/'bin'/name))
for p in runtime:
    for folder in (repo/'share/plugins/HarmonyAssistant',installed/'plugins/HarmonyAssistant',enabled):
        assert p.read_bytes()==(folder/p.name).read_bytes(),str(folder/p.name)
built=repo/'msvc.build_harmony_release_x64/main/Release/MuseScore3Evo.exe'
assert hashlib.sha256(built.read_bytes()).digest()==hashlib.sha256((installed/'bin/MuseScore3Evo.exe').read_bytes()).digest()
print('21 release files identical across four copies; old enabled files backed up; installed exe matches build')
