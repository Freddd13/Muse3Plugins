"""Bounded final runtime checks, preserving generated test scores."""
from pathlib import Path
import hashlib,subprocess,shutil
repo=Path('E:/programming/funcodes/muse3_dev/MuseScore')
base=Path(__file__).resolve().parents[1]
p=repo/'mtest/mscore/scoreobserver/smoke.qml';s=p.read_text(encoding='utf-8')
needle='            result.persistedCorrection='
assert needle in s and 'upper extensions changed' not in s
s=s.replace(needle,'''            if(!panel.automaticRegions.some(function(r){return r.start<=480 && r.end>480 && r.root===0 && r.definition===23}))result.failures.push("upper extensions changed the bass harmony")
'''+needle,1)
with p.open('w',encoding='utf-8',newline='\n') as f:f.write(s)
dest=repo/'msvc.build_personal_0_6_x64/harmony-note-1-4-final/note-exports';dest.mkdir(exist_ok=True)
for name in ['grace-test.mscx','notelimits-test.mscx','tpc-test.mscx','tpc-transpose-test.mscx','tpc-transpose2-test.mscx']:
    p=repo/name
    if p.exists():
        assert not (dest/name).exists()
        assert p.resolve().parent==repo.resolve() and repo.resolve() in dest.resolve().parents
        shutil.move(str(p),str(dest/name))
runtime=sorted(p for p in base.iterdir() if p.suffix in ('.qml','.js') or p.name=='README.md')
for p in runtime:
    for folder in [repo/'share/plugins/HarmonyAssistant',repo/'msvc.install_harmony_1_4_x64/plugins/HarmonyAssistant',Path('C:/Users/Fred/Documents/MuseScore3/插件/HarmonyAssistant')]:
        assert p.read_bytes()==(folder/p.name).read_bytes(),str(folder/p.name)
built=repo/'msvc.build_personal_0_6_x64/main/Release/MuseScore3Evo.exe'
installed=repo/'msvc.install_harmony_1_4_x64/bin/MuseScore3Evo.exe'
assert hashlib.sha256(built.read_bytes()).digest()==hashlib.sha256(installed.read_bytes()).digest()
print('14 runtime files identical across four copies; installed exe matches final build')
