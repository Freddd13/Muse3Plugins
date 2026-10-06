"""Actual Qt fixture: static marker protocol, stable regions and ribbon position."""
from pathlib import Path
base=Path(__file__).resolve().parent
script=(base/'test_modern_panel.py').read_text(encoding='utf-8')
# Add the 0.4 API to the fixture without losing the existing legacy/current-layer checks.
script=script.replace('        property int baseCalls:0', '''        property int activeScoreTick:-1
        function setActiveScorePreview(tick){activeScoreTick=tick}
        signal previewActivated(int tick,int track)
        property int baseCalls:0''')
script=script.replace('        result.modern={baseCount:fixtureObserver.basePreview.length,frames:analysisRecords.length}', '''        check(fixedChordNative,"fixed annotation API detected")
        check(!fixtureObserver.preview.some(function(n){return n.chord || n.degree}),"current notes never carry moving chord text")
        configuration.chordContent=1;configuration.chordOrder=3;configuration.chordScale=150
        applyScorePreview()
        var degreeMarkers=fixtureObserver.basePreview.filter(function(n){return n.degree})
        check(degreeMarkers.length===2 && degreeMarkers.every(function(n){return !n.chord}),"degree-only markers")
        check(degreeMarkers.every(function(n){return n.chordOrder===3 && n.chordScale===1.5}),"style protocol")
        check(degreeMarkers.every(function(n){return n.preferExistingHarmony===true}),"existing notation preferred")
        configuration.respectExistingHarmony=false;applyScorePreview()
        check(fixtureObserver.basePreview.filter(function(n){return n.degree}).every(function(n){return n.preferExistingHarmony===false}),"simultaneous analysis remains available")
        configuration.chordMask=false;applyScorePreview()
        check(fixtureObserver.basePreview.filter(function(n){return n.degree}).every(function(n){return n.chordMask===false}),"mask can be disabled")
        var originalRecords=analysisRecords
        var releases=JSON.parse(JSON.stringify(analysisRecords))
        var release=JSON.parse(JSON.stringify(releases[0]));release.tick=240;release.chord="Cm";release.degree="i";release.definition=1
        releases.splice(1,0,release);releases.forEach(function(f){f.imported=true});analysisRecords=releases;automaticRegions=Timeline.build(analysisRecords,collectPreferences(),firstTrack,[]);rebuildRegions();applyScorePreview()
        var releaseMarker=fixtureObserver.basePreview.filter(function(n){return n.chordTick===240})
        check(releaseMarker.length===1 && releaseMarker[0].tick===0,"release-only harmonic change anchors to its own tick")
        check(fixtureObserver.basePreview.filter(function(n){return n.tick===0 && n.chordTick!==undefined}).length===2,"one sustained source can own multiple markers")
        analysisRecords=originalRecords;automaticRegions=Timeline.build(analysisRecords,collectPreferences(),firstTrack,[]);rebuildRegions();applyScorePreview()
        configuration.chordContent=0;applyScorePreview()
        check(fixtureObserver.basePreview.filter(function(n){return n.chord}).length===2,"chord-only markers")
        check(!fixtureObserver.basePreview.some(function(n){return n.degree}),"degree text hidden")
        var baseCalls=fixtureObserver.baseCalls
        fixtureObserver.tick=480;followNativePosition()
        check(fixtureObserver.activeScoreTick===480,"fixed marker highlight follows real tick")
        check(fixtureObserver.baseCalls===baseCalls,"playback does not rebuild fixed annotations")
        result.modern={baseCount:fixtureObserver.basePreview.length,frames:analysisRecords.length}''')
# Extend the existing visual fixture, before its event loop starts.
script=script.replace("# Keep the original test path", '''script=script.replace(" QTimer.singleShot(1400,app.quit)"," QTimer.singleShot(1500,stable_begin)")
extra = r"""

def geometry():
 keys=['harmonySummary','harmonyFunctions','harmonyKeyboard']
 return [(root.findChild(QQuickItem,key).y(),root.findChild(QQuickItem,key).height()) for key in keys]

def stable_begin():
 window.resize(360,1100);root.setWidth(360);root.setHeight(1100)
 visual_state(False)
 QTimer.singleShot(60,stable_long)

def stable_long():
 global initial_geometry
 initial_geometry=geometry()
 visual_state(True)
 QTimer.singleShot(60,stable_check)

def stable_check():
 assert geometry()==initial_geometry,(initial_geometry,geometry())
 assert root.property('chromaticChord')
 capture(360,1100,'panel-stable-long.png')
 QTimer.singleShot(80,ribbon_begin)

def ribbon_begin():
 window.resize(1100,150);root.setWidth(1100);root.setHeight(150)
 QMetaObject.invokeMethod(root,'setRibbonPosition',Q_ARG(QVariant,0))
 QTimer.singleShot(60,ribbon_left)

def visual_state(long_text):
 root.setProperty('surfaceActive',False)
 values={'keyboardExpanded':True,'settingsExpanded':False,'chordRoot':2 if long_text else 0,'chordDefinition':0,
  'chordText':'Dmaj13/F# lengthy chord voicing' if long_text else 'C','degreeText':'V/V lengthy degree description' if long_text else 'I',
  'alternativesText':'Possible alternatives / '*12 if long_text else '',
  'matchText':'Incomplete and ambiguous. '*10 if long_text else 'Complete',
  'noticeText':'Configuration saved and analysis updated. '*10 if long_text else ''}
 for key,value in values.items():root.setProperty(key,value)
 rows=root.property('toneRows').toVariant()
 for row in rows:row['notes']='C10 / E10 / G10 / B10 / D10' if long_text else 'C4'
 root.setProperty('toneRows',rows)

def ribbon_left():
 global left_x
 left_x=root.findChild(QQuickItem,'harmonyRibbonGroup').x()
 QMetaObject.invokeMethod(root,'setRibbonPosition',Q_ARG(QVariant,1))
 QTimer.singleShot(60,ribbon_center)

def ribbon_center():
 global center_x
 center_x=root.findChild(QQuickItem,'harmonyRibbonGroup').x()
 QMetaObject.invokeMethod(root,'setRibbonPosition',Q_ARG(QVariant,2))
 QTimer.singleShot(60,ribbon_check)

def ribbon_check():
 right_x=root.findChild(QQuickItem,'harmonyRibbonGroup').x()
 assert left_x<center_x<=right_x,(left_x,center_x,right_x)
 print('Stable region geometry and left/center/right ribbon positions passed')
 QTimer.singleShot(80,app.quit)
"""
script=script.replace("QTimer.singleShot(500,checks)",extra+chr(10)+"QTimer.singleShot(500,checks)")
script=script.replace("from PyQt5.QtCore import QUrl,QMetaObject,QTimer","from PyQt5.QtCore import QUrl,QMetaObject,QTimer,Q_ARG,QVariant")
script=script.replace("from PyQt5.QtQuick import QQuickWindow","from PyQt5.QtQuick import QQuickWindow,QQuickItem")
# Keep the original test path''')
exec(compile(script,str(base/'test_modern_panel.py'),'exec'))
