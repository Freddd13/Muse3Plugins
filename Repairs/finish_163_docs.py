from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[1];HOST=ROOT.parent/'muse3_dev/MuseScore';N=ROOT/'P2/native';OUT=ROOT/'P2/out/repair-163'
file=N/'personal/docs/REFERENCE_CONTROLS_163_CHECKS.md';text=file.read_text('utf8').replace('当前继续核对新版设置按钮、普通版保存和最终程序导出，再更新原安装目录。','新版范围设置与恢复按钮已实际点击，谱面选音正常；四个新场景和原有完整操作共五个场景通过。官方3.6.2打开并重存20音测试谱，音符、时值、指法、谱表与摆放元数据一致。最终程序普通MIDI与0.162一致，PDF正常。当前准备更新原安装目录。');file.write_bytes(text.encode('utf8'))
shutil.copy2(OUT/'reference-cross-line-163.png',N/'personal/docs/images/reference-cross-line-163.png')
