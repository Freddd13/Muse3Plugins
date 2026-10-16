from pathlib import Path
root=Path(__file__).resolve().parent;p=root.parent/'PerformanceExpression/PerformanceExpression_MS3.qml';s=p.read_text(encoding='utf8')
s=s.replace(' property var previewUndo:[]',' property var previewUndo:[]\n property var previewRedo:[]\n onPreviewUndoChanged:publishComparison()\n onPreviewRedoChanged:publishComparison()',1)
s=s.replace('previewVersion:previewVersion,result:','previewVersion:previewVersion,previewCanUndo:previewUndo.length>0,previewCanRedo:previewRedo.length>0,result:',1)
begin=s.index('  if(action==="undoPreview"){');end=s.index('  if(action==="velocityTargets"',begin)
s=s[:begin]+'''  if(action==="undoPreview"||action==="redoPreview"){
   var backward=action==="undoPreview",history=(backward?previewUndo:previewRedo).slice();
   if(!history.length)return;
   var current={config:Project.copy(config),candidate:Project.copy(candidate)},previous=history.pop();
   if(backward){previewUndo=history;previewRedo=previewRedo.concat([current]);}else{previewRedo=history;previewUndo=previewUndo.concat([current]);}
   config=previous.config;candidateConfig=JSON.stringify(config);candidate=previous.candidate;dirtyProject=true;status=backward?"已撤销上一次预览调整。":"已重做预览调整。";return;
  }
''' +s[end:]
s=s.replace('   previewUndo=previewUndo.concat([{config:Project.copy(config),candidate:Project.copy(candidate)}]).slice(-40);','   pushPreviewUndo();',1)
s=s.replace(' function editConfig(name,value){',' function pushPreviewUndo(){if(candidate){previewUndo=previewUndo.concat([{config:Project.copy(config),candidate:Project.copy(candidate)}]).slice(-40);previewRedo=[];}}\n function editConfig(name,value){pushPreviewUndo();',1)
s=s.replace('  applicationMessage=message;refreshingApplication=true;','  previewUndo=[];previewRedo=[];applicationMessage=message;refreshingApplication=true;',1)
p.write_text(s,encoding='utf8',newline='\n')
p=root/'native/mscore/performanceeditor/expressioncompare.cpp';s=p.read_text(encoding='utf8')
old='      if((event->type()==QEvent::ShortcutOverride||event->type()==QEvent::KeyPress)&&static_cast<QKeyEvent*>(event)->matches(QKeySequence::Undo)){event->accept();if(event->type()==QEvent::KeyPress)workflowContext()->expressionAction("undoPreview",QString(),QString());return true;}'
new='''      if(event->type()==QEvent::ShortcutOverride||event->type()==QEvent::KeyPress){auto key=static_cast<QKeyEvent*>(event);const auto state=workflowContext()->expression();const bool undo=key->matches(QKeySequence::Undo)&&state.value("previewCanUndo").toBool(),redo=key->matches(QKeySequence::Redo)&&state.value("previewCanRedo").toBool();if(undo||redo){event->accept();if(event->type()==QEvent::KeyPress)workflowContext()->expressionAction(undo?"undoPreview":"redoPreview",QString(),QString());return true;}}'''
assert s.count(old)==1;s=s.replace(old,new);p.write_text(s,encoding='utf8',newline='\n')
p=root/'native/mtest/mscore/performanceeditor/expression_compare_tests.inc';s=p.read_text(encoding='utf8').replace('{"previewVersion",1},{"candidate",candidate}','{"previewVersion",1},{"previewCanUndo",true},{"candidate",candidate}',1);p.write_text(s,encoding='utf8',newline='\n')
print('Preview undo/redo stays separate from applied score changes')
