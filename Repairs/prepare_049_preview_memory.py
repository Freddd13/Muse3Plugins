from pathlib import Path
p=Path(__file__).resolve().parent.parent/'PerformanceExpression/PerformanceExpression_MS3.qml'
s=p.read_text(encoding='utf8')
old='var current={config:Project.copy(config),candidate:Project.copy(candidate)},previous=history.pop();'
assert old in s;s=s.replace(old,'var current={config:Project.copy(config)},previous=history.pop();')
old='config=previous.config;candidateConfig=JSON.stringify(config);candidate=previous.candidate;dirtyProject=true;'
assert old in s;s=s.replace(old,'candidateConfig="";config=previous.config;candidateTimer.restart();dirtyProject=true;')
old='previewUndo=previewUndo.concat([{config:Project.copy(config),candidate:Project.copy(candidate)}]).slice(-40);'
assert old in s;s=s.replace(old,'previewUndo=previewUndo.concat([{config:Project.copy(config)}]).slice(-40);')
p.write_text(s,encoding='utf8',newline='\n')
# Replace the current chapter while keeping all other chapters together.
guide=p.parent.parent/'Repairs/USER_GUIDE_CURRENT.md';text=guide.read_text(encoding='utf8')
chapter=(p.parent.parent/'Repairs/docs/EXPRESSION_049_GUIDE.md').read_text(encoding='utf8')
start=text.index('## 12. ');end=text.index('## 13. ',start)
guide.write_text(text[:start]+chapter.rstrip()+'\n\n'+text[end:],encoding='utf8',newline='\n')
