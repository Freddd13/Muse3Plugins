from pathlib import Path
repo=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
p=repo/'mscore/plugin/api/scoreobserver.cpp';s=p.read_text(encoding='utf-8')
old='                        if (!scratch) scratch=std::make_unique<Ms::MasterScore>(_score->style());'
assert old in s
s=s.replace(old,'''                        if (!scratch) {
                              scratch=std::make_unique<Ms::MasterScore>(_score->style());
                              // Scores without written Harmony may not yet have loaded their symbol list.
                              scratch->style().checkChordList();
                              }''',1)
with p.open('w',encoding='utf-8',newline='\n') as f:f.write(s)
p=repo/'mtest/mscore/pluginhost/tst_pluginhost.cpp';s=p.read_text(encoding='utf-8')
old='''            observer->setScore(&wrapped);
            auto descriptors=observer->snapshot'''
new='''            observer->setScore(&wrapped);
            // Freeze the plugin's background analysis while testing the observer layer directly.
            panel->setProperty("surfaceActive",false);observer->clearAllPreviews();
            auto descriptors=observer->snapshot'''
assert old in s;s=s.replace(old,new,1)
# A full redraw after clearing tests complete dirty-region restoration (no other plugin timer).
old='''            observer.clearAllPreviews();QCOMPARE(view->grab().toImage(),original);
            // Native P keyboard'''
new='''            observer.clearAllPreviews();view->update();QTest::qWait(10);
            QCOMPARE(view->grab().toImage(),original);
            // Native P keyboard'''
assert old in s;s=s.replace(old,new,1)
with p.open('w',encoding='utf-8',newline='\n') as f:f.write(s)
