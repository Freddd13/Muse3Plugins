from pathlib import Path
R=Path(__file__).resolve().parent;P=R.parent;H=P.parent/'muse3_dev/MuseScore'
p=P/'ArrangementAssistant/ArrangementAssistant_MS3.qml';s=p.read_text(encoding='utf8')
s=s.replace('    property var issues:[]','''    property var issues:[]
    property int rangeChoice:0
    property int categoryFilter:0
    property int severityFilter:0
    property var filteredIssues:issues.filter(function(issue){return (!categoryFilter||issue.type===["","harmony","counterpoint","playability"][categoryFilter])&&(!severityFilter||issue.severity===["","需核查","注意","提示"][severityFilter])})
    function issueStep(direction){var row=filteredIssues.findIndex(function(i){return root.current&&i.id===root.current.id});row+=direction;if(row>=0&&row<filteredIssues.length){currentIssueIndex=issues.findIndex(function(i){return i.id===root.filteredIssues[row].id});locate()}}''',1)
# issue fields are category (see issue() in Rules.js).
s=s.replace('issue.type===["","harmony"','issue.category===["","harmony"')
s=s.replace('onClicked:root.start(root.requested)','onClicked:{root.whole=root.rangeChoice===1;root.start(root.rangeChoice===2&&root.requested)}')
s=s.replace('text:root.whole?"改查钢琴全谱":"改查当前选区"','text:"检查当前选区"').replace('onClicked:root.start(false)','onClicked:{root.rangeChoice=0;root.whole=false;root.start(false)}')
s=s.replace('model:["下次检查：选区／当前小节","下次检查：钢琴全谱"];Layout.fillWidth:true;onActivated:root.whole=currentIndex===1','model:["当前选区／小节","钢琴全谱","保留本次范围"];currentIndex:root.rangeChoice;Layout.fillWidth:true;onActivated:{root.rangeChoice=currentIndex;root.whole=currentIndex===1}')
s=s.replace('            ListView {\n                id:list;', '''            RowLayout {Layout.fillWidth:true
                Desk.DeskComboBox {objectName:"arrangementCategoryFilter";Layout.fillWidth:true;model:["全部问题","和声 · "+root.counts.harmony,"对位 · "+root.counts.counterpoint,"可弹性 · "+root.counts.playability];currentIndex:root.categoryFilter;onActivated:root.categoryFilter=currentIndex}
                Desk.DeskComboBox {objectName:"arrangementSeverityFilter";model:["全部程度","需核查","注意","提示"];currentIndex:root.severityFilter;onActivated:root.severityFilter=currentIndex}
            }
            ListView {
                id:list;''',1)
s=s.replace('currentIndex:root.currentIssueIndex;onCurrentIndexChanged:if(currentIndex>=0&&count>0)root.currentIssueIndex=currentIndex;', 'currentIndex:root.filteredIssues.findIndex(function(i){return root.current&&i.id===root.current.id});')
s=s.replace('clip:true;model:root.issues;spacing:1','clip:true;model:root.filteredIssues;spacing:1')
s=s.replace('root.currentIssueIndex=index;if(!root.observer','root.currentIssueIndex=root.issues.findIndex(function(i){return i.id===modelData.id});if(!root.observer')
s=s.replace('onClicked:{root.currentIssueIndex--;root.locate()}','onClicked:root.issueStep(-1)').replace('onClicked:{root.currentIssueIndex++;root.locate()}','onClicked:root.issueStep(1)')
s=s.replace('root.currentIssueIndex=issues.length?0:-1;work.stop()', 'root.currentIssueIndex=issues.length?0:-1;rangeChoice=2;work.stop()')
s=s.replace('''        problemHint.x=Math.max(left,Math.min(right-problemHint.width,point.x+point.width+12))
        problemHint.y=Math.max(top,Math.min(bottom-problemHint.height,point.y+point.height+8))''','''        var box={x:point.measureX===undefined?point.x:point.measureX,y:point.measureY===undefined?point.y:point.measureY,w:point.measureWidth||point.width,h:point.measureHeight||point.height}
        var candidates=[{x:box.x+box.w+12,y:box.y},{x:box.x-problemHint.width-12,y:box.y},{x:box.x,y:box.y-problemHint.height-12},{x:box.x,y:box.y+box.h+12}]
        var best=null,cost=Infinity
        candidates.forEach(function(p){p.x=Math.max(left,Math.min(right-problemHint.width,p.x));p.y=Math.max(top,Math.min(bottom-problemHint.height,p.y));var overlap=Math.max(0,Math.min(p.x+problemHint.width,box.x+box.w)-Math.max(p.x,box.x))*Math.max(0,Math.min(p.y+problemHint.height,box.y+box.h)-Math.max(p.y,box.y));var value=overlap*100+Math.abs(p.x-box.x)+Math.abs(p.y-box.y);if(value<cost){cost=value;best=p}})
        if(best){problemHint.x=best.x;problemHint.y=best.y}''',1)
s=s.replace('                Label {text:"对位规则（预设可覆盖）";', '''                Desk.DeskButton {text:"低音程参考表…";onClicked:intervalLimits.open()}
                Label {text:"对位规则（预设可覆盖）";''',1)
at=s.rfind('\n}')
s=s[:at]+'''
    Popup {id:intervalLimits;parent:root;width:Math.min(360,root.width);height:Math.min(540,root.height);modal:true;focus:true
        background:Rectangle {color:theme.background;border.color:theme.line}
        ScrollView {anchors.fill:parent;clip:true
            ColumnLayout {width:intervalLimits.availableWidth
                Label {text:"低音排列参考";color:theme.text;font.bold:true}
                Label {text:"低端音低于表中位置时，提示试听清晰程度。踏板留下的声音也参与检查。";Layout.fillWidth:true;wrapMode:Text.WordWrap;color:theme.muted}
                Repeater {model:Object.keys(Rules.lowIntervalLimits)
                    RowLayout {property string interval:modelData;Layout.fillWidth:true
                        Label {text:Rules.lowIntervalNames[interval];Layout.fillWidth:true;color:theme.text}
                        Desk.DeskComboBox {model:Array.from({length:37},function(_,i){var pitch=i+24;return Harmony.sharpNames[pitch%12]+(Math.floor(pitch/12)-1)});currentIndex:(root.config.lowIntervalLimits||Rules.lowIntervalLimits)[interval]-24;onActivated:{var c=Rules.clone(root.config);if(!c.lowIntervalLimits)c.lowIntervalLimits=Rules.clone(Rules.lowIntervalLimits);c.lowIntervalLimits[interval]=currentIndex+24;root.config=c;root.persist();root.markDirty()}}
                    }
                }
                Label {text:'参考：<a href="https://nicechord.com/post/low-interval-limit/">好和弦·低音程限制</a>';textFormat:Text.RichText;onLinkActivated:Qt.openUrlExternally(link);color:theme.muted}
                RowLayout {Desk.DeskButton {text:"恢复参考表";onClicked:{var c=Rules.clone(root.config);c.lowIntervalLimits=Rules.clone(Rules.lowIntervalLimits);root.config=c;root.persist();root.markDirty()}}Desk.DeskButton {text:"关闭";onClicked:intervalLimits.close()}}
            }
        }
    }
'''+s[at:];p.write_bytes(s.encode())
# Stable harmony card and collapsible keyboard.
p=P/'HarmonyAssistant/PanelCard.qml';s=p.read_text(encoding='utf8').replace('    property real minimumBodyHeight: 0','    property real minimumBodyHeight: 0\n    property real fixedBodyHeight:0').replace('Math.max(minimumBodyHeight, body.implicitHeight)','(fixedBodyHeight>0?fixedBodyHeight:Math.max(minimumBodyHeight, body.implicitHeight))').replace('        spacing: 6','        height:parent.fixedBodyHeight>0?parent.fixedBodyHeight:implicitHeight\n        clip:parent.fixedBodyHeight>0\n        spacing: 6');p.write_bytes(s.encode())
p=P/'HarmonyAssistant/HarmonyAssistant_MS3.qml';s=p.read_text(encoding='utf8')
start=s.index('                    HarmonyLabel {width:',s.index('id:summaryCard'))
end=s.index('                    StableLabel {reservedLines:2; text:matchText',start)
s=s[:start]+'''                    Item {width:parent.width;height:44
                        HarmonyLabel {anchors.left:parent.left;anchors.verticalCenter:parent.verticalCenter;width:Math.min(parent.width,implicitWidth);height:Math.min(44,implicitHeight);observer:root.observer;chord:root.chordText;degree:root.degreeText;color:root.chordInk;pixels:24;gap:8;chordFont:["","Edwin","Arial"][configuration.chordFont];degreeFont:configuration.degreeFont;revision:root.analysisFingerprint}
                    }
'''+s[end:]
s=s.replace('minimumBodyHeight:settingsExpanded ? 190 : 156','fixedBodyHeight:settingsExpanded ? 230 : 200',1)
s=s.replace('                    objectName:"harmonyKeyboard"','                    heading:"实际音高";collapsed:configuration.collapsedSections.indexOf("pitches")>=0;onToggleRequested:root.toggleSection("pitches")\n                    objectName:"harmonyKeyboard"',1)
s=s.replace('UiLabel {text:"实际音高"; Layout.fillWidth:true;', 'UiLabel {text:"键盘范围"; Layout.fillWidth:true;',1)
p.write_bytes(s.encode())
print('0.55 panel sources prepared')
