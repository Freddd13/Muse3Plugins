"""Keep comparison, audition and applying values in the editor workflow."""
from pathlib import Path
ROOT=Path(__file__).resolve().parent
HOST=Path('E:/programming/funcodes/muse3_dev/MuseScore')
def change(s,old,new):
    if new in s:return s
    if s.count(old)!=1:raise RuntimeError('Check editor source: '+old[:80])
    return s.replace(old,new,1)
def apply():
    p=HOST/'mscore/workflow/workflowexpression.cpp';s=p.read_text(encoding='utf-8')
    s=change(s,'#include <QAction>','#include <QAction>\n#include <QToolButton>\n#include <QDockWidget>')
    s=change(s,' else mscore->showPerformanceEditor(true);\n return {{"ok",true}};',' mscore->showPerformanceEditor(true);\n if(auto toggle=mscore->findChild<QToolButton*>("performanceWorkflowToggle"))toggle->setChecked(true);\n if(auto dock=mscore->findChild<QDockWidget*>("performanceEditorDock")){dock->show();dock->raise();}\n return {{"ok",true}};')
    p.write_text(s,encoding='utf-8',newline='\n')
    p=HOST/'mscore/performanceeditor/workflowlanes.h';s=p.read_text(encoding='utf-8')
    s=change(s,'struct Hit {QRectF bounds;QString scoreId,midiId;int track=-1;};','struct Hit {QRectF bounds;QString scoreId,midiId;int track=-1;QString tooltip;};')
    s=change(s,'      void mousePressEvent(QMouseEvent*)override;','      void mousePressEvent(QMouseEvent*)override;\n      void mouseMoveEvent(QMouseEvent*)override;')
    p.write_text(s,encoding='utf-8',newline='\n')
    p=HOST/'mscore/performanceeditor/workflowlanes.cpp';s=p.read_text(encoding='utf-8')
    s=change(s,'                  for(auto it=from;it!=matches.cend();++it){auto m=it->toMap();',
               '                  QHash<int,int> counts,onsetSlots;for(auto it=from;it!=matches.cend() && it->toMap().value("tick").toInt()<=until;++it)++counts[it->toMap().value("tick").toInt()];\n                  for(auto it=from;it!=matches.cend();++it){auto m=it->toMap();')
    s=change(s,'                        double mx=x(performanceTick(', '                        const int slot=onsetSlots[m.value("tick").toInt()]++;const int offsets[8]={0,-6,6,-10,10,-3,3,13};const int offset=offsets[slot%8];const double sy=y+13+offset,my=y+40+offset;\n                        double mx=x(performanceTick(')
    s=s.replace('QPointF(px,y+13),QPointF(mx,y+37)','QPointF(px,sy),QPointF(mx,my)').replace('QPointF(px,y+13),4,4','QPointF(px,sy),3,3').replace('QPointF(mx,y+37),4,4','QPointF(mx,my),3,3')
    s=change(s,'                        _hits.append({QRectF(px-7,y+5,14,18),m.value("scoreId").toString(),QString(),-1});_hits.append({QRectF(mx-7,y+28,14,18),m.value("scoreId").toString(),m.value("midiId").toString(),-1});',
               '''                        const auto original=m.value("original").toMap();auto target=targets.value(m.value("scoreId").toString()).toMap();const int pitch=m.value("pitch",original.value("pitch",60)).toInt();static const QStringList names={"C","C♯","D","D♯","E","F","F♯","G","G♯","A","A♯","B"};
                        const auto tooltip=tr("%1%2 · 谱表%3／声部%4\\n原力度 %5 → 新力度 %6\\n演奏时间 %7 秒").arg(names[qBound(0,pitch,127)%12]).arg(pitch/12-1).arg(m.value("track").toInt()/4+1).arg(m.value("track").toInt()%4+1).arg(original.value("velocity",64).toInt()).arg(target.value("target",m.value("velocity",64)).toInt()).arg(m.value("seconds").toDouble(),0,'f',3);
                        _hits.append({QRectF(px-6,sy-6,12,12),m.value("scoreId").toString(),QString(),-1,tooltip});_hits.append({QRectF(mx-6,my-6,12,12),m.value("scoreId").toString(),m.value("midiId").toString(),-1,tooltip});''')
    s=change(s,'p.setBrush(Qt::NoBrush);p.drawRect(QRectF(px-4,y+126-oldValue*.5,8,oldValue*.5));p.setBrush(c);p.drawRect(QRectF(px-2,y+126-target*.5,4,target*.5));',
               'const double vx=px+(slot-(counts[m.value("tick").toInt()]-1)*.5)*9;p.setBrush(Qt::NoBrush);p.drawRect(QRectF(vx-4,y+126-oldValue*.5,8,oldValue*.5));p.setBrush(c);p.drawRect(QRectF(vx-2,y+126-target*.5,4,target*.5));')
    s=change(s,'      for(auto hit:_hits)if(hit.bounds.contains(event->pos())){','      const Hit* nearest=nullptr;double distance=1e12;for(const auto& candidate:_hits)if(candidate.bounds.contains(event->pos())){const auto delta=candidate.bounds.center()-event->pos();const double cost=delta.x()*delta.x()+delta.y()*delta.y();if(cost<distance){distance=cost;nearest=&candidate;}}\n      if(nearest){const auto hit=*nearest;')
    s=change(s,'void WorkflowLanes::operation(const QString& action)',
               'void WorkflowLanes::mouseMoveEvent(QMouseEvent* event){const Hit* nearest=nullptr;double distance=1e12;for(const auto& hit:_hits)if(hit.bounds.contains(event->pos())&&!hit.tooltip.isEmpty()){const auto delta=hit.bounds.center()-event->pos();const double cost=delta.x()*delta.x()+delta.y()*delta.y();if(cost<distance){distance=cost;nearest=&hit;}}if(nearest)QToolTip::showText(event->globalPos(),nearest->tooltip,this);else QToolTip::hideText();}\nvoid WorkflowLanes::operation(const QString& action)')
    a=s.index('      for(auto item:QList<QPair<QString,QString>>{{QObject::tr("确认"),"confirm"}')
    b=s.index('      row->addStretch();',a)
    s=s[:a]+'''      for(auto item:QList<QPair<QString,QString>>{{QObject::tr("试听原来"),"auditionOriginal"},{QObject::tr("试听新效果"),"auditionCandidate"},{QObject::tr("使用力度"),"apply"}}){auto b=new QToolButton(panel);b->setText(item.first);b->setObjectName("workflow"+item.second);QObject::connect(b,&QToolButton::clicked,lane,[lane,item,mode]{lane->operation(item.second=="apply"?(mode->currentIndex()==1?"applyTempo":"applyVelocity"):item.second);});if(item.second=="apply")QObject::connect(mode,QOverload<int>::of(&QComboBox::currentIndexChanged),b,[b](int i){b->setText(i?QObject::tr("使用速度"):QObject::tr("使用力度"));});row->addWidget(b);}
      auto more=new QToolButton(panel);more->setText(QObject::tr("更多"));more->setPopupMode(QToolButton::InstantPopup);auto menu=new QMenu(more);more->setMenu(menu);row->addWidget(more);
      for(const char* name:{"reference-audio-play","reference-joint-play"})menu->addAction(getAction(name));
      for(auto item:QList<QPair<QString,QString>>{{QObject::tr("确认对应"),"confirm"},{QObject::tr("连接所选两音"),"connect"},{QObject::tr("固定对齐点"),"anchor"},{QObject::tr("解除对应"),"unlink"}}){auto action=menu->addAction(item.first);action->setObjectName("workflow"+item.second);QObject::connect(action,&QAction::triggered,lane,[lane,item]{lane->operation(item.second);});}
      auto legend=new QLabel(QObject::tr("上排：谱面起音；下排：演奏起音。力度空心框是原值，实心条是新值。指向点可查看音名和数值。"),panel);legend->setWordWrap(true);layout->insertWidget(1,legend);
''' +s[b:]
    p.write_text(s,encoding='utf-8',newline='\n')
    for name in ['mscore/workflow/workflowexpression.cpp','mscore/performanceeditor/workflowlanes.h','mscore/performanceeditor/workflowlanes.cpp']:(ROOT/'native'/name).write_bytes((HOST/name).read_bytes())
if __name__=='__main__':apply()
