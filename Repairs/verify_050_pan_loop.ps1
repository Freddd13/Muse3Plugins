param([switch]$SkipBuild)
$ErrorActionPreference='Stop'
$target='E:/programming/funcodes/muse3_dev/MuseScore/msvc.build_harmony_release_x64'
$builder='C:/Program Files (x86)/Microsoft Visual Studio/2019/BuildTools/MSBuild/Current/Bin/MSBuild.exe'
$python='C:/Users/Fred/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $python Repairs/apply_native.py
if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}
if(!$SkipBuild){
 $env:_CL_='/MP2'
 foreach($project in @('mscore/mscoreapp','mtest/mscore/p1native/tst_p1native','mtest/mscore/performanceeditor/tst_performanceeditor')){
  $name=Split-Path $project -Leaf
  $testOptions=@();if($project -like "mtest/*"){$testOptions=@("/p:ForceImportBeforeCppTargets=E:/programming/funcodes/muse3_plugins/P0/tests/NoPch.props")}
  & $builder "$target/$project.vcxproj" /p:Configuration=Release /p:Platform=x64 /p:BuildProjectReferences=false /m:1 @testOptions /noconsolelogger /fl "/flp:logfile=E:/programming/funcodes/muse3_plugins/Repairs/out/repair-050-latest-$name-build.txt;verbosity=minimal"
  if($LASTEXITCODE -ne 0){Get-Content "Repairs/out/repair-050-latest-$name-build.txt" -Tail 16;exit $LASTEXITCODE}
 }
}
$env:PERFORMANCE_NO_SYSTEM_CLIPBOARD='1'
$env:PERFORMANCE_GUI_TIMEOUT='180'
$env:PERFORMANCE_REFERENCE_MODULE="$target/mscore/referenceaudio/Release/kumo_referenceaudio.dll"
& $python Repairs/tests/run_gui_cases.py "$target/mtest/mscore/p1native/Release/tst_p1native.exe" 'E:/programming/funcodes/muse3_dev/MuseScore/msvc.install_repair_0_49_x64' 'Repairs/out/repair-050-reference-ui-latest' realPanelMouseActions > Repairs/out/repair-050-reference-ui-latest-summary.txt
$first=$LASTEXITCODE
Get-Content Repairs/out/repair-050-reference-ui-latest-summary.txt -Tail 16
& $python Repairs/tests/run_gui_cases.py "$target/mtest/mscore/performanceeditor/Release/tst_performanceeditor.exe" 'E:/programming/funcodes/muse3_dev/MuseScore/msvc.install_repair_0_49_x64' 'Repairs/out/repair-050-joint-transport-latest' actualHostAndMouseInteraction expressionPlaybackKeepsScoreAndBeat > Repairs/out/repair-050-joint-transport-latest-summary.txt
$second=$LASTEXITCODE
Get-Content Repairs/out/repair-050-joint-transport-latest-summary.txt -Tail 22
if($first -ne 0){exit $first}
exit $second
