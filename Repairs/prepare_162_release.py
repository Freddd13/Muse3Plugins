"""Derive narrow release commands from the preceding checked batch."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for old,new in [('check_161_program.py','check_162_program.py'),('install_161.py','install_162.py')]:
    text=(ROOT/'Repairs'/old).read_text('utf8').replace('0.161','0.162').replace('0.160','0.161').replace('repair-161','repair-162').replace('release161','release162')
    if new=='check_162_program.py':
        text=text.replace("OUT/'performance-timing-161.mscz'","ROOT/'P2/out/repair-161/performance-timing-161.mscz'")
    else:
        text=text.replace('shutil.copy2(str(SOURCE),str(TARGET))','''module=HOST/"msvc.build_harmony_release_x64/mscore/referenceaudio/Release/kumo_referenceaudio.dll"
moduleTarget=INSTALL/"bin/kumo_referenceaudio.dll"
moduleBackup=OUT/"previous-kumo_referenceaudio.dll"
if not moduleBackup.is_file():shutil.copy2(moduleTarget,moduleBackup)
shutil.copy2(module,moduleTarget)
if moduleTarget.read_bytes()!=module.read_bytes():raise ValueError("Media module differs")
shutil.copy2(str(SOURCE),str(TARGET))''')
        text=text.replace('guide=guides,sourceCommit=','mediaSha256=hashlib.sha256(moduleTarget.read_bytes()).hexdigest(),guide=guides,sourceCommit=')
    (ROOT/'Repairs'/new).write_text(text,encoding='utf8',newline='\n')
