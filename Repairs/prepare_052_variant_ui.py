from pathlib import Path
R=Path(__file__).resolve().parent/'native'
p=R/'mscore/workflow/regionalpanel.cpp';s=p.read_text(encoding='utf8');s=s.replace('#include "regionalcontrols.h"','#include "regionalcontrols.h"\n#include "regionalcomparison.h"\n#include "libmscore/undo.h"\n#include <QCheckBox>\n#include <QComboBox>')
s=s.replace('      QTimer _refresh;','''      QTimer _refresh;
      QCheckBox *_compare,*_listen;
      QComboBox *_compareWith,*_combinations;
      QTreeWidget *_differences;
      std::unique_ptr<MasterScore> _other;
      ScoreContentState _comparedState;
      QString _comparedGroup,_comparedVariant;
      QPointer<ScoreView> _compareView;
      bool _refreshing=false;
      void clearDifference(){if(_compareView)showRegionalDifference(_compareView,nullptr,{});_other.reset();_comparedGroup.clear();_comparedVariant.clear();}
      void compare(){
            if(_refreshing)return;
            _compareWith->setVisible(_compare->isChecked());_differences->setVisible(_compare->isChecked());
            if(!_compare->isChecked()||!score()||!isVisible()){clearDifference();return;}
            const auto target=_compareWith->currentData().toString();auto view=mscore->currentScoreView();
            if(target.isEmpty()||!view||view->score()!=score()){clearDifference();return;}
            if(seq&&seq->isPlaying())return;
            if(_other&&_compareView==view&&_comparedState==score()->state()&&_comparedGroup==group()&&_comparedVariant==target)return;
            clearDifference();QString problem;_other.reset(RegionalVariants::comparison(score(),group(),target,&problem));
            if(!_other){_status->setText(problem);return;}
            _comparedState=score()->state();_comparedGroup=group();_comparedVariant=target;_compareView=view;
            const auto rows=RegionalVariants::differences(score(),_other.get(),group());_differences->clear();
            for(auto value:rows){const auto row=value.toMap();auto item=new QTreeWidgetItem(_differences,{tr("第%1小节 · 声部%2").arg(row.value("measure").toInt()).arg(row.value("track").toInt()%4+1),row.value("types").toStringList().join("、")});item->setData(0,Qt::UserRole,row);}
            showRegionalDifference(view,_other.get(),rows);_status->setText(rows.isEmpty()?tr("两种写法的音符、节奏、力度和附着标记相同。"):tr("%1处变化。谱面淡色显示另一写法，边框标出当前写法中变化的位置；点列表可定位。").arg(rows.size()));
            }
      void comparisonChoices(){
            _refreshing=true;const auto previous=_compareWith->currentData();const auto g=selectedGroup();
            _compareWith->clear();for(auto value:g.value("variants").toList()){auto v=value.toMap();if(v.value("id")!=g.value("active"))_compareWith->addItem(v.value("name").toString(),v.value("id"));}
            const int i=_compareWith->findData(previous);if(i>=0)_compareWith->setCurrentIndex(i);
            const auto combination=_combinations->currentData();_combinations->clear();_combinations->addItem(tr("选择组合…"),QString());
            for(auto value:RegionalVariants::state(score()).value("combinations").toList()){auto item=value.toMap();_combinations->addItem(item.value("name").toString(),item.value("id"));}
            const int c=_combinations->findData(combination);if(c>=0)_combinations->setCurrentIndex(c);_refreshing=false;compare();
            }
      void saveCombination(){
            if(!idle())return;bool ok=false;const auto name=QInputDialog::getText(this,tr("保存组合"),tr("组合名称（同名保存会更新选择）"),QLineEdit::Normal,_combinations->currentIndex()>0?_combinations->currentText():tr("组合%1").arg(_combinations->count()),&ok);
            if(!ok)return;const auto result=RegionalVariants::storeCombination(score(),name);report(result,tr("已保存各组当前写法。Ctrl+S保存到这份乐谱。"));if(result.value("ok").toBool()){comparisonChoices();_combinations->setCurrentIndex(_combinations->findData(result.value("id")));}
            }
''')
s=s.replace('            _choices->addStretch();','            _choices->addStretch();\n            if(_compareWith)comparisonChoices();')
s=s.replace('            if (master == _master && data == _last)\n                  return;','            if (master == _master && data == _last){compare();return;}')
start=s.index('      void switchTo() {');end=s.index('      void mainChoice()',start)
s=s[:start]+'''      void switchTo() {
            if(variant().isEmpty()){_status->setText(tr("请选中组内的一种写法。"));return;}
            const auto result=switchRegionalWriting(mscore->currentScoreView(),group(),variant());
            report(result,result.contains("playbackError")?tr("写法已切换。%1").arg(result.value("playbackError").toString()):regionalAuditionEnabled()?tr("正在从同一片段起点试听。"):tr("已切换写法，可以继续编辑。"));
      }
'''+s[end:]
start=s.index('            auto groups = RegionalVariants::state(score()).value("groups").toList();',s.index('      void showMain()'))
end=s.index('            _status->setText(',start)
s=s[:start]+'''            QVariantMap choices;for(auto value:RegionalVariants::state(score()).value("groups").toList()){auto g=value.toMap();choices[g.value("id").toString()]=g.value("main");}
            const auto result=RegionalVariants::selectMany(score(),choices);if(result.contains("error")){report(result,{});return;}
'''+s[end:]
s=s.replace('            _refresh.stop();\n      }','            _refresh.stop();clearDifference();\n      }')
s=s.replace('      explicit RegionalPanel(QWidget *parent) : QWidget(parent) {','      explicit RegionalPanel(QWidget *parent) : QWidget(parent),_compare(nullptr),_listen(nullptr),_compareWith(nullptr),_combinations(nullptr),_differences(nullptr) {')
anchor='            auto transport = new QHBoxLayout;'
insert='''            _compare=new QCheckBox(tr("显示差异"),this);_compare->setObjectName("regionalCompare");
            _compareWith=new QComboBox(this);_compareWith->setObjectName("regionalCompareWith");_compareWith->hide();
            auto comparisonRow=new QHBoxLayout;comparisonRow->addWidget(_compare);comparisonRow->addWidget(_compareWith,1);layout->addLayout(comparisonRow);
            _differences=new QTreeWidget(this);_differences->setObjectName("regionalDifferences");_differences->setHeaderLabels({tr("位置"),tr("变化")});_differences->setMaximumHeight(160);_differences->hide();layout->addWidget(_differences);
            connect(_compare,&QCheckBox::toggled,this,[this]{comparisonChoices();});connect(_compareWith,QOverload<int>::of(&QComboBox::currentIndexChanged),this,[this]{compare();});
            connect(_differences,&QTreeWidget::itemClicked,this,[this](QTreeWidgetItem* item,int){const auto row=item->data(0,Qt::UserRole).toMap();PluginAPI::Score wrapped(score());_observer->setScore(&wrapped);_observer->navigateWorkflow({{"start",row.value("tick")},{"end",row.value("tick").toInt()+1},{"firstTrack",row.value("track")}},false);});
            auto combinationRow=new QHBoxLayout;_combinations=new QComboBox(this);_combinations->setObjectName("regionalCombinations");combinationRow->addWidget(_combinations,1);button(combinationRow,tr("保存组合…"),"regionalSaveCombination",[this]{saveCombination();});layout->addLayout(combinationRow);
            connect(_combinations,QOverload<int>::of(&QComboBox::activated),this,[this](int i){if(i<=0||!idle())return;report(RegionalVariants::selectCombination(score(),_combinations->itemData(i).toString()),tr("已切换整组选择；Ctrl+Z可一起恢复。"));if(regionalAuditionEnabled())audition();});
            _listen=new QCheckBox(tr("试听比较：切换后从同处听"),this);_listen->setObjectName("regionalAuditionCompare");_listen->setChecked(regionalAuditionEnabled());layout->addWidget(_listen);connect(_listen,&QCheckBox::toggled,this,[](bool value){setRegionalAuditionEnabled(value);});
'''
assert anchor in s;s=s.replace(anchor,insert+anchor);p.write_text(s,encoding='utf8',newline='\n')

p=R/'mscore/workflow/regionalcontrols.cpp';s=p.read_text(encoding='utf8');s=s.replace('#include "regionalpanel.h"','#include "regionalpanel.h"\n#include "regionalcomparison.h"\n#include <QWheelEvent>')
a=s.index('            mscore->setCurrentScoreView(_view);');b=s.index('      void menu(',a)
s=s[:a]+'''            const auto result=switchRegionalWriting(_view,group,variant);
            if(result.contains("error"))QToolTip::showText(QCursor::pos(),result.value("error").toString(),_view);
            else if(result.contains("playbackError"))QToolTip::showText(QCursor::pos(),result.value("playbackError").toString(),_view);
      }
      bool eventFilter(QObject* object,QEvent* event)override{
            if(event->type()!=QEvent::Wheel)return QObject::eventFilter(object,event);auto wheel=static_cast<QWheelEvent*>(event);if(wheel->modifiers()!=Qt::ControlModifier)return false;
            auto score=_view?_view->score():nullptr;if(!score)return false;const auto key=object->property("regionalGroup").toString();
            for(auto value:RegionalVariants::state(score).value("groups").toList()){auto g=value.toMap();if(g.value("id").toString()!=key)continue;auto variants=g.value("variants").toList();if(variants.size()<2)break;
                  int index=0;for(int i=0;i<variants.size();++i)if(variants[i].toMap().value("id")==g.value("active"))index=i;
                  const int delta=wheel->angleDelta().y();if(!delta)break;index=(index+(delta<0?1:variants.size()-1))%variants.size();choose(key,variants[index].toMap().value("id").toString());wheel->accept();return true;}
            return false;
      }
'''+s[b:]
s=s.replace('                              button->setObjectName("regionalScoreSwitch/" + key);','                              button->setObjectName("regionalScoreSwitch/" + key);\n                              button->setProperty("regionalGroup",key);button->installEventFilter(this);')
s=s.replace('点击切换写法；当前修改会保存。','点击或Ctrl+滚轮切换写法；当前修改会保存。')
p.write_text(s,encoding='utf8',newline='\n')
