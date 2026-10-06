"""Reuse the real Qt panel fixture to test the new additive observer contract."""
from pathlib import Path
import sys
base=Path(__file__).resolve().parent
script=(base/'render_and_check.py').read_text(encoding='utf-8')
script=script.replace('        property var preview: []','''        property var preview: []
        property var basePreview: []
        property var saved: ({})
        property int baseCalls:0
        property var baseLast:[]
        function contextSnapshot(tick,first,end,pedal,window,sounding) {
            var frame=snapshot(tick,first,end,sounding)
            frame.tick=tick;frame.analysisNotes=frame.notes;frame.fingerprint=new Array(65).join("a");return frame
        }
        function analysisFrames(from,limit,first,end,pedal,window) {
            return {nextTick:-1,fingerprint:new Array(65).join("a"),frames:[contextSnapshot(0),contextSnapshot(480),contextSnapshot(960)]}
        }
        function loadConfiguration(name){return saved}
        function saveConfiguration(name,value){saved=value;return true}
        function setScorePreview(notes){basePreview=notes;baseLast=notes;baseCalls++}
        function clearAllPreviews(){preview=[];basePreview=[]}
''')
script=script.replace('        if(lastPlaying) result.failures.push("showing after hidden stop restores selection mode")', '''        if(lastPlaying) result.failures.push("showing after hidden stop restores selection mode")
        var config=Preferences.defaults()
        config.allColor=true;config.noteFunctions=true;config.chordLabels=true
        config.labels["3"]="three";config.colors["3"]="#123abc"
        applyPreferences(config)
        refreshTimer.stop();buildAnalysisChunk();analysisTimer.stop()
        function check(value,name){if(!value)result.failures.push(name)}
        check(analysisRecords.length===3,"whole-score frame analysis")
        check(fixtureObserver.basePreview.length===6,"all written attacks colored once")
        check(fixtureObserver.basePreview.filter(function(n){return n.label==="three"}).length===1,"custom function labels")
        check(fixtureObserver.basePreview.filter(function(n){return n.color==="#123abc"}).length===1,"custom role palette")
        check(fixtureObserver.basePreview.filter(function(n){return n.chord}).length===2,"harmonic change labels")
        savePreferences()
        check(fixtureObserver.saved.allColor && fixtureObserver.saved.labels["3"]==="three","preferences saved")
        fixtureObserver.playing=true;fixtureObserver.tick=480;followNativePosition()
        check(fixtureObserver.preview.every(function(n){return n.active}),"playback text highlight")
        fixtureObserver.tick=960;followNativePosition()
        check(!fixtureObserver.preview.length && fixtureObserver.basePreview.length===6,"rest retains full-score base only")
        stopColoring()
        check(fixtureObserver.basePreview.every(function(n){return !n.color}),"restore removes all colors while retaining text")
        result.modern={baseCount:fixtureObserver.basePreview.length,frames:analysisRecords.length}
        fixtureObserver.playing=false;followNativePosition()
        configurationTimer.stop();analysisTimer.stop()
''',1)
# Keep the original test path so resource resolution remains unchanged.
exec(compile(script,str(base/'render_and_check.py'),'exec'))

