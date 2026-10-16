from pathlib import Path
root=Path(__file__).resolve().parent;host=Path('E:/programming/funcodes/muse3_dev/MuseScore')
def patch(name,old,new):
 p=root/'native'/name;s=p.read_text(encoding='utf8')
 if new in s:return
 assert s.count(old)==1,(name,old[:80],s.count(old));s=s.replace(old,new);p.write_text(s,encoding='utf8',newline='\n');(host/name).write_bytes(p.read_bytes())
patch('mscore/performanceeditor/performanceeditor.cmake','      ${CMAKE_CURRENT_LIST_DIR}/expressioncompare.cpp','      ${CMAKE_CURRENT_LIST_DIR}/expressioncompare.cpp\n      ${CMAKE_CURRENT_LIST_DIR}/markvelocity.cpp\n      ${CMAKE_CURRENT_LIST_DIR}/markvelocity.h')
patch('mscore/performanceeditor/performanceeditor.h','            QVector<GeneratedVelocity> generatedVelocities;','            QVector<GeneratedVelocity> generatedVelocities;\n            QString dynamicText;')
patch('mscore/performanceeditor/performanceeditor.cpp','#include <QJsonDocument>','#include <QJsonDocument>\n#include "markvelocity.h"')
patch('mscore/performanceeditor/performanceeditor.cpp','      _relativeMax = 100; _tempoMax = 240; _measures.clear();','      const auto markNames=readMarkVelocityText(_score);\n      _relativeMax = 100; _tempoMax = 240; _measures.clear();')
patch('mscore/performanceeditor/performanceeditor.cpp','auto addChord = [this, tick, globalMethod, live, stablePlayback](Chord* chord)','auto addChord = [this, tick, globalMethod, live, stablePlayback,&markNames](Chord* chord)')
patch('mscore/performanceeditor/performanceeditor.cpp','auto& cached = _notes.back(); cached.baseMin = cached.baseMax = cached.base;','auto& cached = _notes.back(); cached.baseMin = cached.baseMax = cached.base;cached.dynamicText=markVelocityAt(markNames,note->track(),tick);')
patch('mscore/performanceeditor/performanceux.cpp','tr("谱表 %1 · 声部 %2 · 记号力度 %3").arg(staff+1).arg(n.track%VOICES+1).arg(n.base)','tr("谱表 %1 · 声部 %2 · %3 %4").arg(staff+1).arg(n.track%VOICES+1).arg(n.dynamicText.isEmpty()?tr("记号力度"):n.dynamicText).arg(n.base)')
name='mscore/workflow/scoreworkflow.cpp';p=root/'native'/name
if not p.exists():p.write_bytes((host/name).read_bytes())
s=p.read_text(encoding='utf8')
s=s.replace('#include "libmscore/notevelocity.h"','#include "libmscore/notevelocity.h"\n#include "mscore/performanceeditor/markvelocity.h"',1)
s=s.replace('QVector<QPair<int,int>> curves;QCache','QVector<QPair<int,int>> curves;MarkVelocityText marks;QCache',1)
s=s.replace('cache.clock.setRelTempo(1.0);cache.curves.clear();','cache.clock.setRelTempo(1.0);cache.marks=readMarkVelocityText(_score);cache.curves.clear();',1)
s=s.replace('n.insert("velocityType",int(note->veloType()));','n.insert("velocityMark",markVelocityAt(cache.marks,note->track(),n.value("tick").toInt()));\n  n.insert("velocityType",int(note->veloType()));',1)
p.write_text(s,encoding='utf8',newline='\n');(host/name).write_bytes(p.read_bytes())
for name in ['mscore/performanceeditor/markvelocity.h','mscore/performanceeditor/markvelocity.cpp']:(host/name).write_bytes((root/'native'/name).read_bytes())
print('Dynamic names follow their actual staff/part/system range')
