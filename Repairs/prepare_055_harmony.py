from pathlib import Path
R=Path(__file__).resolve().parent;P=R.parent;H=P.parent/'muse3_dev/MuseScore'
def stage(k,s):
 p=R/'native'/k;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(s.encode())
p=P/'ArrangementAssistant/ArrangementAssistant_MS3.qml';s=p.read_text(encoding='utf8').replace('issue.category===','issue.type===');p.write_bytes(s.encode())
s=(H/'mscore/workflow/chordeditor.cpp').read_text(encoding='utf8').replace('qMin(tick,source->lastMeasure()->endTick().ticks()-1)','qMin(tick==end?qMax(0,tick-1):tick,source->lastMeasure()->endTick().ticks()-1)',1);stage('mscore/workflow/chordeditor.cpp',s)
s=(H/'mscore/workflow/harmonylabel.cpp').read_text(encoding='utf8').replace('#include "libmscore/harmony.h"','#include "libmscore/harmony.h"\n#include "libmscore/chordlist.h"')
s=s.replace('      Harmony harmony(&scratch);','''      // This display uses the same baseline for root, slash and bass. The score style stays unchanged.
      for(auto& action:scratch.style().chordList()->renderListBase)if(action.type==RenderAction::RenderActionType::MOVE)action.movey=0;
      Harmony harmony(&scratch);''',1)
s=s.replace('      const QSizeF combined=vertical?', '      const qreal ascent=qMax(-chordBox.top()*scale,-degreeBox.top()),descent=qMax(chordBox.bottom()*scale,degreeBox.bottom());\n      const QSizeF combined=vertical?',1)
s=s.replace('QSizeF(a.width()+b.width()+spacing,qMax(a.height(),b.height()))','QSizeF(a.width()+b.width()+spacing,ascent+descent)',1)
s=s.replace('if(plain){painter.setPen(ink);','if(plain){painter.setPen(ink);',1)
s=s.replace('      if(!chord.isEmpty()){painter.save();','      if(!vertical){chordAt.setY(2+ascent+chordBox.top()*scale);degreeAt.setY(2+ascent+degreeBox.top());}\n      if(!chord.isEmpty()){painter.save();',1)
s=s.replace('{"font",reference.family()}', '{"baseline",2+ascent},{"ascent",ascent},{"descent",descent},{"font",reference.family()}',1)
stage('mscore/workflow/harmonylabel.cpp',s)
p=P/'HarmonyAssistant/HarmonyLabel.qml';s=p.read_text(encoding='utf8').replace('    implicitWidth:', '    property real baseline:rendered&&rendered.baseline?rendered.baseline:implicitHeight\n    implicitWidth:',1);p.write_bytes(s.encode())
p=P/'HarmonyAssistant/HarmonyAssistant_MS3.qml';s=p.read_text(encoding='utf8')
s=s.replace('    property var manualPositions:[]','    property bool nativeCorrectionWrite:false\n    property string nativeCorrectionsJSON:""\n    property var manualPositions:[]',1)
s=s.replace('saveCorrections();applyScorePreview();syncScoreRangeEditor()','saveCorrections(true);applyScorePreview();syncScoreRangeEditor()',1)
s=s.replace('        loadedFingerprint=analysisFingerprint\n        var saved=', '''        loadedFingerprint=analysisFingerprint
        if(observer&&typeof observer.workflowData==="function"){
            var embedded=observer.workflowData("harmony");nativeCorrectionsJSON=JSON.stringify(embedded)
            if(embedded.schema===2){manualOverrides=Timeline.validEdits(embedded.overrides||[]);manualPositions=AnnotationEdits.positions(embedded.positions||[]);return}
        }
        var saved=''',1)
s=s.replace('    function saveCorrections() {','''    function syncNativeCorrections(){
        if(nativeCorrectionWrite||!observer||typeof observer.workflowData!=="function")return
        var saved=observer.workflowData("harmony"),json=JSON.stringify(saved)
        if(!nativeCorrectionsJSON.length||json===nativeCorrectionsJSON)return
        nativeCorrectionsJSON=json;manualOverrides=Timeline.validEdits(saved.overrides||[]);manualPositions=AnnotationEdits.positions(saved.positions||[]);manualNeedsReview=false
        rebuildRegions();applyScorePreview();syncScoreRangeEditor()
    }
    function saveCorrections(inScore) {''',1)
s=s.replace('        if(!observer.saveConfiguration("HarmonyAssistant-regions-"+loadedFingerprint,','''        if(inScore&&typeof observer.setWorkflowData==="function"){
            var data={schema:2,fingerprint:loadedFingerprint,overrides:manualOverrides,positions:manualPositions}
            nativeCorrectionWrite=true;var result=observer.setWorkflowData("harmony",data);nativeCorrectionWrite=false
            if(result.error){noticeText=result.error;return}nativeCorrectionsJSON=JSON.stringify(observer.workflowData("harmony"))
        }
        if(!observer.saveConfiguration("HarmonyAssistant-regions-"+loadedFingerprint,''',1)
s=s.replace('        if(command==="undo" || command==="redo") {','''        if((command==="undo"||command==="redo")&&typeof observer.workflowUndo==="function"){observer.workflowUndo(command==="redo");syncNativeCorrections();return}
        if(command==="undo" || command==="redo") {''',1)
s=s.replace('rebuildRegions();saveCorrections();applyScorePreview();return','rebuildRegions();saveCorrections(true);applyScorePreview();return',1)
s=s.replace('rebuildRegions();saveCorrections();analyze();applyScorePreview()','rebuildRegions();saveCorrections(true);analyze();applyScorePreview()',1)
s=s.replace('editUndo=[];editRedo=[];saveCorrections()','editUndo=[];editRedo=[];saveCorrections(true)',1)
s=s.replace('loadedFingerprint="";manualNeedsReview=false','loadedFingerprint="";nativeCorrectionsJSON="";manualNeedsReview=false')
s=s.replace('        if (!started || internalChange) return\n        if (state.undoRedo','        if (!started || internalChange) return\n        syncNativeCorrections()\n        if (state.undoRedo',1)
s=s.replace('enabled:root.editRedo.length>0','enabled:typeof root.observer.workflowUndo==="function"||root.editRedo.length>0').replace('enabled:root.editUndo.length>0','enabled:typeof root.observer.workflowUndo==="function"||root.editUndo.length>0')
p.write_bytes(s.encode())
print('harmony typography and document edits prepared')
