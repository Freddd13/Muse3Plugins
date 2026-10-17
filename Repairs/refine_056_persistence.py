from pathlib import Path
R=Path(__file__).resolve().parent
p=R/'staged056/plugins/ReferencePlayer/ReferencePlayer.view.qml';s=p.read_text(encoding='utf8')
s=s.replace('function restoreScoreProject(){\n  if','function restoreScoreProject(){\n  documentTimer.stop()\n  if',1)
s=s.replace('Component.onDestruction:{','Component.onDestruction:{saveScoreProject();',1)
p.write_bytes(s.encode())
p=R/'prepare_056_docs.py';s=p.read_text(encoding='utf8').replace('点“片段播放”试听','在播放对象选择“原曲”，点“播放”试听').replace('“查看片段”','“片段视图”').replace('再点“一起播放”。','把播放对象切为“一起播放”，再点“播放”。').replace('“联动定位”默认关闭','“联动编辑器定位”默认关闭').replace('点“重新定位”','点“重新定位音频”');p.write_bytes(s.encode())
p=R/'staged057/plugins/PerformanceExpression/PerformanceExpression_MS3.qml';s=p.read_text(encoding='utf8')
s=s.replace('config=data.config||config;','config=data.config||({strength:50,velocityStrength:50,velocityWriteMode:"preserve",rubatoStrength:50});')
p.write_bytes(s.encode())
