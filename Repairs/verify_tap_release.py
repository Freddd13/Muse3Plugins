# coding: utf-8
"""Build, exercise and install the reviewed Tap release; never commit on failure."""
from pathlib import Path
import subprocess, sys
ROOT=Path(__file__).resolve().parent
HOST=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
def run(args,where=ROOT.parent,log=None):
    print('运行：'+' '.join(map(str,args)),flush=True)
    if log:
        with (ROOT/'out'/log).open('wb') as stream:
            subprocess.run(list(map(str,args)),cwd=where,stdout=stream,stderr=subprocess.STDOUT,check=True)
    else: subprocess.run(list(map(str,args)),cwd=where,check=True)
run([sys.executable,'-X','utf8','Repairs/apply_native.py'])
run(['cmake','--build','msvc.build_harmony_release_x64','--config','Release','--target','mscore','--parallel','1'],HOST,'tap-035-build.log')
for case in ['p1native','p0native','pluginhost']:
    run([sys.executable,'-X','utf8','P1/tests/run_native_regressions.py','--build','--case',case])
    run([sys.executable,'-X','utf8','P1/tests/run_native_regressions.py','--case',case])
run(['cmake','--install','msvc.build_harmony_release_x64','--config','Release'],HOST,'tap-035-install.log')
run([str(HOST/'msvc.install_p1_x64/bin/MuseScore3Evo.exe'),'--long-version'],HOST,'tap-035-version.log')
run(['git','diff','--check','--','mscore','mtest','personal/CHANGELOG.md','personal/docs','personal/VERSION'],HOST)
index=HOST/'personal/docs/source-map.tsv'
rows=[]
for row in index.read_text(encoding='utf8').splitlines():
    fields=row.split('\t')
    if len(fields)==6 and (HOST/fields[1]).is_file():
        hits=[i for i,value in enumerate((HOST/fields[1]).read_text(encoding='utf8').splitlines(),1) if fields[2] in value]
        if len(hits)==1:fields[3]=str(hits[0])
    rows.append('\t'.join(fields))
index.write_bytes(('\n'.join(rows)+'\n').encode('utf8'))
print('Tap和原入口检查通过，安装完成。提交前仍须核对具体文件。',flush=True)
