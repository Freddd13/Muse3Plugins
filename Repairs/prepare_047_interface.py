"""Arrange the regional writing panel around save, try, switch and listen."""
from pathlib import Path
ROOT=Path(__file__).resolve().parent
HOST=Path('E:/programming/funcodes/muse3_dev/MuseScore')
def replace(s,old,new):
    if new in s:return s
    if s.count(old)!=1:raise RuntimeError('Check source: '+old[:80])
    return s.replace(old,new,1)
def apply():
    for name in ['mscore/workflow/regionalcontrols.cpp','mscore/workflow/regionalcontrols.h']:
        src=ROOT/'native'/name;dst=HOST/name
        if dst.exists() and dst.read_bytes()!=src.read_bytes():raise RuntimeError('Merge '+name)
        dst.write_bytes(src.read_bytes())
    p=HOST/'mscore/workflow/regionalpanel.h'
    s=p.read_text(encoding='utf-8').replace('#pragma once','#pragma once\n#include <QString>')
    s=s.replace('void showRegionalVariantPanel();','void showRegionalVariantPanel(const QString& group = QString());')
    p.write_text(s,encoding='utf-8',newline='\n')
    p=HOST/'mscore/workflow/regionalpanel.cpp';s=p.read_text(encoding='utf-8')
    s=replace(s,'#include "regionalpanel.h"','#include "regionalpanel.h"\n#include "regionalcontrols.h"\n#include <QMenu>\n#include <QToolButton>\n#include <QHBoxLayout>\n#include <QScrollArea>')
    s=replace(s,'      QLabel *_status;','      QLabel *_status;\n      QLabel *_scope;\n      QHBoxLayout *_choices;')
    a=s.index('      void refresh() {')
    s=s[:a]+'''      void choices() {
            while(auto item=_choices->takeAt(0)){if(item->widget())item->widget()->deleteLater();delete item;}
            auto g=selectedGroup();
            if(g.isEmpty()){_scope->setText(tr("选中一段乐谱，点“保存为A”开始。"));return;}
            QString current;for(auto entry:g.value("variants").toList())if(entry.toMap().value("id")==g.value("active"))current=entry.toMap().value("name").toString();
            auto first=score()->tick2measure(Fraction::fromTicks(g.value("start").toInt())),last=score()->tick2measure(Fraction::fromTicks(g.value("end").toInt()-1));
            _scope->setText(tr("%1 · 第%2–%3小节\\n正在编辑：%4").arg(g.value("name").toString()).arg(first?first->no()+1:0).arg(last?last->no()+1:0).arg(current));
            for(auto entry:g.value("variants").toList()) {
                  auto v=entry.toMap();auto button=new QPushButton(this);button->setObjectName("regionalQuick/"+v.value("id").toString());button->setText(button->fontMetrics().elidedText(v.value("name").toString(),Qt::ElideRight,110));button->setToolTip(v.value("name").toString());button->setCheckable(true);button->setChecked(v.value("id")==g.value("active"));_choices->addWidget(button);
                  connect(button,&QPushButton::clicked,this,[this,g,v]{selectTree(g.value("id").toString(),v.value("id").toString());switchTo();});
                  }
            _choices->addStretch();
            }
''' +s[a:]
    s=replace(s,'            else if (_tree->topLevelItemCount())\n                  _tree->setCurrentItem(_tree->topLevelItem(0));',
                '            else if (_tree->topLevelItemCount())\n                  _tree->setCurrentItem(_tree->topLevelItem(0));\n            choices();')
    s=replace(s,'                              flags << tr("普通版主方案");','                              flags << tr("主方案");')
    s=replace(s,'                        child->setData(0, Qt::UserRole, v.value("id"));','                        child->setData(0, Qt::UserRole, v.value("id"));\n                        if(v.value("id")==g.value("active")){auto font=child->font(0);font.setBold(true);child->setFont(0,font);}')
    s=replace(s,'QLineEdit::Normal, tr("B · 试写"), &ok);','QLineEdit::Normal, QString(QChar(\'A\'+qMin(25,selectedGroup().value("variants").toList().size())))+tr(" · 新写法"), &ok);')
    a=s.index('            auto help = new QLabel(',s.index('explicit RegionalPanel('));b=s.index('            _tree = new QTreeWidget(this);',a)
    s=s[:a]+'''            auto help=new QLabel(tr("保存当前写法为A，再增加B。修改后，点写法名称切换比较。Ctrl+S保存全部写法。"),this);help->setWordWrap(true);layout->addWidget(help);
            auto primary=new QHBoxLayout;layout->addLayout(primary);
            auto button=[&](QHBoxLayout* row,const QString& text,const char* id,auto call){auto b=new QPushButton(text,this);b->setObjectName(id);row->addWidget(b);connect(b,&QPushButton::clicked,this,call);return b;};
            button(primary,tr("保存为A"),"regionalCreateButton",[this]{create();});
            button(primary,tr("增加写法"),"regionalCopy",[this]{copy();});
            auto more=new QToolButton(this);more->setText(tr("更多"));more->setObjectName("regionalMore");more->setPopupMode(QToolButton::InstantPopup);auto menu=new QMenu(more);more->setMenu(menu);primary->addWidget(more);
            auto action=[&](const QString& text,const char* id,auto call){auto a=menu->addAction(text);a->setObjectName(id);connect(a,&QAction::triggered,this,call);};
            action(tr("改名…"),"regionalRename",[this]{rename();});
            action(tr("扩大范围…"),"regionalExpand",[this]{expand();});
            menu->addSeparator();
            action(tr("设为主方案"),"regionalMain",[this]{mainChoice();});
            action(tr("显示主方案组合"),"regionalShowMain",[this]{showMain();});
            action(tr("导出普通版副本…"),"regionalOrdinary",[this]{ordinary();});
            action(tr("导入旧写法…"),"regionalImport",[this]{importLegacy();});
            menu->addSeparator();auto controls=menu->addAction(tr("谱上显示切换按钮"));controls->setObjectName("regionalScoreButtons");controls->setCheckable(true);controls->setChecked(regionalControlsVisible());connect(controls,&QAction::toggled,this,[](bool checked){setRegionalControlsVisible(checked);});
            _scope=new QLabel(this);_scope->setObjectName("regionalCurrent");_scope->setWordWrap(true);layout->addWidget(_scope);
            auto strip=new QScrollArea(this);strip->setWidgetResizable(true);strip->setFixedHeight(58);strip->setVerticalScrollBarPolicy(Qt::ScrollBarAlwaysOff);auto host=new QWidget(strip);_choices=new QHBoxLayout(host);_choices->setContentsMargins(0,0,0,0);_choices->setSizeConstraint(QLayout::SetMinimumSize);strip->setWidget(host);layout->addWidget(strip);
''' +s[b:]
    s=replace(s,'            _status = new QLabel(tr("先选择谱段，再建立方案组。"), this);',
                '            connect(_tree,&QTreeWidget::currentItemChanged,this,[this]{choices();});\n            auto transport=new QHBoxLayout;layout->addLayout(transport);button(transport,tr("切换所选写法"),"regionalSwitch",[this]{switchTo();});button(transport,tr("从同处听"),"regionalAudition",[this]{audition();});\n            _status = new QLabel(tr("选中要尝试的几小节，点“保存为A”。"), this);')
    s=replace(s,'            _status->setWordWrap(true);','            _status->setWordWrap(true);\n            _status->setMinimumHeight(48);')
    s=replace(s,'      explicit RegionalPanel(QWidget *parent) : QWidget(parent) {','      void focusGroup(const QString& id){refresh();for(auto value:RegionalVariants::state(score()).value("groups").toList())if(value.toMap().value("id").toString()==id){selectTree(id,value.toMap().value("active").toString());break;}}\n      explicit RegionalPanel(QWidget *parent) : QWidget(parent) {')
    s=s.replace('void showRegionalVariantPanel() {','void showRegionalVariantPanel(const QString& group) {')
    s=replace(s,'      dock->show();\n      dock->raise();','      dock->show();\n      dock->raise();\n      if(!group.isEmpty())static_cast<RegionalPanel*>(dock->widget())->focusGroup(group);')
    p.write_text(s,encoding='utf-8',newline='\n')
    p=HOST/'mscore/plugin/plugin.cmake';s=p.read_text(encoding='utf-8')
    s=replace(s,'    ${PROJECT_SOURCE_DIR}/mscore/workflow/regionalpanel.h','    ${PROJECT_SOURCE_DIR}/mscore/workflow/regionalpanel.h\n    ${PROJECT_SOURCE_DIR}/mscore/workflow/regionalcontrols.cpp\n    ${PROJECT_SOURCE_DIR}/mscore/workflow/regionalcontrols.h');p.write_text(s,encoding='utf-8',newline='\n')
    p=HOST/'mscore/scoreview.cpp';s=p.read_text(encoding='utf-8');s=replace(s,'#include "scoreview.h"','#include "scoreview.h"\n#ifdef SCRIPT_INTERFACE\n#include "workflow/regionalcontrols.h"\n#endif');s=replace(s,'      paintTopChordPreview(vp);','      paintTopChordPreview(vp);\n#ifdef SCRIPT_INTERFACE\n      updateRegionalControls(this);\n#endif');p.write_text(s,encoding='utf-8',newline='\n')
    for name in ['mscore/workflow/regionalpanel.cpp','mscore/workflow/regionalpanel.h','mscore/scoreview.cpp']:(ROOT/'native'/name).write_bytes((HOST/name).read_bytes())
if __name__=='__main__':apply()
