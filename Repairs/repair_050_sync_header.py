from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;HOST=ROOT.parent/'muse3_dev/MuseScore'
p=ROOT/'Repairs/apply_native.py';s=p.read_text(encoding='utf8')
start=s.index(" p=HOST/'mscore/plugin/api/scoreobserver.h';s=p.read_text(encoding='utf8')")
end=s.index(" patch('mscore/plugin/plugin.cmake'",start)
block=s[start:end]
s=s[:start]+" if not (ROOT/'native/mscore/plugin/api/scoreobserver.h').is_file():\n"+'\n'.join(' '+line if line else line for line in block.rstrip().split('\n'))+'\n'+s[end:]
p.write_text(s,encoding='utf8',newline='\n')
source=ROOT/'Repairs/native/mscore/plugin/api/scoreobserver.h';target=HOST/'mscore/plugin/api/scoreobserver.h'
before=source.read_text(encoding='utf8');after=target.read_text(encoding='utf8')
old='      Q_INVOKABLE QVariantMap updateEditorComparisonState(const QVariantMap&);\n      Q_INVOKABLE QVariantMap setReferenceTracks(const QVariantList&);'
new='      Q_INVOKABLE QVariantMap setReferenceTracks(const QVariantList&);\n      Q_INVOKABLE QVariantMap updateEditorComparisonState(const QVariantMap&);'
assert after==before.replace(old,new)
target.write_bytes(source.read_bytes())
