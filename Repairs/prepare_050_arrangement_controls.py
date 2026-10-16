from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
p=ROOT/'ArrangementAssistant/ArrangementAssistant_MS3.qml';s=p.read_text(encoding='utf8')
def replace(old,new):
 global s
 assert old in s,old[:75];s=s.replace(old,new)
replace('anchors.right:parent.right;anchors.margins:4;height:28;spacing:4','anchors.right:parent.right;anchors.margins:root.dualSummaryActive?0:4;height:28;spacing:4')
replace('''                Desk.DeskButton {text:"设置";onClicked:settings.open()}
            }
            Label {Layout.fillWidth:true;elide:Text.ElideRight;color:theme.text;text:root.requested?''','''                Desk.DeskButton {text:"设置";onClicked:settings.open()}
                Desk.DeskButton {id:moreButton;text:"更多";onClicked:{var point=moreButton.mapToItem(details,0,moreButton.height);moreMenu.x=Math.max(0,Math.min(details.width-moreMenu.width,point.x));moreMenu.y=point.y;moreMenu.open()}}
            }
            Label {Layout.fillWidth:true;elide:Text.ElideRight;color:theme.text;text:root.requested?''')
replace('model:["选区／当前小节","当前钢琴全谱"]','model:["下次检查：选区／当前小节","下次检查：钢琴全谱"]')
replace('''                Desk.DeskButton {text:"定位";enabled:!!root.current;onClicked:root.locate()}''','''                Desk.DeskButton {text:"定位相关音";enabled:!!root.current;onClicked:root.locate();ToolTip.visible:hovered;ToolTip.text:"选中涉及的音，并在谱面短暂标出所在小节"}''')
replace('''            RowLayout {
                Desk.DeskButton {text:"声部／分手";onClicked:roleDialog.open()}
                Desk.DeskButton {text:"和弦解释";onClicked:chordDialog.open()}
                Desk.DeskButton {text:"导入和声";onClicked:importDialog.open()}
            }''','''            Desk.DeskButton {text:"声部与左右手";onClicked:roleDialog.open();ToolTip.visible:hovered;ToolTip.text:"指定旋律、低音和内声部，或为所选音校正左右手"}''')
replace('x:Math.max(0,(root.width-width)/2);y:0;','x:Math.max(0,(details.width-width)/2);y:0;')
needle='    Window {\n        id:problemHint;'
replace(needle,'''    Menu {
        id:moreMenu;parent:details;width:230
        MenuItem {text:"指定局部和弦…";onTriggered:chordDialog.open()}
        MenuItem {text:"导入和弦助手分析…";onTriggered:importDialog.open()}
        MenuItem {text:"恢复已忽略的提示";enabled:root.config.ignored.length>0;onTriggered:{var c=Rules.clone(root.config);c.ignored=[];root.config=c;root.persist();root.markDirty()}}
    }
'''+needle)
replace('text:"自动建议 + 快速校正"','text:"声部与左右手"')
replace('text:roles.length?"按谱表／voice 设置；最高最低音线适用于和弦声部。":"先分析以取得声部列表。"','text:roles.length?"按谱表和声部设置。和弦内可指定最高音线或最低音线。":"点击更新结果后，这里会列出声部。"')
replace('" · voice "+(track%4+1)','" · 声部 "+(track%4+1)')
replace('''            Label {text:"起止 tick（每四分音符 480）";color:theme.muted}
            RowLayout {Desk.DeskSpinBox {id:chordStart;''','''            Label {text:"选择需要按这个和弦检查的范围";color:theme.muted}
            Label {Layout.fillWidth:true;wrapMode:Text.WordWrap;color:theme.text;text:root.describePosition(chordStart.value)+" 至 "+root.describePosition(chordEnd.value)}
            Desk.DeskButton {text:"用当前谱面选区";onClicked:root.useChordSelection()}
            CheckBox {id:exactChordPosition;text:"输入精确位置（tick）"}
            RowLayout {visible:exactChordPosition.checked;Desk.DeskSpinBox {id:chordStart;''')
replace('text:"应用本谱局部解释"','text:"使用这个和弦解释"')
replace('text:"清除本谱局部解释"','text:"恢复自动和弦解释"')
replace('height:300;y:0\n        background:Rectangle {color:theme.background;border.color:theme.line}\n        ColumnLayout {anchors.fill:parent','height:Math.min(400,details.height);y:0\n        background:Rectangle {color:theme.background;border.color:theme.line}\n        ColumnLayout {anchors.fill:parent')
needle='    function ignore() {'
replace(needle,'''    function describePosition(tick) {
        var meters=cachedData?cachedData.meters:[],found=null
        for(var i=0;i<meters.length;++i)if(meters[i].tick<=tick)found=meters[i]
        if(!found)return "位置 "+tick
        if(tick===found.end)return "第 "+found.measure+" 小节末"
        var beat=1+(tick-found.tick)/(480*4/(found.denominator||4)),text=Number(beat.toFixed(2))
        return "第 "+found.measure+" 小节第 "+text+" 拍"
    }
    function useChordSelection() {
        if(!observer||!curScore)return
        var selection=curScore.selection,from=-1,until=-1
        if(selection&&selection.isRange&&selection.startSegment){from=selection.startSegment.tick;until=selection.endSegment?selection.endSegment.tick:scope.end}
        else if(typeof observer.expressionSelection==="function"){
            var notes=observer.expressionSelection().notes||[]
            notes.forEach(function(note){from=from<0?note.tick:Math.min(from,note.tick);until=Math.max(until,note.end||note.tick+1)})
        }
        if(from>=0&&until>from){chordStart.value=from;chordEnd.value=until}
        else status="在谱面框选一段，再点用当前谱面选区。"
    }
'''+needle)
p.write_text(s,encoding='utf8',newline='\n')
