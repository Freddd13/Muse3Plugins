# coding: utf-8
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parent
HOST=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
def git(*args,**kwargs):
    return subprocess.check_output(['git',*args],cwd=HOST,**kwargs).decode('utf8').strip()
git('diff','--check','--','mscore','mtest','share/plugins/HarmonyAssistant','personal/CHANGELOG.md','personal/docs','personal/VERSION')
paths=['mscore/CMakeLists.txt','mscore/notepreview.h','mscore/plugin/api/scoreobserver.cpp','mscore/plugin/qmlplugin.cpp','mscore/scoreview.cpp','mscore/scoreview.h','mscore/workflow/chordoverlay.cpp','mtest/mscore/pluginhost/tst_pluginhost.cpp','mtest/mscore/scoreobserver/tst_scoreobserver.cpp','share/plugins/HarmonyAssistant/AppearanceEditor.qml','share/plugins/HarmonyAssistant/HarmonyAssistant_MS3.qml','share/plugins/HarmonyAssistant/Preferences.js','personal/CHANGELOG.md','personal/docs/source-map.tsv','personal/docs/images/chord-034.png','personal/VERSION']
git('add','--',*paths)
sha=git('hash-object','-w','--stdin',input=(ROOT/'out/guide-index.md').read_bytes())
git('update-index','--cacheinfo','100644,'+sha+',personal/USER_GUIDE.md')
print(git('diff','--cached','--stat'))
print(git('commit','-m','fix(harmony): visible score annotations and compact top panel'))
git('tag','personal-v0.34.0')
print(git('status','--short'))
