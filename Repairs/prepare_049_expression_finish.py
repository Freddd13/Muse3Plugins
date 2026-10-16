from pathlib import Path
p=Path(__file__).resolve().parent.parent/'PerformanceExpression/PerformanceExpression_MS3.qml'
s=p.read_text(encoding='utf8')
s=s.replace('if(response.error){fail(response.error);return;}appliedProgress=Progress.record(appliedProgress,values);readApplied(', 'if(response.error){fail(response.error);return;}values.velocity=response.appliedVelocity||values.velocity;appliedProgress=Progress.record(appliedProgress,values);readApplied(')
old='onVisibleChanged:if(!visible){cancel();if(observer&&typeof observer.cancelPerformanceMidi==="function")observer.cancelPerformanceMidi()}'
new='onVisibleChanged:{if(!visible){candidateTimer.stop();cancel();if(observer&&typeof observer.cancelPerformanceMidi==="function")observer.cancelPerformanceMidi()}else if(candidate&&previewUpdating)candidateTimer.restart()}'
assert old in s;s=s.replace(old,new)
p.write_text(s,encoding='utf8',newline='\n')
