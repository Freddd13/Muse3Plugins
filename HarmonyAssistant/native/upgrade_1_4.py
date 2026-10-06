# -*- coding: utf-8 -*-
"""One-time 1.4 plugin integration; guarded replacements preserve existing controls."""
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'HarmonyAssistant_MS3.qml'
s=p.read_text(encoding='utf-8')
def replace(old,new):
    global s
    assert old in s,old[:100]
    s=s.replace(old,new,1)
replace('import "Analysis.js" as Analysis','import "Analysis.js" as Analysis\nimport "Timeline.js" as Timeline')
replace('version: "1.3.0"','version: "1.4.0"')
replace('    property var pendingRecords: []','''    property var analysisRegions: []
    property var manualOverrides: []
    property var editUndo: []
    property var editRedo: []
    property string loadedFingerprint: ""
    property bool manualNeedsReview: false
    property int annotationTick: -1
    property int liveRoot: -1
    property int liveDefinition: -1
    property string instantChordText: "—"
    property string instantDegreeText: "—"
    property var ownedRegion: Timeline.atTick(analysisRegions,currentTick,partForTrack(selectionTrack))
    property string summaryChordText: configuration.summaryMode===0 ? instantChordText : ownedRegion ? ownedRegion.chord : analysisDirty ? "分析中…" : "—"
    property string summaryDegreeText: configuration.summaryMode===0 ? instantDegreeText : ownedRegion ? ownedRegion.degree : "—"
    property int analysisEnd: analysisRecords.length ? (analysisRecords[analysisRecords.length-1].scoreEnd || analysisRecords[analysisRecords.length-1].tick+480) : 1920
    property var pendingRecords: []''')
replace('    function openAnnotation(tick,track) {','''    function partForTrack(track) {
        if(curScore)for(var i=0;i<curScore.parts.length;++i)if(track>=curScore.parts[i].startTrack && track<curScore.parts[i].endTrack)return curScore.parts[i].startTrack
        return firstTrack
    }
    function highlightedTick() {return lastPlaying && followPlayback.checked ? currentTick : annotationTick>=0 ? annotationTick : currentTick}
    function rebuildRegions() {
        analysisRegions=Timeline.build(analysisRecords,collectPreferences(),firstTrack,manualNeedsReview?[]:manualOverrides)
    }
    function loadCorrections() {
        if(!advancedNative || loadedFingerprint===analysisFingerprint)return
        if(manualOverrides.length && loadedFingerprint.length) {
            manualNeedsReview=true;noticeText="谱面已变更；人工范围暂未应用，请复核后确认。";return
        }
        loadedFingerprint=analysisFingerprint
        var saved=observer.loadConfiguration("HarmonyAssistant-regions-"+analysisFingerprint)
        if(saved.schema===1 && saved.fingerprint===analysisFingerprint) {
            try{manualOverrides=Timeline.validEdits(saved.overrides)}catch(error){noticeText="人工范围未读取："+error}
        }
    }
    function saveCorrections() {
        if(!advancedNative || !loadedFingerprint.length || manualNeedsReview)return
        if(!observer.saveConfiguration("HarmonyAssistant-regions-"+loadedFingerprint,{schema:1,fingerprint:loadedFingerprint,overrides:manualOverrides}))noticeText="人工范围保存失败。"
    }
    function editRange(command,start,end,rootIndex,qualityIndex) {
        if(command==="select"){annotationTick=start;displayTick(start,true);return}
        if(command==="review"){loadedFingerprint=analysisFingerprint;manualNeedsReview=false;rebuildRegions();saveCorrections();applyScorePreview();return}
        var next=Timeline.clone(manualOverrides),region=ownedRegion
        if(command==="undo" || command==="redo") {
            var source=command==="undo"?editUndo:editRedo,target=command==="undo"?editRedo:editUndo
            if(!source.length)return
            target=target.concat([Timeline.clone(manualOverrides)]);next=source[source.length-1];source=source.slice(0,-1)
            if(command==="undo"){editUndo=source;editRedo=target}else{editRedo=source;editUndo=target}
        } else {
            if(manualNeedsReview){noticeText="请先复核已有人工范围。";return}
            if(command==="split" && region){next.push(Timeline.clone(region));next[next.length-1].start=start}
            else if(command==="merge" && region) {
                var previous=null
                for(var i=0;i<analysisRegions.length;++i)if(analysisRegions[i].part===region.part && analysisRegions[i].end===region.start)previous=analysisRegions[i]
                if(!previous){noticeText="没有相邻的前一和弦。";return}
                var merged=Timeline.clone(previous);merged.end=region.end;next.push(merged);annotationTick=merged.start
            } else {
                if(start<0 || end<=start || end>analysisEnd){noticeText="范围必须在谱内，且终点晚于起点。";return}
                if(command==="restore")next=next.filter(function(n){return n.part!==partForTrack(selectionTrack)||n.end<=start||n.start>=end})
                else {
                    var edit=region?Timeline.clone(region):{part:partForTrack(selectionTrack),notes:Timeline.clone(currentNotes)}
                    if(command==="assign") {
                        var info=Timeline.describe({root:Harmony.rootPcs[rootIndex],definition:qualityIndex},edit.notes,start,Harmony.rootPcs[keyTonic.currentIndex],keyMode.currentIndex===1)
                        for(var field in info)edit[field]=info[field]
                    }
                    if(edit.root===undefined){edit.root=-1;edit.definition=-1}
                    edit.start=start;edit.end=end;edit.suppressed=command==="suppress";next.push(edit);annotationTick=start
                }
            }
            editUndo=editUndo.concat([Timeline.clone(manualOverrides)]).slice(-100);editRedo=[]
        }
        manualOverrides=Timeline.validEdits(next);loadedFingerprint=analysisFingerprint
        rebuildRegions();saveCorrections();analyze();applyScorePreview()
    }
    function openAnnotation(tick,track) {''')
replace('        if(!curScore)return\n        if(!lastPlaying)', '        if(!curScore)return\n        annotationTick=tick\n        if(!lastPlaying)')
replace('            d.chordTick=frame.tick;d.chordUntil=frame.tick','            d.chordTick=frame.start===undefined?frame.tick:frame.start;d.chordUntil=frame.end===undefined?frame.tick:frame.end')
replace('            d.chordFont=["","Edwin","Arial"][configuration.chordFont]','            d.chordFont=["","Edwin","Arial"][configuration.chordFont]\n            d.degreeFont=configuration.degreeFont')
replace('showFunctions.checked || pendingExport.length>0)', 'showFunctions.checked || configuration.summaryMode===1 || configuration.detailMode===1 || pendingExport.length>0)')
replace('            chord:chord,degree:degree,notes:notes,chromatic:', '            chord:chord,degree:degree,notes:notes,parts:frame.parts,pedalWindows:frame.pedalWindows,scoreEnd:frame.scoreEnd,keySignature:frame.keySignature,imported:!!imported,chromatic:')
replace('        applyScorePreview()\n        if(pendingExport.length)', '        loadCorrections();rebuildRegions();analyze();applyScorePreview()\n        if(pendingExport.length)')
a=s.index('    function applyScorePreview() {');b=s.index('    function prepareExport(',a)
s=s[:a]+'''    function applyScorePreview() {
        if(!advancedNative)return
        var descriptors=[],written={},markers={},regions=analysisRegions
        for(var r=0;r<regions.length;++r) {
            var region=regions[r]
            if(showChords.checked && region.notes.length) {
                var anchor=region.notes.filter(function(n){return n.tick===region.start})[0]||region.notes[0]
                var marker=chordDescriptor(anchor,region);markers[region.part+":"+region.start]=marker
            }
        }
        for(var i=0;i<analysisRecords.length;++i) {
            var frame=analysisRecords[i]
            for(var n=0;n<frame.notes.length;++n) {
                var note=frame.notes[n]
                if(note.tick!==frame.tick)continue
                var key=note.tick+":"+note.track+":"+note.index
                if(written[key])continue
                written[key]=true
                var part=partForTrack(note.track),owned=Timeline.atTick(regions,frame.tick,part)
                if(!owned)continue
                var d=Timeline.clone(note)
                if(scoreColoring.checked && allColor.checked)d.color=colorFor(d.pitch,owned.root,owned.definition)
                if(showFunctions.checked)d.label=functionText(d.pitch,owned.root,owned.definition)
                var markerKey=part+":"+frame.tick,m=markers[markerKey]
                if(m && m.track===note.track && m.index===note.index) {
                    for(var field in m)d[field]=m[field]
                    delete markers[markerKey]
                }
                if(d.color || d.label || d.chord || d.degree)descriptors.push(d)
            }
        }
        for(var markerKey in markers)descriptors.push(markers[markerKey])
        if(configuration.repeatBars && showChords.checked) {
            var lastBar=-1
            for(i=0;i<analysisRecords.length;++i) {
                frame=analysisRecords[i]
                if(frame.bar===lastBar)continue
                lastBar=frame.bar
                for(r=0;r<regions.length;++r)if(regions[r].start<frame.tick && frame.tick<regions[r].end && regions[r].notes.length) {
                    var repeated=Timeline.clone(regions[r]);repeated.start=frame.tick
                    descriptors.push(chordDescriptor(repeated.notes[0],repeated))
                }
            }
        }
        observer.setScorePreview(descriptors)
        observer.clearNotePreviewColors();repaintNotes()
        if(typeof observer.previewStatus==="function") {
            var status=observer.previewStatus()
            if(status.hidden>0)noticeText=status.hidden+" 个记号空间不足；分析及范围编辑仍可查看。"
            else if(status.fontFallback)noticeText="记号字体缺失，已回退到 "+status.fontFallback
        }
    }
''' + s[b:]
replace('                    importedRecords=imported.frames;', '                    manualOverrides=Timeline.validEdits(imported.overrides||[]);loadedFingerprint=fingerprint;manualNeedsReview=false;saveCorrections()\n                    importedRecords=imported.frames;')
replace('Analysis.document(analysisRecords,analysisFingerprint,collectPreferences())','Analysis.document(analysisRecords,analysisFingerprint,collectPreferences(),analysisRegions,manualOverrides)')
replace('        importedRecords = []\n        analysisRecords = []','        saveCorrections()\n        manualOverrides=[];editUndo=[];editRedo=[];analysisRegions=[];loadedFingerprint="";manualNeedsReview=false;annotationTick=-1\n        importedRecords = []\n        analysisRecords = []')
replace('observer.setActiveScorePreview(lastPlaying && followPlayback.checked ? tick : -1)','observer.setActiveScorePreview(highlightedTick())')
replace('observer.setActiveScorePreview(lastPlaying && followPlayback.checked ? currentTick : -1)','observer.setActiveScorePreview(highlightedTick())')
replace('        updateTexts()\n        updatePianoRange()', '        liveRoot=chordRoot;liveDefinition=chordDefinition\n        updateTexts()\n        updatePianoRange()')
replace('    function updateTexts() {\n        chordText', '    function updateTexts() {\n        chordRoot=liveRoot;chordDefinition=liveDefinition\n        chordText')
replace('        var degrees = ["1","3","5","7","9","11","13"], rows = []','''        instantChordText=chordText;instantDegreeText=degreeText
        if(configuration.detailMode===1 && ownedRegion) {
            chordRoot=ownedRegion.root;chordDefinition=ownedRegion.definition
            chordText=ownedRegion.chord;degreeText=ownedRegion.degree
            matchText="所属和弦 · "+(ownedRegion.source==="manual"?"人工修正":ownedRegion.kind||"已识别")
            inversionText=Harmony.inversion(Harmony.labelFor(ownedRegion.bass,chordRoot,chordDefinition))+" · 区间 ticks "+ownedRegion.start+"–"+ownedRegion.end
        }
        var degrees = ["1","3","5","7","9","11","13"], rows = []''')
replace('        var roleNotes = contextNotes.length ? contextNotes : currentNotes','        var roleNotes = configuration.detailMode===1 && ownedRegion ? ownedRegion.notes : contextNotes.length ? contextNotes : currentNotes')
replace('onModified:{root.configuration=configuration; optionsChanged(false)}}','onModified:{root.configuration=configuration; rebuildRegions();analyze();optionsChanged(false)}}')
replace('                    Switch {id:pedalContext;', '''                    RowLayout {width:parent.width
                        UiLabel {text:"踏板内识别";color:muted;font.pixelSize:11}
                        ComboBox {model:["单个和弦","多个和弦"];currentIndex:configuration.pedalMode;Layout.fillWidth:true;onActivated:{var c=Timeline.clone(configuration);c.pedalMode=currentIndex;configuration=Preferences.clean(c);optionsChanged()}}
                    }
                    Switch {id:pedalContext;''')
replace('                PanelCard {\n                    width:root.expanded ? (panel.width-10)/2 : panel.width\n                    visible:settingsExpanded\n                    UiLabel {text:"全谱和弦分析";', '''                PanelCard {
                    width:root.expanded ? (panel.width-10)/2 : panel.width
                    visible:settingsExpanded && advancedNative
                    RangeEditor {width:parent.width;region:root.ownedRegion;regions:root.analysisRegions.filter(function(n){return n.part===root.partForTrack(root.selectionTrack)})
                        tick:Math.max(0,root.currentTick);scoreEnd:root.analysisEnd;canUndo:root.editUndo.length>0;canRedo:root.editRedo.length>0
                        roots:Harmony.rootNames;qualities:root.qualityNames;onAction:root.editRange(command,start,end,rootIndex,qualityIndex)}
                    Button {text:"复核完成：应用原人工范围";visible:root.manualNeedsReview;onClicked:root.editRange("review",0,0,0,0)}
                }
                PanelCard {
                    width:root.expanded ? (panel.width-10)/2 : panel.width
                    visible:settingsExpanded
                    UiLabel {text:"全谱和弦分析";''')
replace('StableLabel {text:chordText; color:chordInk; horizontalAlignment:', 'StableLabel {text:root.summaryChordText; color:chordInk; horizontalAlignment:')
replace('StableLabel {text:degreeText+" · "+positionText;', 'StableLabel {text:root.summaryDegreeText+" · "+positionText;')
replace('savePreferences(); undoPause = false;', 'savePreferences();saveCorrections(); undoPause = false;')
with p.open('w',encoding='utf-8',newline='\n') as f:f.write(s)
