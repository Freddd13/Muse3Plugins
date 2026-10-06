"""One-time upgrade of the 1.0 panel; original and previous release remain available."""
from pathlib import Path
P=Path(__file__).resolve().parent.parent
p=P/'HarmonyAssistant_MS3.qml'
s=p.read_text(encoding='utf-8-sig')
def replace(old,new):
    global s
    assert old in s,old[:90]
    s=s.replace(old,new,1)
replace('import "Harmony.js" as Harmony','''import "Harmony.js" as Harmony
import "Preferences.js" as Preferences
import "Analysis.js" as Analysis
import QtQuick.Dialogs 1.3''')
replace('version: "1.0.0"','version: "1.1.0"')
replace('    property bool started: false', '''    property var configuration: Preferences.defaults()
    property bool loadingConfiguration: false
    property bool ribbon: (width > 460 && height < 300) ||
        (typeof panelPlacement === "string" && (panelPlacement === "top" || panelPlacement === "bottom") && height < 400)
    property bool expanded: flick.width >= 680
    property bool advancedNative: observer && typeof observer.contextSnapshot === "function"
    property var contextNotes: []
    property var analysisRecords: []
    property var pendingRecords: []
    property var importedRecords: []
    property string analysisFingerprint: ""
    property int analysisNextTick: 0
    property bool analysisDirty: true
    property string pendingFileAction: ""
    property string pendingExport: ""
    property bool started: false''')
replace('    function same(a, b)', (P/'tests/panel-extension.qml.inc').read_text(encoding='utf-8')+'\n    function same(a, b)')
replace('        timeline = []\n        cacheDirty = true', '''        timeline = []
        analysisTimer.stop()
        importedRecords = []
        analysisRecords = []
        analysisDirty = true
        cacheDirty = true''')
replace('            buildSegment = null\n        }\n        if (surfaceActive)', '''            buildSegment = null
            analysisDirty = true
            if (advancedNative) observer.clearAllPreviews()
            if (importedRecords.length) {importedRecords=[]; noticeText="乐谱已变更，已退出导入结果；请重新分析。"}
        }
        if (surfaceActive)''')
replace('            nativeSnapshot = observer.snapshot(tick, firstTrack, endTrack, lastPlaying && followPlayback.checked)', '''            nativeSnapshot = advancedNative ? observer.contextSnapshot(tick, firstTrack, endTrack,
                pedalContext.checked, windowTicks(), lastPlaying && followPlayback.checked) :
                observer.snapshot(tick, firstTrack, endTrack, lastPlaying && followPlayback.checked)''')
replace('        notes.sort(function(a,b)', '''        var detectedNotes = nativeSnapshot.analysisNotes || notes
        var contextChanged = JSON.stringify(detectedNotes) !== JSON.stringify(contextNotes)
        contextNotes = detectedNotes
        notes.sort(function(a,b)''')
replace('        if (!changed && !force)', '        if (!changed && !contextChanged && !force)')
replace('        if (!currentNotes.length) {', '        if (!contextNotes.length && !currentNotes.length) {')
replace('            var result = Harmony.detect(currentPitches)', '''            var contextPitches = contextNotes.map(function(n){return n.pitch})
            var result = Harmony.detect(contextPitches.length ? contextPitches : currentPitches)
            var imported = Analysis.atTick(importedRecords, currentTick)
            if (imported) result = {root:imported.root,definition:imported.definition,kind:"已导入的分析",alternatives:[]}
            else if (contextPitches.length > currentPitches.length) result.kind += " · 踏板 / 琶音上下文"''')
replace('        repaintNotes()\n    }\n    function updateTexts()', '        repaintNotes()\n        scheduleAnalysis()\n    }\n    function updateTexts()')
replace('        for (var i = 0; i < currentNotes.length; ++i)\n            if (Harmony.mod12(currentNotes[i].pitch) === chordRoot)\n                return Harmony.spelledName(currentNotes[i].tpc, currentNotes[i].pitch, prefersFlats())', '''        var namingNotes = contextNotes.length ? contextNotes : currentNotes
        for (var i = 0; i < namingNotes.length; ++i)
            if (Harmony.mod12(namingNotes[i].pitch) === chordRoot)
                return Harmony.spelledName(namingNotes[i].tpc, namingNotes[i].pitch, prefersFlats())''')
replace('color:Harmony.colors[degree]', 'color:configuration.colors[degree]')
s=s.replace('Harmony.colorFor(', 'colorFor(')
start=s.index('    function repaintNotes() {')
end=s.index('    function restoreColors(',start)
s=s[:start]+'''    function repaintNotes() {
        if (observer) {
            var descriptors = []
            if (chordRoot >= 0) {
                var notes = currentNotes.length ? currentNotes : contextNotes
                for (var i=0;i<notes.length;++i) {
                    var d=JSON.parse(JSON.stringify(notes[i]))
                    if(scoreColoring.checked)d.color=colorFor(d.pitch,chordRoot,chordDefinition)
                    if(advancedNative && showFunctions.checked)d.label=functionText(d.pitch,chordRoot,chordDefinition)
                    if(advancedNative && showChords.checked && i===0)d.chord=chordText+" · "+degreeText
                    if(advancedNative)d.active=lastPlaying && followPlayback.checked
                    if(d.color || d.label || d.chord)descriptors.push(d)
                }
            }
            observer.setNotePreviewColors(descriptors)
        } else syncColors(scoreColoring.checked && !lastPlaying)
    }
''' + s[end:]
replace('        restoreColors(true)\n    }\n    function updatePianoRange()', '''        restoreColors(true)
        if(advancedNative)observer.clearAllPreviews()
        applyScorePreview()
        savePreferences()
    }
    function updatePianoRange()''')
replace('        if (!currentPitches.length) {pianoStart', '        if (!currentPitches.length) {pianoStart')
replace('            if (observer) scoreColoring.checked = true', '''            if (observer) scoreColoring.checked = true
            if (advancedNative) {
                var saved=observer.loadConfiguration("HarmonyAssistant")
                if(saved.schema)applyPreferences(saved)
            } else settingsStore.active=true''')
replace('        if (!surfaceActive) {refreshTimer.stop(); playbackTimer.stop(); buildTimer.stop()}', '''        if (!surfaceActive) {refreshTimer.stop(); playbackTimer.stop(); buildTimer.stop(); analysisTimer.stop()}
        else if(advancedNative) {analysisDirty=true; scheduleAnalysis()}''')
# Avoid two else branches by keeping the existing resume block as a separate if.
replace('        else {followNativePosition(); requestRefresh(false)}', '        if (surfaceActive) {followNativePosition(); requestRefresh(false)}')
replace('Component.onDestruction: {if (started) {undoPause = false; restoreColors(true)}}', '''Component.onDestruction: {if (started) {savePreferences(); undoPause = false; restoreColors(true); if(advancedNative)observer.clearAllPreviews()}}''')
replace('    Timer {id:refreshTimer;', '''    Timer {id:configurationTimer; interval:350; onTriggered:savePreferences()}
    Timer {id:analysisTimer; interval:12; onTriggered:buildAnalysisChunk()}
    Loader {id:settingsStore; active:false; source:"SettingsStore.qml"; onLoaded:{if(item.payload.length){try{applyPreferences(JSON.parse(item.payload))}catch(error){noticeText="配置未读取："+error}}}}
    FileDialog {
        id:exchangeDialog
        title:pendingFileAction.indexOf("import")===0 ? "导入 JSON" : "导出和声信息"
        selectExisting:pendingFileAction.indexOf("import")===0
        nameFilters:pendingFileAction==="csv" ? ["CSV (*.csv)"] : ["JSON (*.json)"]
        onAccepted:exchangeFile(String(fileUrl))
    }
    Popup {
        id:detailPopup; width:Math.min(760,Math.max(280,root.width-32)); height:Math.min(650,root.windowHeight())
        x:Math.max(0,(root.width-width)/2); y:0; modal:false; padding:0
    }
    Timer {id:refreshTimer;''')
replace('    Rectangle {\n        anchors.fill: parent', '''    Rectangle {
        id:backdrop
        anchors.fill: parent''')
replace('        color: "#F4F6F8"', '        color: "#f4f4f4"')
replace('            id: flick\n            anchors.fill: parent', '''            id: flick
            parent:root.ribbon ? detailPopup.contentItem : backdrop
            anchors.fill: parent''')
replace('            Column {\n                id: panel', '            Flow {\n                id: panel')
replace('            boundsBehavior: Flickable.StopAtBounds', '            boundsBehavior: Flickable.StopAtBounds\n            visible:!root.ribbon || detailPopup.opened')
replace('                width: Math.max(180, flick.width - 24)', '                width: Math.max(160, flick.width - 24)')
replace('                        ToolButton {\n                            font.family: "Microsoft YaHei UI";text:"键盘";', '''                        ToolButton {
                            text:typeof root.panelFloating === "boolean" && root.panelFloating ? "停靠" : "悬浮"
                            visible:typeof root.setPanelFloating === "function"
                            font.pixelSize:11
                            onClicked:root.setPanelFloating(!root.panelFloating)
                        }
                        ToolButton {
                            font.family: "Microsoft YaHei UI";text:"键盘";''')
# Only direct panel cards participate in the two-column layout.
s=s.replace('                PanelCard {\n                    width: parent.width', '                PanelCard {\n                    width: root.expanded ? (panel.width-10)/2 : panel.width')
s=s.replace('                PanelCard {\n                    width:parent.width', '                PanelCard {\n                    width:root.expanded ? (panel.width-10)/2 : panel.width')
s=s.replace('border.color: modelData.present ? modelData.color : "#E6E9ED"', 'border.color:"#e0e0e0"')
replace('                                Column {\n                                    id:toneBody', '''                                Rectangle {width:3; height:parent.height-16; x:0; y:8; color:modelData.present?modelData.color:"#e0e0e0"; radius:1}
                                Column {
                                    id:toneBody''')
replace('                                color:colorFor(modelData.pitch,chordRoot,chordDefinition)', '                                color:"#f4f4f4"; border.color:"#e0e0e0"')
replace('text:noteName(modelData)+" · "+functionLabel; color:"white"', 'text:noteName(modelData)+" · "+root.functionText(modelData.pitch,chordRoot,chordDefinition); color:root.colorFor(modelData.pitch,chordRoot,chordDefinition)')
replace('                    UiLabel {text:"识别与调性";', '''                    UiLabel {text:"识别与调性";''')
replace('                    ComboBox {\n                            font.family: "Microsoft YaHei UI";\n                        id:scope;', '''                    Switch {id:pedalContext; text:"踏板保持"; checked:true; enabled:advancedNative; onToggled:optionsChanged()}
                    RowLayout {
                        width:parent.width
                        UiLabel {text:"无踏板聚合"; color:muted; font.pixelSize:11}
                        ComboBox {id:arpeggioWindow; model:["即时","半拍","1 拍","2 拍","4 拍"]; Layout.fillWidth:true; implicitHeight:32; onActivated:optionsChanged()}
                    }
                    UiLabel {width:parent.width; text:"聚合限当前小节，休止截断。快速转和弦时建议即时或半拍；踏板保持不等同于声学残响。"; color:muted; font.pixelSize:10; wrapMode:Text.Wrap; visible:settingsExpanded}
                    ComboBox {
                            font.family: "Microsoft YaHei UI";
                        id:scope;''')
replace('                        onToggled:{if(checked)undoPause=false; if(!internalChange)repaintNotes()}', '                        onToggled:{if(checked)undoPause=false; if(!internalChange){repaintNotes(); optionsChanged()}}')
replace('                    UiLabel {\n                        width:parent.width; font.pixelSize:10; color:muted; wrapMode:Text.Wrap\n                        visible:scoreColoring.checked', '''                    Switch {id:allColor; text:"配色覆盖全部小节"; checked:false; enabled:advancedNative && scoreColoring.checked; onToggled:optionsChanged()}
                    Switch {id:showChords; text:"谱面上方显示和弦 / 级数"; checked:false; enabled:advancedNative; onToggled:optionsChanged()}
                    Switch {id:showFunctions; text:"音旁显示功能名"; checked:false; enabled:advancedNative; onToggled:optionsChanged()}
                    UiLabel {
                        width:parent.width; font.pixelSize:10; color:muted; wrapMode:Text.Wrap
                        visible:scoreColoring.checked''')
replace('text:"有色框：实际发声 · 缺音：尚未发声', 'text:"色条：当前音符 · 缺音：未奏出')
# Configuration/data controls form additive cards; all original controls stay available.
replace('            }\n        }\n    }\n}', '''                PanelCard {
                    width:root.expanded ? (panel.width-10)/2 : panel.width
                    visible:settingsExpanded
                    ConfigurationEditor {width:parent.width; configuration:root.configuration; onModified:{root.configuration=configuration; optionsChanged()}}
                    RowLayout {
                        width:parent.width
                        Button {text:"导入配置"; Layout.fillWidth:true; enabled:advancedNative; onClicked:chooseFile("import-config")}
                        Button {text:"导出配置"; Layout.fillWidth:true; enabled:advancedNative; onClicked:chooseFile("export-config")}
                    }
                    UiLabel {width:parent.width; text:"设置自动保存，下次启动自动读取。"; color:muted; font.pixelSize:10; wrapMode:Text.Wrap}
                }
                PanelCard {
                    width:root.expanded ? (panel.width-10)/2 : panel.width
                    visible:settingsExpanded
                    UiLabel {text:"全谱和弦分析"; color:ink; font.bold:true; font.pixelSize:13}
                    Flow {
                        width:parent.width; spacing:6
                        Button {text:"导出 JSON"; enabled:advancedNative; onClicked:prepareExport("json")}
                        Button {text:"导出 CSV"; enabled:advancedNative; onClicked:prepareExport("csv")}
                        Button {text:"导入 JSON"; enabled:advancedNative; onClicked:chooseFile("import-analysis")}
                        Button {text:"重新检测"; enabled:advancedNative; onClicked:{importedRecords=[]; optionsChanged()}}
                    }
                    UiLabel {width:parent.width; text:analysisTimer.running?"正在分批分析…":analysisRecords.length+" 个时间切片"+(importedRecords.length?" · 使用导入分析":""); color:muted; font.pixelSize:11; wrapMode:Text.Wrap}
                }
            }
        }
        RowLayout {
            visible:root.ribbon; anchors.fill:parent; anchors.margins:12; spacing:16
            Column {
                Layout.preferredWidth:Math.min(root.width*.38,280); spacing:2
                UiLabel {width:parent.width; text:chordText; color:ink; font.pixelSize:Math.min(32,Math.max(18,root.height*.22)); font.bold:true; elide:Text.ElideRight}
                UiLabel {width:parent.width; text:degreeText+" · "+positionText; color:muted; font.pixelSize:11; elide:Text.ElideRight}
            }
            Flow {
                Layout.fillWidth:true; Layout.fillHeight:true; spacing:6
                Repeater {model:root.toneRows; delegate:Rectangle {
                    width:42; height:30; color:"#ffffff"; radius:4
                    Rectangle {x:0;y:8;width:3;height:14;color:modelData.present?modelData.color:"#d0d0d0"}
                    UiLabel {anchors.centerIn:parent; text:modelData.label; color:modelData.present?modelData.color:muted; font.pixelSize:12}
                }}
            }
            Column {
                spacing:4
                Button {text:"详细面板"; onClicked:detailPopup.open(); implicitHeight:30; font.pixelSize:11}
                Button {text:"悬浮"; visible:typeof root.setPanelFloating==="function"; onClicked:root.setPanelFloating(true); implicitHeight:30; font.pixelSize:11}
            }
        }
    }
}''')
# User-only control changes persist; playback selection updates must not write preferences.
s=s.replace('onClicked:keyboardExpanded=checked', 'onClicked:{keyboardExpanded=checked; configurationTimer.restart()}')
s=s.replace('onClicked:settingsExpanded=checked', 'onClicked:{settingsExpanded=checked; configurationTimer.restart()}')
s=s.replace('onToggled:analyze()', 'onToggled:{analyze(); optionsChanged()}')
s=s.replace('onActivated:requestRefresh(true)', 'onActivated:{requestRefresh(true); optionsChanged()}')
s=s.replace('onActivated:{manualKey=true; updateTexts()}', 'onActivated:{manualKey=true; updateTexts(); optionsChanged()}')
s=s.replace('onActivated:{autoChord.checked=false; analyze()}', 'onActivated:{autoChord.checked=false; analyze(); optionsChanged()}')
s=s.replace('onToggled:{lastPlayTick=-1; requestRefresh(false)}', 'onToggled:{lastPlayTick=-1; requestRefresh(false); configurationTimer.restart()}')
s=s.replace('onActivated:{if(!manualKey && currentTick>=0) initializeKey(currentTick); updateTexts()}', 'onActivated:{if(!manualKey && currentTick>=0) initializeKey(currentTick); updateTexts(); optionsChanged()}')
with p.open('w',encoding='utf-8',newline='\n') as f:f.write(s)
