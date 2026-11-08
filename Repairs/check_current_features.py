"""Exercise existing user workflows against the current native build."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys

R = Path(__file__).resolve().parents[1]
H = R.parent/'muse3_dev/MuseScore'
B = H/'msvc.build_harmony_release_x64'
O = R/'P2/out/usability-167'
runtime = R/'P1/out/final-regression/runtime'
I = H/'msvc.install_repair_current_x64'
O.mkdir(parents=True, exist_ok=True)
sys.stdout.reconfigure(encoding='utf8',errors='replace')
suite='pluginhost'
if '--suite' in sys.argv:
    index=sys.argv.index('--suite')
    suite=sys.argv[index+1]
    del sys.argv[index:index+2]
if suite not in ('pluginhost','performanceeditor','p1native','p0native'):
    raise ValueError(suite)
env = dict(os.environ, TEMP=str(R/'P2/out/check-temp'), TMP=str(R/'P2/out/check-temp'),
           QT_QPA_PLATFORM=os.environ.get('USABILITY_QPA','windows'), QT_QUICK_BACKEND='software',
           QML_DISABLE_DISK_CACHE='1', KUMO_MCP_AUTOSTART='0',
           HARMONY_TEST_ARTIFACTS=str(O), PERFORMANCE_NO_SYSTEM_CLIPBOARD='1',
           P0_TEST_SOUNDFONT=str(I/'sound/MuseScore_General.sf3'),
           KUMO_KAWAI_SF2='E:/music_fonts/[GD] Kawai ES100 Concert Grand 1 [V3].sf2',
           P2_LAYOUT_PROFILE='C:/Users/Fred/AppData/Roaming/MuseScore/MuseScore3Evo.ini',
           P2_GUI_SCORE='C:/Users/Fred/OneDrive - yunzd/arr/如果有来生/如果有来生-release5.mscz')
env.update(P2_COMMON_PIANO_AUDIO='1',P2_SOURCE_MODE_NATIVE='1')
if '--sync-probes' in sys.argv:
    sys.argv.remove('--sync-probes')
    for filename in ('composition_flow_tests.inc','workspace_093_tests.inc','playback_159_tests.inc',
                     'reference_input_120_tests.inc','arrangement_candidate_quality_tests.inc','layout_079_tests.inc'):
        path=Path('mtest/mscore/pluginhost')/filename
        shutil.copy2(R/'P2/native'/path,H/path)
    path=Path('mscore/workflow/workspaceviews.cpp')
    shutil.copy2(R/'P2/native'/path,H/path)
    path=Path('mscore/performanceeditor/performanceux.cpp')
    shutil.copy2(R/'P2/native'/path,H/path)
if '--build' in sys.argv:
    sys.argv.remove('--build')
    msbuild='C:/Program Files/Microsoft Visual Studio/2022/Community/MSBuild/Current/Bin/MSBuild.exe'
    for label,project in [('app','mscore/mscoreapp.vcxproj'),('host',f'mtest/mscore/{suite}/tst_{suite}.vcxproj')]:
        args=[msbuild,str(B/project),'/nologo','/m:1','/p:Configuration=Release','/p:Platform=x64','/p:BuildProjectReferences=false']
        if label=='host': args.append('/p:ForceImportBeforeCppTargets='+str(R/'P2/out/repair-166/no-test-pch.props'))
        with (O/('build-'+suite+'-'+label+'.txt')).open('w',encoding='utf8') as stream:
            code=subprocess.call(args,cwd=H,env=dict(env,_CL_='/MP2'),stdout=stream,stderr=subprocess.STDOUT)
        if code: raise RuntimeError('Build failed: '+label)
        print(label+' built',flush=True)
    shutil.copy2(B/f'mtest/mscore/{suite}/Release/tst_{suite}.exe',runtime/f'bin/tst_{suite}.exe')

# Use the released media module and pages, retaining the existing Qt runtime.
for folder in ('workflow','plugins'):
    for source in (I/folder).rglob('*'):
        if source.is_file():
            target=runtime/folder/source.relative_to(I/folder)
            if not target.is_file() or hashlib.sha256(target.read_bytes()).digest()!=hashlib.sha256(source.read_bytes()).digest():
                target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(source,target)
source=I/'bin/kumo_referenceaudio.dll'
target=runtime/'bin/kumo_referenceaudio.dll'
if not target.is_file() or hashlib.sha256(target.read_bytes()).digest()!=hashlib.sha256(source.read_bytes()).digest():
    shutil.copy2(source,target)
groups={
 'daily':['continuousComposition','workspaceSideWidthsRoundTrip','existingEditorProfileFirstOpen',
          'paletteRemainsInteractiveAfterPlayback','referencePanelsAfterPlayback120',
          'velocityPeekHold159','keyboardPointer159','scoreBandStaysNearSelectedSystem'],
 'assistance':['continuousWorkflowSessions','legacyVariantsSaveBeforeSwitch','harmonyWindow112',
               'harmonySpellingAcrossViews109','harmonyPanelRangeDrag114','harmonyCloseAll123',
               'arrangementActualPanel122','traditionalVoicingCandidateFlow'],
 'sources':['vstInstrumentFirstScanAndRestoreSound','vstEffectsHaveOwnPresets',
            'commonPianoPlaybackSnapshot128','sourceModeDuringPlayback129',
            'kawaiReverbSend159','privateSf2Reverb159'],
 'output':['graceSpacing159','systemLockMenuRange138','nativeScoreImageNotation141',
           'aiSuggestionState144','scoreVideoPanel164','midiEventPostprocessing122'],
}
name=sys.argv[1]
cases=groups.get(name,sys.argv[2:])
if not cases: raise ValueError(name)
log=O/(name+'.txt')
with (O/(name+'-process.txt')).open('w',encoding='utf8') as stream:
    code=subprocess.call([str(runtime/f'bin/tst_{suite}.exe'),*cases,'-o',str(log)+',txt'],
                         cwd=runtime/'bin',env=env,stdout=stream,stderr=subprocess.STDOUT,timeout=420)
if log.exists():
    print('\n'.join(line for line in log.read_text('utf8',errors='replace').splitlines()
        if line.startswith(('PASS','FAIL','QFATAL','Totals:'))))
print('Result:',name,code,'log:',log,flush=True)
raise SystemExit(code)
