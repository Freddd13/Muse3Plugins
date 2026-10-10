"""One-time final scope cleanup before compiling tests."""
from pathlib import Path
repo=Path('E:/programming/funcodes/muse3_dev/MuseScore')
base=Path(__file__).resolve().parents[1]
p=repo/'mtest/mscore/pluginhost/tst_pluginhost.cpp';s=p.read_text(encoding='utf-8')
assert 'root->version()=="1.4.0"' in s;s=s.replace('root->version()=="1.4.0"','root->version()=="1.5.0"')
with p.open('w',encoding='utf-8',newline='\n') as f:f.write(s)
p=repo/'mscore/plugin/api/scoreobserver.cpp';s=p.read_text(encoding='utf-8')
old='clearPreview(this); clearPreview(&_baseOwner); _baseColors.clear(); _baseChordBoxes.clear(); _previewViews.clear(); _activePreviewTick=-1;'
assert old in s
s=s.replace(old,old+'\n        setProperty("previewStatus",QVariantMap{{"hidden",0},{"unplaced",QVariantList{}},{"fontFallback",QString()}});',1)
with p.open('w',encoding='utf-8',newline='\n') as f:f.write(s)
for p in base.iterdir():
    if p.suffix in ('.qml','.js') or p.name=='README.md':
        content=p.read_bytes().replace(b'\r\n',b'\n');p.write_bytes(content)
        (repo/'share/plugins/HarmonyAssistant'/p.name).write_bytes(content)
print('Final runtime sync and metadata clearing; existing functionality preserved')
