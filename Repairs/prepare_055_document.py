from pathlib import Path
R=Path(__file__).resolve().parent;H=R.parent.parent/'muse3_dev/MuseScore'
def stage(k,s):
 p=R/'native'/k;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(s.encode())
p=R/'native/mscore/plugin/api/scoreobserver.h';s=p.read_text(encoding='utf8');s=s.replace('      Q_INVOKABLE QString referenceStructureKey() const;','''      Q_INVOKABLE QString referenceStructureKey() const;
      Q_INVOKABLE QVariantMap workflowData(const QString& section) const;
      Q_INVOKABLE QVariantMap setWorkflowData(const QString& section,const QVariantMap& value);
      Q_INVOKABLE void workflowUndo(bool redo=false);''');stage('mscore/plugin/api/scoreobserver.h',s)
s=(H/'mscore/plugin/plugin.cmake').read_text(encoding='utf8').replace('set (PLUGIN_SRC','list(APPEND PLUGIN_API_SRC ${PROJECT_SOURCE_DIR}/mscore/workflow/workflowdocument.cpp)\n\nset (PLUGIN_SRC',1);stage('mscore/plugin/plugin.cmake',s)
stage('mscore/workflow/workflowdocument.cpp','''// GPL-2.0-or-later. Per-score workflow documents stored as ordinary metadata.
#include "mscore/plugin/api/scoreobserver.h"
#include "mscore/musescore.h"
#include "mscore/shortcut.h"
#include "libmscore/undo.h"
#include <QJsonDocument>
namespace Ms {namespace PluginAPI {
static bool documentSection(const QString& section){return section=="harmony"||section=="reference";}
QVariantMap ScoreObserver::workflowData(const QString& section) const {
 if(!_score||!documentSection(section))return {};
 const auto bytes=_score->masterScore()->metaTag("kumo."+section).toUtf8();
 return QJsonDocument::fromJson(bytes).toVariant().toMap();
}
QVariantMap ScoreObserver::setWorkflowData(const QString& section,const QVariantMap& value){
 if(!_score||!documentSection(section))return {{"error","请打开乐谱后保存。"}};
 if(playing())return {{"error","请停止播放后保存修改。"}};
 auto master=_score->masterScore();if(master->readOnly())return {{"error","这份乐谱以只读方式打开，请另存后修改。"}};
 const auto bytes=QJsonDocument::fromVariant(value).toJson(QJsonDocument::Compact);
 if(bytes.size()>4*1024*1024)return {{"error","项目记录过大，请减少附加数据后保存。"}};
 const QString key="kumo."+section,text=QString::fromUtf8(bytes);
 if(master->metaTag(key)==text)return {{"ok",true},{"changed",false}};
 master->startCmd();master->undo(new ChangeMetaText(master,key,text));master->endCmd();
 if(mscore)mscore->endCmd();return {{"ok",true},{"changed",true}};
}
void ScoreObserver::workflowUndo(bool redo){
 if(mscore&&_score&&mscore->currentScore()&&mscore->currentScore()->masterScore()==_score->masterScore())mscore->cmd(getAction(redo?"redo":"undo"));
}
}}
''')
