from pathlib import Path
root=Path(__file__).resolve().parent;host=Path('E:/programming/funcodes/muse3_dev/MuseScore')
def save(name,s):
 p=root/'native'/name;p.write_text(s,encoding='utf8',newline='\n');(host/name).write_bytes(p.read_bytes())
name='mscore/plugin/api/scoreobserver.h';s=(root/'native'/name).read_text(encoding='utf8').replace('      Q_INVOKABLE QVariantMap finishExpressionAudition();','      Q_INVOKABLE QVariantMap finishExpressionAudition();\n      Q_INVOKABLE QVariantMap closeExpressionPreviewTabs();',1);save(name,s)
name='mscore/workflow/workflowexpression.cpp';s=(root/'native'/name).read_text(encoding='utf8').replace('#include <QTemporaryDir>','#include <QTemporaryDir>\n#include <QRegularExpression>',1)
at=s.index('QVariantMap ScoreObserver::finishExpressionAudition()')
s=s[:at]+'''QVariantMap ScoreObserver::closeExpressionPreviewTabs(){
 if(!idle())return {{"error",tr("停止播放后可以整理旧试听页。")}};
 if(!mscore||!_score)return {{"error",tr("回到正在编写的乐谱后，可以关闭旧试听页。")}};
 const QRegularExpression generated("^expression-[0-9a-fA-F-]{36}\\\\.mscz$");
 int closed=0,kept=0;const auto open=mscore->scores();
 for(auto score:open){
  if(score==_score->masterScore()||!generated.match(score->fileInfo()->fileName()).hasMatch())continue;
  const QString folder=QDir::fromNativeSeparators(score->fileInfo()->absolutePath());
  if(!score->property("kumoWorkflowOwned").toBool()&&!folder.contains("/musescore-expression/",Qt::CaseInsensitive))continue;
  if(score->dirty()){++kept;continue;}mscore->closeScore(score);++closed;
 }
 return {{"ok",true},{"closed",closed},{"kept",kept}};
}
''' +s[at:];save(name,s)
name='mscore/seq.cpp';s=(root/'native'/name).read_text(encoding='utf8');s=s.removeprefix('#include "workflow/playbackpreview.h"\n');s=s.replace('#include "seq.h"','#include "seq.h"\n#include "workflow/playbackpreview.h"\n#include <QCoreApplication>',1);save(name,s)
p=root.parent/'PerformanceExpression/PerformanceExpression_MS3.qml';s=p.read_text(encoding='utf8').replace(' Menu {id:projectMenu',' Menu {id:projectMenu\n  MenuItem {text:"关闭已保存的旧试听页";enabled:!root.busy&&!root.previewing&&root.observer&&!root.observer.playing;onTriggered:{var r=root.observer.closeExpressionPreviewTabs();root.status=r.error?Messages.readable(r.error):"已关闭 "+r.closed+" 个旧试听页"+(r.kept?"，另有 "+r.kept+" 页保存着修改。":"。")}}',1);p.write_text(s,encoding='utf8',newline='\n')
print('Clean generated preview tabs can be closed from the project menu')
