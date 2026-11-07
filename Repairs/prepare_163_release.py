from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
text=(ROOT/'Repairs/check_162_program.py').read_text('utf8').replace('0.162','0.163').replace('0.161','0.162').replace('repair-162','repair-163')
text=text.replace("('timing',ROOT/'P2/out/repair-161/performance-timing-161.mscz')","('controls',OUT/'reference-control-163.mscz')").replace("roundtrip-timing161.mscz","roundtrip-reference163.mscz")
text=text.replace("report['version']='0.163.0'","assert report['controls-mid']==report['stock-mid'],'Ordinary-version reference roundtrip changed MIDI'\nreport['version']='0.163.0'")
(ROOT/'Repairs/check_163_program.py').write_text(text,encoding='utf8',newline='\n')
text=(ROOT/'Repairs/install_162.py').read_text('utf8').replace('0.162','0.163').replace('repair-162','repair-163').replace('release162','release163')
text=text.replace('shutil.copy2(str(SOURCE),str(TARGET))','''panel=Path("workflow/panels/ReferencePlayer/ReferencePlayer.view.qml")
panelTarget=INSTALL/panel
panelBackup=OUT/"previous-installed-ReferencePlayer.view.qml"
if not panelBackup.is_file():shutil.copy2(panelTarget,panelBackup)
shutil.copy2(HOST/"share"/panel,panelTarget)
if panelTarget.read_bytes()!=(HOST/"share"/panel).read_bytes():raise ValueError("Reference interface differs")
shutil.copy2(str(SOURCE),str(TARGET))''')
(ROOT/'Repairs/install_163.py').write_text(text,encoding='utf8',newline='\n')
text=(ROOT/'Repairs/finalize_162.py').read_text('utf8').replace('repair-162','repair-163').replace('0.162','0.163').replace('N6','N7')
text=text.replace("['spectrum-checks.txt','pluginhost-spectrumInteraction162.txt','pluginhost-spectrumInitialSourceAndChoice.txt']","['pluginhost-referenceControls163.txt']")
start=text.index('helpers=');end=text.index("subprocess.run(['git','add','--',*paths]",start)
text=text[:start]+'''helpers=['prepare_163.py','prepare_163_wiring.py','sync_163.py','build_163.py','format_163.py','run_163_checks.py','prepare_163_docs.py','finish_163_docs.py','prepare_163_release.py','check_163_program.py','install_163.py','finalize_163.py']
paths=['P2/native/'+name for name in files]+['Repairs/'+name for name in helpers]+['Planning/REFERENCE_CONTROLS_163_DESIGN.md','Planning/PLAYBACK_MULTITRACK_VIDEO_IMPLEMENTATION.md']
'''+text[end:]
text=text.replace('Improve 0.163 spectrum reuse, harmonic guides and MIDI comparison','Add 0.163 reference range controls with split playback and undo').replace('Deliver N7 spectrum preparation, interaction and checked guides','Deliver N7 reference ranges, split controls and verified instructions')
(ROOT/'Repairs/finalize_163.py').write_text(text,encoding='utf8',newline='\n')
