from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parent;HOST=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
log=HOST/'personal/CHANGELOG.md';s=log.read_text(encoding='utf8').replace('保留先前系统剪贴板未验收记录。','原操作14项、菜单显示12项、演奏编辑器45项亦通过；剪贴板子检查未运行，保留先前系统剪贴板未验收记录。');log.write_bytes(s.encode('utf8'))
index=HOST/'personal/docs/source-map.tsv';rows=[]
for row in index.read_text(encoding='utf8').splitlines():
 fields=row.split('\t')
 if len(fields)==6 and (HOST/fields[1]).is_file():
  hits=[i for i,v in enumerate((HOST/fields[1]).read_text(encoding='utf8').splitlines(),1) if fields[2] in v]
  if len(hits)==1:fields[3]=str(hits[0])
 rows.append('\t'.join(fields))
index.write_bytes(('\n'.join(rows)+'\n').encode('utf8'))
def git(*args,**kwargs):return subprocess.check_output(['git',*args],cwd=HOST,**kwargs).decode('utf8').strip()
paths=['mscore/CMakeLists.txt','mscore/dragdrop.cpp','mscore/menus.cpp','mscore/palette.cpp','mscore/palette/palettetree.cpp','mscore/performanceeditor/parameteredit.cpp','mscore/performanceeditor/parameteredit.h','mscore/temposymbols.cpp','mscore/temposymbols.h','mtest/mscore/p1native/tst_p1native.cpp','mtest/mscore/p1native/tempo_palette_tests.inc','mtest/libmscore/beam/tst_beam.cpp','personal/CHANGELOG.md','personal/VERSION','personal/docs/source-map.tsv']
git('add','--',*paths)
sha=git('hash-object','-w','--stdin',input=(ROOT/'out/guide-index.md').read_bytes());git('update-index','--cacheinfo','100644,'+sha+',personal/USER_GUIDE.md')
git('diff','--cached','--check');print(git('diff','--cached','--stat'));print(git('commit','-m','feat(tempo): playable palette symbols with protected placement and undo'))
git('tag','personal-v0.37.0');print(git('status','--short'))
