from pathlib import Path
import shutil

base = Path(__file__).resolve().parents[1]
repo = Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
runtime = ['HarmonyAssistant_MS3.qml','Harmony.js','PanelCard.qml','UiLabel.qml','README.md']
paths = [base/name for name in runtime]
paths += [repo/'personal/docs'/name for name in ['README.md','01-architecture.md','04-feature-map.md','05-piano-development.md','06-build-and-test.md','10-score-observer.md']]
paths += [repo/'mtest/mscore/scoreobserver/piano.mscx']
for path in paths:
    text = path.read_text(encoding='utf-8-sig')
    with path.open('w',encoding='utf-8',newline='\n') as stream: stream.write(text)
for name in runtime:
    shutil.copy2(base/name,repo/'share/plugins/HarmonyAssistant'/name)
target = repo/'msvc.install_harmony_release_x64/plugins/HarmonyAssistant'
target.mkdir(parents=True,exist_ok=True)
for name in runtime: shutil.copy2(base/name,target/name)
for source,name in [('mscore/notepreview.h','notepreview.h'),('mscore/plugin/api/scoreobserver.h','scoreobserver.h'),('mscore/plugin/api/scoreobserver.cpp','scoreobserver.cpp'),('mtest/mscore/scoreobserver/tst_scoreobserver.cpp','tst_scoreobserver.cpp'),('mtest/mscore/scoreobserver/CMakeLists.txt','test-CMakeLists.txt')]:
    shutil.copy2(repo/source,base/'native'/name)
print('Line endings normalized; final plugin installed; native patch source snapshots updated')
