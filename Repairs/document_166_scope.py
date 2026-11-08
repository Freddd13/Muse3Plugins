"""Unify the cumulative feature list and publish it with the current program."""
from pathlib import Path
import importlib.util
import subprocess

R = Path(__file__).resolve().parents[1]
N = R/'P2/native'
H = R.parent/'muse3_dev/MuseScore'
overview = 'personal/docs/FEATURES_166_OVERVIEW.md'
(H/overview).write_bytes((N/overview).read_bytes())
names = [overview, 'personal/USER_GUIDE.md', 'personal/docs/REWORK_PROGRESS.md',
         'personal/docs/ROUND_166_REVIEW.md', 'personal/CHANGELOG.md']
for base in (N,H):
    p = base/'personal/USER_GUIDE.md'
    text = p.read_text('utf8')
    anchor = '先按下面的任务找到入口。'
    text = text.replace(anchor, '0.166包含之前各版的累计修复和新增工具。[全部功能与使用入口](docs/FEATURES_166_OVERVIEW.md)集中列出编辑、和弦、录制、音源、试写、导出及AI等功能。\n\n'+anchor, 1)
    p.write_text(text, encoding='utf8', newline='\n')
    p = base/'personal/docs/REWORK_PROGRESS.md'
    text = p.read_text('utf8').replace('\n\n', '\n\n**当前完整范围：**此前01—33项修复与功能，连同最近N1—N9，继续一起维护。[全部功能、入口和后续顺序](FEATURES_166_OVERVIEW.md)。\n\n', 1)
    text = text.replace('当前已安装0.157。下表引用各批实际操作记录；', '当前已安装0.166。此前01—33项继续保留；最近的MIDI轨道、实际音长、频谱、原曲控件、视频和AI更新见上方N1—N9及[当前功能总览](FEATURES_166_OVERVIEW.md)。下表引用各批实际操作记录；', 1)
    text = text.replace('0.157随包235份说明，安装目录补至236份；源文档、链接和源码位置按本批重新检查', '0.166累计说明与总览随程序提供；源文档、链接和源码位置同步维护', 1)
    text = text.replace('| 动态乐谱视频、完整后处理、导入DAW的进一步操作 | 完成本轮后讨论具体输出软件和操作流程；当前MIDI先在F验证 |', '| 动态乐谱视频、完整后处理、导入DAW的进一步操作 | 动态乐谱已提供，见[SCORE_VIDEO_164_GUIDE.md](SCORE_VIDEO_164_GUIDE.md)；更完整的后处理与DAW交换继续设计 |', 1)
    p.write_text(text, encoding='utf8', newline='\n')
    p = base/'personal/docs/ROUND_166_REVIEW.md'
    text = p.read_text('utf8').replace('\n\n', '\n\n此前工作视图、和弦、表达、试写、记谱、音源和导出等01—33项继续纳入维护；[全部功能与入口](FEATURES_166_OVERVIEW.md)列出当前累计能力。本页N1—N9记录最近一轮的具体调整。\n\n',1)
    p.write_text(text, encoding='utf8', newline='\n')
    p = base/'personal/CHANGELOG.md'
    text = p.read_text('utf8').replace('## 0.166.0 — 2026-11-08\n', '## 0.166.0 — 2026-11-08\n\n- 补齐累计功能总览，统一此前01—33项与本轮N1—N9的范围、入口和后续顺序，更新进度中的旧版本及视频状态。\n',1)
    p.write_text(text, encoding='utf8', newline='\n')
p=R/'Planning/USABILITY_REWORK_20261019.md'
text=p.read_text('utf8').replace('\n\n', '\n\n当前累计程序0.166；此前01—33项与最近N1—N9继续一起维护。全部入口与后续顺序见[当前功能总览](../P2/native/personal/docs/FEATURES_166_OVERVIEW.md)。以下保留各轮原始记录。\n\n',1)
p.write_text(text,encoding='utf8',newline='\n')
p=R/'Planning/PLAYBACK_MULTITRACK_VIDEO_IMPLEMENTATION.md'
text=p.read_text('utf8').replace('\n\n', '\n\n本表N1—N9与此前01—33项共同构成当前范围；[全部功能与入口](../P2/native/personal/docs/FEATURES_166_OVERVIEW.md)列出累计能力和后续顺序。\n\n',1)
p.write_text(text,encoding='utf8',newline='\n')

def git(repo,*args,content=None):
    result=subprocess.run(['git',*args],cwd=repo,input=content,capture_output=True)
    if result.returncode: raise RuntimeError(result.stderr.decode('utf8',errors='replace'))
    return result.stdout

for repo in (H,R):
    assert not git(repo,'diff','--cached','--name-only').strip()
git(H,'add','--',*[n for n in names if n!='personal/USER_GUIDE.md'])
blob=git(H,'hash-object','-w','--stdin',content=(N/'personal/USER_GUIDE.md').read_bytes()).decode().strip()
git(H,'update-index','--cacheinfo','100644,'+blob+',personal/USER_GUIDE.md')
git(H,'diff','--cached','--check')
print(git(H,'commit','-m','Document all cumulative personal tools and full repair scope').decode('utf8',errors='replace'))
paths=['P2/native/'+n for n in names]+['Planning/USABILITY_REWORK_20261019.md',
       'Planning/PLAYBACK_MULTITRACK_VIDEO_IMPLEMENTATION.md','Repairs/document_166_scope.py']
git(R,'add','--',*paths)
git(R,'diff','--cached','--check')
print(git(R,'commit','-m','Unify previous repairs and new features in the current scope').decode('utf8',errors='replace'))
spec=importlib.util.spec_from_file_location('release166',R/'P2/package_stable_release.py')
publisher=importlib.util.module_from_spec(spec)
spec.loader.exec_module(publisher)
print('Published guide:',publisher.export_committed_guide(H/'msvc.install_repair_current_x64'))
for repo in (H,R):
    subprocess.run(['git','push','origin','HEAD'],cwd=repo,check=True)
