from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;N=ROOT/'Repairs/native';HOST=ROOT.parent/'muse3_dev/MuseScore'
def mirror(name):
 p=N/name
 if not p.exists():p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((HOST/name).read_bytes())
 return p
def edit(p,old,new):
 s=p.read_text(encoding='utf8');assert old in s,str(p)+' missing '+old[:60];p.write_text(s.replace(old,new),encoding='utf8',newline='\n')
p=mirror('mscore/notepreview.h');edit(p,'      QPointF anchor;','      QPointF anchor, leaderAnchor;\n      bool leader = false;');edit(p,'&& anchor == other.anchor && spatium == other.spatium','&& anchor == other.anchor && leaderAnchor == other.leaderAnchor && leader == other.leader && spatium == other.spatium')
p=mirror('mscore/plugin/api/scoreobserver.cpp');edit(p,'entry.anchor=note->canvasPos();entry.spatium=sp;','entry.anchor=note->canvasPos();entry.spatium=sp;\n            entry.leader=value.value("leader",false).toBool();entry.leaderAnchor=note->canvasBoundingRect().center();')
p=mirror('mscore/workflow/chordoverlay.cpp');edit(p,'#include <QPainter>','#include <QPainter>\n#include <QLineF>');edit(p,'            painter.save();painter.translate(box.topLeft());','''            if(entry.leader){
                  const auto source=entry.leaderAnchor;
                  const QPointF edge(qBound(box.left(),source.x(),box.right()),qBound(box.top(),source.y(),box.bottom()));
                  const QLineF line(source,edge);
                  if(line.length()>entry.spatium){auto color=entry.chordColor;color.setAlpha(100);painter.setPen(QPen(color,entry.spatium*.06));painter.drawLine(line.pointAt(qMin(.5,entry.spatium*.6/line.length())),edge);}
                  }
            painter.save();painter.translate(box.topLeft());''')
p=ROOT/'ArrangementAssistant/ArrangementAssistant_MS3.qml';edit(p,'if(problemHint.visible)positionProblemHint()','if(problemHint&&problemHint.visible)positionProblemHint()')
edit(p,'clip:true;model:root.nearbyIssues\n                delegate:','clip:true;model:root.nearbyIssues\n                ScrollBar.vertical:ScrollBar {}\n                delegate:')
