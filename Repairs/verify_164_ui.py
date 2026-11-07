from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1];N=R/'P2/native';H=R.parent/'muse3_dev/MuseScore';O=R/'P2/out/repair-164';manifest=O/'files.json';files=json.loads(manifest.read_text('utf8'));name='mtest/mscore/pluginhost/reference_163_tests.inc'
if name not in files:files[name]=hashlib.sha256((H/name).read_bytes()).hexdigest();(N/name).write_bytes((H/name).read_bytes())
p=N/name;t=p.read_text('utf8');old='''    QTest::mouseClick(panel->window(), Qt::LeftButton, Qt::NoModifier,
                      select->mapToScene(QPointF(15, select->height() + 42)).toPoint());'''
new='''    auto asObject=[](const QVariant& value){return value.canConvert<QJSValue>()?value.value<QJSValue>().toQObject():value.value<QObject*>();};
    auto popup=asObject(select->property("popup"));QVERIFY(popup);
    QTRY_VERIFY(popup->property("visible").toBool());
    auto content=asObject(popup->property("contentItem"));QVERIFY(content);
    QQuickItem* target=nullptr;
    for(auto candidate:content->findChildren<QQuickItem*>())if(candidate->property("text").toString()==QString::fromUtf8("范围：始终显示")&&candidate->isVisible()){target=candidate;break;}
    QVERIFY(target);
    QTest::mouseClick(target->window(),Qt::LeftButton,Qt::NoModifier,target->mapToScene(QPointF(target->width()/2,target->height()/2)).toPoint());'''
if old in t:t=t.replace(old,new,1);p.write_text(t,encoding='utf8',newline='\n')
manifest.write_text(json.dumps(files,indent=2),encoding='utf8')
p=N/'mtest/mscore/pluginhost/tst_pluginhost.cpp';t=p.read_text('utf8');t=t.replace('      void scoreVideoLong164();','      void scoreVideoWorkspace164();\n      void scoreVideoLong164();') if 'void scoreVideoWorkspace164();' not in t else t;p.write_text(t,encoding='utf8',newline='\n')
