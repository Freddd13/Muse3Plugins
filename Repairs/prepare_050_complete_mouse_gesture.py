from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
p=ROOT/'ArrangementAssistant/ArrangementAssistant_MS3.qml';s=p.read_text(encoding='utf8')
start=s.index('    Loader {\n        id:primarySummary;');end=s.index('    Item {\n        id:details',start)
rowStart=s.index('        RowLayout {\n            id:summary',start)
rowEnd=s.rfind('    }',start,end)
row=s[rowStart:rowEnd];row='\n'.join(line[4:] if line.startswith('    ') else line for line in row.rstrip().splitlines())+'\n'
row=row.replace('id:summary\n','id:summary;parent:root.dualSummaryActive?root.summaryPanelHost:root\n')
s=s[:start]+row+s[end:];p.write_text(s,encoding='utf8',newline='\n')
p=ROOT/'Repairs/native/mtest/mscore/p1native/assistant_surface_tests.inc';s=p.read_text(encoding='utf8')
old='QTest::mouseDClick(view,Qt::LeftButton,Qt::NoModifier,hit);QTest::qWait(80);'
new='QTest::mouseClick(view,Qt::LeftButton,Qt::NoModifier,hit);QTest::mouseDClick(view,Qt::LeftButton,Qt::NoModifier,hit);QTest::mouseRelease(view,Qt::LeftButton,Qt::NoModifier,hit);QTest::qWait(80);'
assert old in s;s=s.replace(old,new)
s=s.replace('qInfo()<<"window"<<item->window()->isVisible()', 'qInfo()<<"mouse state"<<QGuiApplication::mouseButtons()<<QWidget::mouseGrabber();qInfo()<<"window"<<item->window()->isVisible()')
p.write_text(s,encoding='utf8',newline='\n')
