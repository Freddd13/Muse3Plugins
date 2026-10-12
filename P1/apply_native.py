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
 cm=HOST/'mscore/plugin/plugin.cmake';text=cm.read_text(encoding='utf8')
 owned=['referencefactory.h','referencefactory.cpp','midiinput.h','midiinput.cpp','scoreworkflow.cpp','workflowexpression.cpp','workflowvariants.cpp','tapwrite.h','tapwrite.cpp']
 for name in owned:
  text='\n'.join(line for line in text.splitlines() if line.strip()!='${PROJECT_SOURCE_DIR}/mscore/workflow/'+name)+'\n'
 additions=''.join('\n    ${PROJECT_SOURCE_DIR}/mscore/workflow/'+name for name in owned)
 text=text.replace('set (PLUGIN_API_SRC','set (PLUGIN_API_SRC'+additions,1)
 if cm.read_text(encoding='utf8')!=text:cm.write_bytes(text.encode('utf8'))
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
 cm=HOST/'mtest/CMakeLists.txt';text=cm.read_text(encoding='utf8')
 if '        mscore/p1native' not in text:cm.write_bytes(text.replace('        mscore/p0native','        mscore/p0native\n        mscore/p1native').encode('utf8'))
 replace('mscore/plugin/api/scoreobserver.h','#include <QVector>','#include <QVector>\n#include <memory>\n#include <atomic>')
 api=HOST/'mscore/plugin/api/scoreobserver.h';text=api.read_text(encoding='utf8')
 ownedFields=['      int _midiToken = 0;','      std::shared_ptr<std::atomic_bool> _midiCancel;','      QPointer<Ms::Score> _workflowOriginal;','      bool _workflowApplyingPreview = false;']
 text='\n'.join(l for l in text.splitlines() if l not in ownedFields)+'\n'
 text=text.replace('      int _readOnlyJobToken = 0;','      int _readOnlyJobToken = 0;\n'+'\n'.join(ownedFields),1)
 if api.read_text(encoding='utf8')!=text:api.write_bytes(text.encode('utf8'))
 api=HOST/'mscore/plugin/api/scoreobserver.h';text=api.read_text(encoding='utf8')
 declarations=[
  'int readPerformanceMidi(const QString& path);',
  'void cancelPerformanceMidi();',
  'QVariantMap savePerformanceSource(const QString& source,const QString& destination,const QString& expected);',
  'QVariantMap workflowInfo();',
  'QVariantMap workflowStatus();',
  'QVariantMap workflowFingerprint(int from,int limit,const QString& expected);',
  'QVariantMap performanceRange(int start,int end,int firstTrack,int endTrack,int fromTick,int limit,const QString& expected);',
  'QVariantMap navigateWorkflow(const QVariantMap& range,bool audition = false);',
  'QVariantMap applyExpression(const QVariantMap& candidate);',
  'QVariantMap copyWorkflowScore(const QString& destination,const QString& expected,bool overwrite = false);',
  'QVariantMap openWorkflowScore(const QString& filename,bool baseline = false,const QString& expectedHash = QString());',
  'QVariantMap previewExpression(const QString& workspace,const QVariantMap& candidate,const QVariantMap& scope);',
  'QVariantMap returnWorkflowSource();'
 ]
 for signature in declarations:
  if signature not in text:text=text.replace('      Q_INVOKABLE QString analysisRevision();','      Q_INVOKABLE QString analysisRevision();\n      Q_INVOKABLE '+signature,1)
 if text!=api.read_text(encoding='utf8'):api.write_bytes(text.encode('utf8'))
 replace('mscore/plugin/api/scoreobserver.h','   signals:\n      void readOnlyJobFinished','   signals:\n      void performanceMidiReady(int token,const QVariantMap& result);\n      void readOnlyJobFinished')

 replace('mscore/plugin/api/scoreobserver.cpp','ScoreObserver::~ScoreObserver() { cancelReadOnlyJob();','ScoreObserver::~ScoreObserver() { cancelPerformanceMidi(); cancelReadOnlyJob();')
 print('P1 owned modules copied, existing features preserved.')
if __name__=='__main__':apply()
