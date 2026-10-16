from pathlib import Path
p=Path(__file__).resolve().parent/'native/mtest/mscore/p1native/assistant_surface_tests.inc'
s=p.read_text(encoding='utf8')
old='QSignalSpy clicked(item,SIGNAL(clicked()));QTest::mouseClick(item->window(),Qt::LeftButton,Qt::NoModifier,point.toPoint());qInfo()<<"clicked"<<clicked.count();return clicked.count()==1;'
new='''QSignalSpy clicked(item,SIGNAL(clicked()));
      qInfo()<<"window"<<item->window()->isVisible()<<item->window()->isExposed()<<item->window()->isActive()<<"button"<<item->size()<<item->parentItem()->size();
      auto hit=item->window()->contentItem();QPointF local=point;for(int depth=0;depth<12;++depth){auto child=hit->childAt(local.x(),local.y());if(!child)break;local=child->mapFromItem(hit,local);hit=child;qInfo()<<"hit"<<hit->metaObject()->className()<<hit->objectName()<<hit->isEnabled();}
      item->window()->requestActivate();QTest::qWait(30);QTest::mouseMove(item->window(),point.toPoint());QTest::mousePress(item->window(),Qt::LeftButton,Qt::NoModifier,point.toPoint());QTest::qWait(25);qInfo()<<"pressed"<<item->property("pressed");QTest::mouseRelease(item->window(),Qt::LeftButton,Qt::NoModifier,point.toPoint());QTest::qWait(30);qInfo()<<"clicked"<<clicked.count();return clicked.count()==1;'''
assert old in s;s=s.replace(old,new);p.write_text(s,encoding='utf8',newline='\n')
