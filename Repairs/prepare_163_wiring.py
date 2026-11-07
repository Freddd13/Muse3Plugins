from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];N=ROOT/'P2/native'
def edit(name,old,new):
    path=N/name;text=path.read_text('utf8')
    if new in text:return
    if old not in text:raise ValueError(name+' missing target')
    path.write_text(text.replace(old,new,1),encoding='utf8',newline='\n')
path=N/'mscore/workflow/referencefactory.cpp';text=path.read_text('utf8')
if 'class ReferenceScoreControls' in text:
    start=text.index('// Small native buttons follow exact association starts.');end=text.index('QPointer<ReferencePlaybackPolicy>',start)
    text=text[:start]+text[end:];text=text.replace('#include "referencefactory.h"','#include "referencefactory.h"\n#include "referencecontrols.h"').replace('new ReferenceScoreControls(project);','installReferenceScoreControls(project);');path.write_text(text,encoding='utf8',newline='\n')
edit('mscore/plugin/plugin.cmake','    ${PROJECT_SOURCE_DIR}/mscore/workflow/referencefactory.cpp','    ${PROJECT_SOURCE_DIR}/mscore/workflow/referencefactory.cpp\n    ${PROJECT_SOURCE_DIR}/mscore/workflow/referencecontrols.cpp\n    ${PROJECT_SOURCE_DIR}/mscore/workflow/referencecontrols.h')
edit('mscore/workflow/workflowdocument.cpp','section=="harmony"||section=="reference"','section=="harmony"||section=="referenceControls"||section=="reference"')
edit('mscore/referenceaudio/mediaproject.h','      Q_PROPERTY(QString activeAssociation','      Q_PROPERTY(QString scoreRangeDisplay READ scoreRangeDisplay WRITE setScoreRangeDisplay NOTIFY scoreControlsChanged)\n      Q_PROPERTY(QString activeAssociation')
edit('mscore/referenceaudio/mediaproject.h','      bool scoreControls()const;','      QString scoreRangeDisplay()const;\n      void setScoreRangeDisplay(const QString&);\n      bool scoreControls()const;')
edit('mscore/referenceaudio/mediaproject.cpp','bool ReferenceMediaProject::scoreControls()const','QString ReferenceMediaProject::scoreRangeDisplay()const{return QSettings().value("workflow/reference/scoreRangeDisplay","hover").toString();}\nvoid ReferenceMediaProject::setScoreRangeDisplay(const QString& value){if(value!="always"&&value!="hover"&&value!="playing")return;if(value==scoreRangeDisplay())return;QSettings().setValue("workflow/reference/scoreRangeDisplay",value);emit scoreControlsChanged();}\nbool ReferenceMediaProject::scoreControls()const')
edit('share/workflow/panels/ReferencePlayer/ReferencePlayer.view.qml','        Desk.DeskSwitch {text:"联动编辑器定位"','        Desk.DeskComboBox {objectName:"referenceScoreRangeDisplay";width:140;model:["范围：悬停时显示","范围：始终显示","范围：播放时显示"];currentIndex:root.audioProject?({hover:0,always:1,playing:2}[root.audioProject.scoreRangeDisplay]||0):0;onActivated:if(root.audioProject)root.audioProject.scoreRangeDisplay=["hover","always","playing"][currentIndex]}\n        Desk.DeskButton {objectName:"referenceRestoreScoreControls";iconName:"restore";text:"恢复谱面按钮";enabled:root.observer&&!root.observer.playing;onClicked:{var result=root.observer.setWorkflowData("referenceControls",{schema:1});root.status=result.error||"谱面按钮已恢复显示和自动位置；Ctrl+Z可撤销。"}}\n        Desk.DeskSwitch {text:"联动编辑器定位"')
edit('mtest/mscore/pluginhost/tst_pluginhost.cpp','      void spectrumInteraction162();','      void referenceControls163();\n      void referenceControlsPlayback163();\n      void referenceControlsRange163();\n      void spectrumInteraction162();')
edit('mtest/mscore/pluginhost/tst_pluginhost.cpp','#include "spectrum_162_tests.inc"','#include "spectrum_162_tests.inc"\n#include "reference_163_tests.inc"')
