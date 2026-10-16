from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
p=ROOT/'ArrangementAssistant/ArrangementAssistant_MS3.qml';s=p.read_text(encoding='utf8')
start=s.index('    RowLayout {\n        id:summary;');end=s.index('    Item {\n        id:details',start)
row=s[start:end].replace('id:summary;parent:root.dualSummaryActive?root.summaryPanelHost:root','id:summary')
loaders='''    Loader {
        id:primarySummary;anchors.fill:parent;active:root.ribbon;sourceComponent:summaryComponent
    }
    Loader {
        id:auxiliarySummary;parent:typeof root.summaryPanelHost!=="undefined"?root.summaryPanelHost:null
        anchors.fill:parent;active:root.dualSummaryActive;sourceComponent:summaryComponent
    }
    Component {
        id:summaryComponent
'''
s=s[:start]+loaders+''.join('    '+line+'\n' for line in row.rstrip().splitlines())+'    }\n'+s[end:]
p.write_text(s,encoding='utf8',newline='\n')
p=ROOT/'Repairs/native/mscore/plugin/qmlplugin.cpp';s=p.read_text(encoding='utf8')
s=s.replace('#include <QQuickView>\n#include <QQmlEngine>\n#include <QQmlComponent>\n','')
start=s.index('namespace {\nQQuickWindow* createWorkflowPanelWindow');end=s.index('//---------------------------------------------------------',start)
s=s[:start]+s[end:]
s=s.replace('createWorkflowPanelWindow(this)','new QQuickWindow()')
p.write_text(s,encoding='utf8',newline='\n')
