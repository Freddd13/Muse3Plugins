param([string[]]$Projects=@('mscore/mscoreapp','mtest/mscore/pluginhost/tst_pluginhost'),[string]$Batch='053',[string[]]$ExcludePlugins=@('ArrangementAssistant'),[string[]]$NativePrefixes=@())
$ErrorActionPreference='Stop'
$taskBuild='E:/programming/funcodes/muse3_dev/MuseScore/msvc.build_harmony_release_x64'
$taskBuilder='C:/Program Files (x86)/Microsoft Visual Studio/2019/BuildTools/MSBuild/Current/Bin/MSBuild.exe'
$taskPython='C:/Users/Fred/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$taskApplyOptions=@();foreach($taskPlugin in $ExcludePlugins){$taskApplyOptions+=@('--exclude-plugin',$taskPlugin)}
foreach($taskPrefix in $NativePrefixes){$taskApplyOptions+=@('--native-prefix',$taskPrefix)}
& $taskPython Repairs/apply_native.py @taskApplyOptions
if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}
& 'C:/Program Files/CMake/bin/cmake.exe' -S 'E:/programming/funcodes/muse3_dev/MuseScore' -B $taskBuild > "Repairs/out/repair-$Batch-configure.txt" 2>&1
if($LASTEXITCODE -ne 0){Get-Content "Repairs/out/repair-$Batch-configure.txt" -Tail 15;exit $LASTEXITCODE}
$env:_CL_='/MP2'
foreach($taskProject in $Projects){
 $taskName=Split-Path $taskProject -Leaf
 $taskExtra=@();if($taskProject -like 'mtest/*'){$taskExtra=@('/p:ForceImportBeforeCppTargets=E:/programming/funcodes/muse3_plugins/P0/tests/NoPch.props')}
 $taskLog="E:/programming/funcodes/muse3_plugins/Repairs/out/repair-$Batch-$taskName-build.txt"
 & $taskBuilder "$taskBuild/$taskProject.vcxproj" /p:Configuration=Release /p:Platform=x64 /p:BuildProjectReferences=false /m:1 @taskExtra /noconsolelogger /fl "/flp:logfile=$taskLog;verbosity=minimal"
 $taskCode=$LASTEXITCODE
 if(Test-Path -LiteralPath $taskLog){Get-Content -LiteralPath $taskLog -Tail 10}
 if($taskCode -ne 0){exit $taskCode}
}
