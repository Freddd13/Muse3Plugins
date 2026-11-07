from pathlib import Path
R=Path(__file__).resolve().parents[1]
t=(R/'Repairs/check_163_program.py').read_text('utf8').replace('0.163','0.164').replace('0.162','0.163').replace('repair-163','repair-164').replace("('controls',OUT/'reference-control-163.mscz')","('video',OUT/'score-video-164.mscz')").replace('roundtrip-reference163.mscz','roundtrip-video164.mscz').replace("report['controls-mid']","report['video-mid']")
(R/'Repairs/check_164_program.py').write_text(t,encoding='utf8',newline='\n')
t=(R/'Repairs/install_163.py').read_text('utf8').replace('0.163','0.164').replace('repair-163','repair-164').replace('release163','release164')
t=t.replace('guides=publisher.export_committed_guide(INSTALL)', '''toolSpec=importlib.util.spec_from_file_location("video_tools",HOST/"personal/tools/install_score_video_tools.py")
tool=importlib.util.module_from_spec(toolSpec);toolSpec.loader.exec_module(tool)
videoTool=tool.install(Path("E:/ffmpeg-2021-12-20-git-631e31773b-full_build/ffmpeg-2021-12-20-git-631e31773b-full_build"),INSTALL/"bin")
guides=publisher.export_committed_guide(INSTALL)''').replace('guide=guides,sourceCommit=', 'guide=guides,videoTool=videoTool,sourceCommit=')
(R/'Repairs/install_164.py').write_text(t,encoding='utf8',newline='\n')
t=(R/'Repairs/finalize_163.py').read_text('utf8').replace('repair-163','repair-164').replace('0.163','0.164').replace('N7','N8')
t=t.replace("['pluginhost-referenceControls163.txt']","['pluginhost-scoreVideoPictures164.txt','spectrum-checks.txt']")
start=t.index('helpers=');end=t.index("subprocess.run(['git','add','--',*paths]",start)
t=t[:start]+'''helpers=['prepare_164.py','prepare_164_audio.py','prepare_164_document.py','wire_164.py','refine_164.py','polish_164.py','verify_164_ui.py','sync_164.py','format_164.py','build_164.py','run_164_checks.py','run_spectrum_164.py','check_video_164.py','prepare_164_docs.py','finish_164_docs.py','prepare_164_release.py','check_164_program.py','install_164.py','finalize_164.py']
paths=['P2/native/'+name for name in files]+['Repairs/'+name for name in helpers]+['Planning/SCORE_VIDEO_164_DESIGN.md','Planning/PLAYBACK_MULTITRACK_VIDEO_IMPLEMENTATION.md']
'''+t[end:]
t=t.replace('Add 0.164 reference range controls with split playback and undo','Add 0.164 native score video preview and MP4 ProRes export').replace('Deliver N8 reference ranges, split controls and verified instructions','Deliver N8 native score video, bounded sound and checked instructions')
(R/'Repairs/finalize_164.py').write_text(t,encoding='utf8',newline='\n')
