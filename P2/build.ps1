param([string[]]$Projects=@('mscore/mscoreapp','mtest/mscore/pluginhost/tst_pluginhost'),[string]$Batch='058')
$ErrorActionPreference='Stop'
$taskRoot=Split-Path -Parent $PSScriptRoot
$taskHost='E:/programming/funcodes/muse3_dev/MuseScore'
$taskBuild="$taskHost/msvc.build_harmony_release_x64"
$taskPython='C:/Users/Fred/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$taskBuilder='C:/Program Files (x86)/Microsoft Visual Studio/2019/BuildTools/MSBuild/Current/Bin/MSBuild.exe'
$taskOutput="$PSScriptRoot/out"
New-Item -ItemType Directory -Force -Path $taskOutput | Out-Null
& $taskPython "$PSScriptRoot/apply.py"
if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}
& 'C:/Program Files/CMake/bin/cmake.exe' -S $taskHost -B $taskBuild > "$taskOutput/$Batch-configure.txt" 2>&1
if($LASTEXITCODE -ne 0){Get-Content "$taskOutput/$Batch-configure.txt" -Tail 18;exit $LASTEXITCODE}
$env:_CL_='/MP2'
$taskProjects=[System.Collections.Generic.List[string]]::new()
foreach($taskProject in $Projects){
 if($taskProject -like 'mtest/mscore/*' -and -not $taskProjects.Contains('mtest/testutils_mscoreapp')){$taskProjects.Add('mtest/testutils_mscoreapp')}
 if(-not $taskProjects.Contains($taskProject)){$taskProjects.Add($taskProject)}
}
foreach($taskProject in $taskProjects){
 $taskName=Split-Path $taskProject -Leaf
 $taskExtra=@();if($taskProject -like 'mtest/*'){$taskExtra=@("/p:ForceImportBeforeCppTargets=$taskRoot/P0/tests/NoPch.props")}
 $taskLog="$taskOutput/$Batch-$taskName-build.txt"
 # Application targets update their audio/core dependencies. Test helpers are
 # rebuilt explicitly so the test-only NoPch props stay out of production libs.
 $taskReferences=if($taskProject -eq 'mscore/mscoreapp' -or $taskProject -eq 'main/mscore'){'true'}else{'false'}
 & $taskBuilder "$taskBuild/$taskProject.vcxproj" /p:Configuration=Release /p:Platform=x64 "/p:BuildProjectReferences=$taskReferences" /m:1 @taskExtra /noconsolelogger /fl "/flp:logfile=$taskLog;verbosity=minimal"
 $taskCode=$LASTEXITCODE
 Get-Content -LiteralPath $taskLog -Tail 10
 if($taskCode -ne 0){exit $taskCode}
}
