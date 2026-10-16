from pathlib import Path
root=Path(__file__).resolve().parent;host=Path('E:/programming/funcodes/muse3_dev/MuseScore')
def patch(name,old,new):
 p=root/'native'/name;s=p.read_text(encoding='utf8');assert s.count(old)==1,(name,old[:85],s.count(old));p.write_text(s.replace(old,new),encoding='utf8',newline='\n');(host/name).write_bytes(p.read_bytes())
patch('mscore/workflow/workflowexpression.cpp','QVariantMap ScoreObserver::finishExpressionAudition(){stopPlaybackPreview(true);','QVariantMap ScoreObserver::finishExpressionAudition(){workflowContext()->finishPlaybackSession();stopPlaybackPreview(true);')
patch('mscore/workflow/workflowexpression.cpp',' const QString key=analysisRevision()+QString::fromLatin1(QCryptographicHash::hash(QJsonDocument::fromVariant(candidate).toJson(QJsonDocument::Compact),QCryptographicHash::Sha256).toHex());',' const QVariantMap settings{{"candidate",candidate},{"scope",scope},{"relTempo",_score->tempomap()->relTempo()}};\n const QString key=analysisRevision()+QString::fromLatin1(QCryptographicHash::hash(QJsonDocument::fromVariant(settings).toJson(QJsonDocument::Compact),QCryptographicHash::Sha256).toHex());')
patch('mscore/workflow/workflowexpression.cpp','  stopPlaybackPreview();if(seq&&seq->isPlaying())seq->stopWait();if(!idle())','  workflowContext()->finishPlaybackSession();stopPlaybackPreview();if(seq&&seq->isPlaying())seq->stopWait();if(!seq->isPlaying())seq->synchronizeStoppedGui();if(!idle())')
patch('mscore/workflow/workflowexpression.cpp','  auto values=candidate;values["revision"]=local.analysisRevision();auto applied=local.applyExpression(values);if(applied.contains("error"))return applied;','''  auto reference=[&](){auto request=scope.value("reference").toMap();if(request.isEmpty())return QVariantMap();request["revision"]=local.analysisRevision();request["start"]=scope.value("start");request["end"]=scope.value("end");request["occurrence"]=scope.value("occurrence",1);return local.referencePlan(request);};
  original.reference=reference();if(original.reference.contains("error"))return original.reference;alignPreviewReference(original);
  auto values=candidate;values["revision"]=local.analysisRevision();auto applied=local.applyExpression(values);if(applied.contains("error"))return applied;''')
patch('mscore/workflow/workflowexpression.cpp','  auto changed=renderPlaybackPreview(_score,target);','  auto changed=renderPlaybackPreview(_score,target);changed.reference=reference();if(changed.reference.contains("error"))return changed.reference;alignPreviewReference(changed);')
patch('mscore/workflow/workflowexpression.cpp',' return startPlaybackPreview(_score,proposed,scope);',''' auto range=scope;range["deferStart"]=scope.contains("reference");auto started=startPlaybackPreview(_score,proposed,range);
 if(started.contains("error")||!scope.contains("reference"))return started;
 auto plan=playbackPreviewReferencePlan(_score,proposed,started.value("fromUtick").toInt());plan["revision"]=analysisRevision();auto audio=startReferencePlayback(plan);if(audio.contains("error")){stopPlaybackPreview(true);return audio;}
 started["preparing"]=true;return started;''')
patch('mscore/workflow/referenceworkflow.cpp',' stopPlaybackPreview();',' if(!plan.value("usesPreview").toBool())stopPlaybackPreview();')
# Every new host uses the source-score playback session, with or without reference audio.
p=root.parent/'PerformanceExpression/PerformanceExpression_MS3.qml';s=p.read_text(encoding='utf8')
s=s.replace('if(!auditionAudio&&typeof observer.auditionExpression==="function")','if(typeof observer.auditionExpression==="function")')
start=s.index('  if(typeof observer.auditionExpression==="function"){',s.index(' function beginAudition'))
end=s.index('  var r=observer.previewExpression',start)
block=s[start:end]
reference=block[block.index('  if(auditionAudio&&audioProject'):]
native=block[:block.index('  legacyAudition=true;')]
s=s[:start]+reference+native+'  legacyAudition=true;\n'+s[end:]
s=s.replace('else status="正在播放："+(useCandidate?"拟采用效果":"谱中效果")+"。切换效果会接着当前拍位播放。";','else status=playing.preparing?"正在准备参考音频与乐谱…":"正在播放："+(useCandidate?"拟采用效果":"谱中效果")+"。切换效果会接着当前拍位播放。";',1)
s=s.replace('text:(root.playbackState.playing?"正在播放：":"已暂停：")','text:(root.playbackState.preparing?"正在准备：":root.playbackState.playing?"正在播放：":"已暂停：")',1)
p.write_text(s,encoding='utf8',newline='\n');print('Reference audio uses the same source-score audition and resumes at the same beat')
