"""Exercise real QML region controls, history, display sources and storage."""
from pathlib import Path
base=Path(__file__).resolve().parent
script=(base/'test_modern_panel.py').read_text(encoding='utf-8')
script=script.replace('        result.modern={baseCount:fixtureObserver.basePreview.length,frames:analysisRecords.length}', '''
        check(analysisRegions.length===2,"regions built separately from raw frames")
        fixtureObserver.playing=false;lastPlaying=false;displayTick(480,true)
        var before=JSON.stringify(manualOverrides)
        editRange("assign",0,720,rootIndex(9),1)
        check(Timeline.atTick(analysisRegions,480,0).chord==="Am/C","manual chord retains independent bass")
        var c=Timeline.clone(configuration);c.detailMode=1;configuration=Preferences.clean(c);analyze()
        check(chordText==="Am/C" && degreeText==="vi","owned display and degree")
        check(instantChordText==="Cmaj13","instant result remains available independently")
        editRange("undo",0,0,0,0);check(JSON.stringify(manualOverrides)===before,"plugin undo independent of score")
        editRange("redo",0,0,0,0);check(Timeline.atTick(analysisRegions,480,0).source==="manual","redo")
        editRange("range",0,600,0,0);check(Timeline.atTick(analysisRegions,660,0).source!=="manual","shrinking removes old override extent")
        editRange("suppress",120,240,0,0);check(!Timeline.atTick(analysisRegions,180,0),"suppressed range")
        editRange("restore",120,240,0,0);check(!!Timeline.atTick(analysisRegions,180,0),"restore automatic range")
        saveCorrections();check(fixtureObserver.saved.fingerprint===analysisFingerprint,"corrections use score fingerprint")
        var beforeImport=JSON.stringify(manualOverrides),stored=JSON.stringify(fixtureObserver.saved)
        var bad=Analysis.document(analysisRecords,analysisFingerprint,collectPreferences(),[{start:0,end:480,part:0,root:999,definition:0}],[])
        fixtureObserver.inputText=JSON.stringify(bad);pendingFileAction="import-analysis";exchangeFile("invalid.json")
        check(JSON.stringify(manualOverrides)===beforeImport && JSON.stringify(fixtureObserver.saved)===stored,"invalid import is atomic")
        settingsExpanded=true
        result.modern={baseCount:fixtureObserver.basePreview.length,frames:analysisRecords.length,regions:analysisRegions.length}
''')
# Add fixed marker API to check selection highlight without a playing sequencer.
script=script.replace('        property int baseCalls:0','''        property int activeScoreTick:-1
        function setActiveScorePreview(tick){activeScoreTick=tick}
        signal previewActivated(int tick,int track)
        property string inputText:""
        function readTextFile(path){return inputText}
        property int baseCalls:0''')
exec(compile(script,str(base/'test_modern_panel.py'),'exec'))
