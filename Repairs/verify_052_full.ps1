param([string]$Install='E:/programming/funcodes/muse3_dev/MuseScore/msvc.install_repair_0_52_x64',[string]$Label='full')
$env:PERFORMANCE_NO_SYSTEM_CLIPBOARD='1'
$env:PERFORMANCE_GUI_TIMEOUT='240'
$env:P0_TEST_SOUNDFONT='E:/programming/funcodes/muse3_dev/MuseScore/msvc.install_p1_x64/sound/MuseScore_General.sf3'
$env:PERFORMANCE_REFERENCE_MODULE='E:/programming/funcodes/muse3_dev/MuseScore/msvc.build_harmony_release_x64/mscore/referenceaudio/Release/kumo_referenceaudio.dll'
$taskPython='C:/Users/Fred/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$taskBuild='E:/programming/funcodes/muse3_dev/MuseScore/msvc.build_harmony_release_x64'
foreach($taskCase in @('p1native','performanceeditor','p0native')){
 & $taskPython Repairs/tests/run_gui_cases.py "$taskBuild/mtest/mscore/$taskCase/Release/tst_$taskCase.exe" $Install "Repairs/out/repair-052-$Label-$taskCase" > "Repairs/out/repair-052-$Label-$taskCase-summary.txt"
 $taskResult=$LASTEXITCODE
 Get-Content "Repairs/out/repair-052-$Label-$taskCase-summary.txt" -Tail 8
 if($taskResult -ne 0){exit $taskResult}
}
$env:PERFORMANCE_BENCHMARK='1'
& $taskPython Repairs/tests/run_gui_cases.py "$taskBuild/mtest/mscore/performanceeditor/Release/tst_performanceeditor.exe" $Install 'Repairs/out/repair-052-benchmark' actualHostAndMouseInteraction largeScoreBenchmark > Repairs/out/repair-052-benchmark-summary.txt
$taskResult=$LASTEXITCODE
Get-Content Repairs/out/repair-052-benchmark-summary.txt -Tail 12
exit $taskResult
