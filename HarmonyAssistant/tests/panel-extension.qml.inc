    function windowTicks() {return [0,240,480,960,1920][arpeggioWindow.currentIndex] || 0}
    function windowHeight() {return 650}
    function functionText(pitch, tonic, definition) {
        var label=Harmony.labelFor(pitch,tonic,definition)
        return configuration.labels[label] === undefined ? label : configuration.labels[label]
    }
    function colorFor(pitch, tonic, definition) {
        return configuration.colors[Harmony.role(Harmony.labelFor(pitch,tonic,definition))] || configuration.colors["外"]
    }
    function collectPreferences() {
        var c=JSON.parse(JSON.stringify(configuration))
        c.auto=autoChord.checked; c.follow=followPlayback.checked; c.coloring=scoreColoring.checked
        c.allColor=allColor.checked; c.chordLabels=showChords.checked; c.noteFunctions=showFunctions.checked
        c.pedal=pedalContext.checked; c.window=arpeggioWindow.currentIndex; c.scope=scope.currentIndex
        c.keyMode=keyMode.currentIndex; c.keyTonic=keyTonic.currentIndex; c.manualKey=manualKey
        c.root=rootCombo.currentIndex; c.quality=qualityCombo.currentIndex
        c.keyboard=keyboardExpanded; c.settings=settingsExpanded
        return Preferences.clean(c)
    }
    function applyPreferences(value) {
        loadingConfiguration=true
        try {
            var c=Preferences.clean(value)
            configuration=c
            autoChord.checked=c.auto; followPlayback.checked=c.follow; scoreColoring.checked=c.coloring
            allColor.checked=c.allColor; showChords.checked=c.chordLabels; showFunctions.checked=c.noteFunctions
            pedalContext.checked=c.pedal; arpeggioWindow.currentIndex=c.window; scope.currentIndex=c.scope
            keyMode.currentIndex=c.keyMode; keyTonic.currentIndex=c.keyTonic; manualKey=c.manualKey
            rootCombo.currentIndex=c.root; qualityCombo.currentIndex=c.quality
            keyboardExpanded=c.keyboard; settingsExpanded=c.settings
        } catch(error) {noticeText="配置未应用："+String(error)}
        finally {loadingConfiguration=false}
        optionsChanged()
    }
    function savePreferences() {
        if(!started || loadingConfiguration)return
        var c=collectPreferences()
        if(advancedNative) {
            if(!observer.saveConfiguration("HarmonyAssistant",c))noticeText="配置保存失败，请检查设置目录权限。"
        } else if(settingsStore.item) settingsStore.item.payload=JSON.stringify(c)
    }
    function optionsChanged() {
        if(!started || loadingConfiguration)return
        configurationTimer.restart()
        analysisDirty=true
        analysisTimer.stop()
        requestRefresh(false)
        if(advancedNative) {observer.setScorePreview([]); scheduleAnalysis()}
    }
    function needsAnalysis() {return advancedNative && ((scoreColoring.checked && allColor.checked) || showChords.checked || showFunctions.checked || pendingExport.length>0)}
    function scheduleAnalysis() {
        if(!started || !surfaceActive || !curScore || !needsAnalysis() || analysisTimer.running || !analysisDirty)return
        setScope()
        pendingRecords=[]
        analysisNextTick=0
        analysisTimer.start()
    }
    function frameResult(frame) {
        var notes=frame.analysisNotes || frame.notes || []
        var pitches=notes.map(function(n){return n.pitch})
        var result=autoChord.checked ? Harmony.detect(pitches) :
            {root:Harmony.rootPcs[rootCombo.currentIndex],definition:qualityCombo.currentIndex}
        var imported=Analysis.atTick(importedRecords,frame.tick)
        if(imported){result.root=imported.root;result.definition=imported.definition}
        var chord="", degree="", tonic=Harmony.rootPcs[keyTonic.currentIndex]
        if(!manualKey) {
            var major=[11,6,1,8,3,10,5,0,7,2,9,4,11,6,1]
            tonic=major[(frame.keySignature || 0)+7]
            if(keyMode.currentIndex===1)tonic=Harmony.mod12(tonic+9)
        }
        if(result.root>=0) {
            var name=nameOf(result.root)
            for(var i=0;i<notes.length;++i)if(Harmony.mod12(notes[i].pitch)===result.root){name=Harmony.spelledName(notes[i].tpc,notes[i].pitch,prefersFlats());break}
            chord=name+Harmony.defs[result.definition].suffix
            degree=Harmony.roman(tonic,keyMode.currentIndex===1,result.root,result.definition)
        }
        return {tick:frame.tick,bar:frame.bar,beat:frame.beat,root:result.root,definition:result.definition,
            chord:chord,degree:degree,notes:notes}
    }
    function buildAnalysisChunk() {
        if(!curScore || !surfaceActive || !needsAnalysis())return
        var batch=observer.analysisFrames(analysisNextTick,32,firstTrack,endTrack,pedalContext.checked,windowTicks())
        analysisFingerprint=batch.fingerprint || ""
        var frames=batch.frames || []
        for(var i=0;i<frames.length;++i)pendingRecords.push(frameResult(frames[i]))
        analysisNextTick=batch.nextTick
        if(analysisNextTick>=0) {analysisTimer.start(); return}
        analysisRecords=pendingRecords; pendingRecords=[]; analysisDirty=false
        applyScorePreview()
        if(pendingExport.length){var action=pendingExport;pendingExport="";chooseFile(action)}
    }
    function applyScorePreview() {
        if(!advancedNative)return
        var descriptors=[], lastChord=""
        for(var i=0;i<analysisRecords.length;++i) {
            var frame=analysisRecords[i], onset=[]
            if(frame.root<0){lastChord="";continue}
            // Attribute notes when they are written; later sustained contexts cannot recolor an earlier attack.
            for(var n=0;n<frame.notes.length;++n)if(frame.notes[n].tick===frame.tick)onset.push(frame.notes[n])
            for(n=0;n<onset.length;++n) {
                var d=JSON.parse(JSON.stringify(onset[n]))
                if(scoreColoring.checked && allColor.checked)d.color=colorFor(d.pitch,frame.root,frame.definition)
                if(showFunctions.checked)d.label=functionText(d.pitch,frame.root,frame.definition)
                if(showChords.checked && n===0 && frame.chord!==lastChord)d.chord=frame.chord+" · "+frame.degree
                if(d.color || d.label || d.chord)descriptors.push(d)
            }
            if(onset.length)lastChord=frame.chord
        }
        observer.setScorePreview(descriptors)
        // The active layer must be last so it can highlight labels during playback.
        observer.clearNotePreviewColors()
        repaintNotes()
    }
    function prepareExport(action) {
        pendingExport=action
        if(analysisDirty || !analysisRecords.length) {analysisDirty=true; scheduleAnalysis()}
        else {pendingExport="";chooseFile(action)}
    }
    function chooseFile(action) {pendingFileAction=action; exchangeDialog.open()}
    function exchangeFile(path) {
        try {
            var action=pendingFileAction, content=""
            if(action.indexOf("import")===0) {
                content=observer.readTextFile(path)
                if(!content.length)throw Error("文件为空、超过 16 MiB 或无法读取")
                var parsed=JSON.parse(content)
                if(action==="import-config") {applyPreferences(Preferences.clean(parsed));savePreferences();noticeText="配置已导入并保存。"}
                else {
                    var imported=Analysis.validate(parsed)
                    setScope()
                    var fingerprint=observer.contextSnapshot(0,firstTrack,endTrack,pedalContext.checked,windowTicks(),false).fingerprint
                    if(imported.fingerprint!==fingerprint)throw Error("分析与当前乐谱 / 乐器范围不一致，未应用")
                    importedRecords=imported.frames; analysisDirty=true; scheduleAnalysis(); requestRefresh(false)
                    noticeText="已导入 "+imported.frames.length+" 个分析切片。"
                }
            } else {
                content=action==="export-config" ? JSON.stringify(collectPreferences(),null,2) :
                    action==="csv" ? Analysis.csv(analysisRecords) :
                    JSON.stringify(Analysis.document(analysisRecords,analysisFingerprint,collectPreferences()),null,2)
                var suffix=action==="csv"?".csv":".json"
                if(path.toLowerCase().slice(-suffix.length)!==suffix)path+=suffix
                if(!observer.writeTextFile(path,content))throw Error("无法写入文件")
                noticeText="已导出："+decodeURIComponent(path)
            }
        } catch(error) {noticeText="操作未完成："+String(error)}
    }
