"""P1 additions and unique, idempotent host integration. Does not run P0 patches."""
from pathlib import Path
ROOT=Path(__file__).resolve().parent
HOST=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
def replace(path,old,new):
 p=HOST/path;s=p.read_text(encoding='utf8')
 if new in s:return
 if s.count(old)!=1:raise RuntimeError('P1 anchor not unique: '+path+' '+old[:50])
 p.write_bytes(s.replace(old,new).encode('utf8'))
def apply():
 for src in (ROOT/'native').rglob('*'):
  if src.is_file():
   dst=HOST/src.relative_to(ROOT/'native');dst.parent.mkdir(parents=True,exist_ok=True)
   if not dst.exists() or dst.read_bytes()!=src.read_bytes():dst.write_bytes(src.read_bytes())
 replace('mscore/plugin/plugin.cmake','set (PLUGIN_API_SRC','set (PLUGIN_API_SRC\n    ${PROJECT_SOURCE_DIR}/mscore/workflow/referencefactory.h\n    ${PROJECT_SOURCE_DIR}/mscore/workflow/referencefactory.cpp')
 replace('mscore/plugin/api/qmlpluginapi.cpp','#include "scoreobserver.h"','#include "scoreobserver.h"\n#include "mscore/workflow/referencefactory.h"')
 replace('mscore/plugin/api/qmlpluginapi.cpp','QObject* PluginAPI::newScoreObserver()','QObject* PluginAPI::newReferenceMedia() { return Ms::createReferenceMedia(this); }\n\nQObject* PluginAPI::newScoreObserver()')
 replace('mscore/plugin/api/qmlpluginapi.h','      Q_INVOKABLE QObject* newScoreObserver();','      Q_INVOKABLE QObject* newScoreObserver();\n      Q_INVOKABLE QObject* newReferenceMedia();')
 cm=HOST/'mscore/CMakeLists.txt';s=cm.read_text(encoding='utf8')
 if 'add_subdirectory(referenceaudio)' not in s:cm.write_bytes((s+'\n# P1 optional media backend; the app never links Qt Multimedia.\nadd_subdirectory(referenceaudio)\n').encode('utf8'))
 for folder in ('ReferencePlayer','PerformanceExpression','ArrangementVariants','WorkflowCommon'):
  plugin=ROOT.parent/folder
  if not plugin.exists():continue
  for src in plugin.rglob('*'):
   if src.is_file() and src.suffix in ('.qml','.js','.md'):
    dst=HOST/'share/plugins'/folder/src.relative_to(plugin);dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(src.read_bytes())
 print('P1 owned modules copied, existing features preserved.')
if __name__=='__main__':apply()
