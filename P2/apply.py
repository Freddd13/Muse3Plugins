"""Apply this batch after checking every destination; preserve unrelated edits."""
from pathlib import Path
import hashlib, json, shutil, subprocess

ROOT = Path(__file__).resolve().parent
HOST = ROOT.parent.parent / 'muse3_dev/MuseScore'

def same(a, b):
    return a.read_bytes() == b.read_bytes()

def main():
    from publish_runtime import prepare
    prepare()
    state_file = ROOT / 'out/applied.json'
    previous = json.loads(state_file.read_text('utf8')) if state_file.exists() else {}
    pending = [(p, HOST / p.relative_to(ROOT / 'native'))
               for p in (ROOT / 'native').rglob('*') if p.is_file()]
    for folder in ('HarmonyAssistant', 'PerformanceExpression', 'WorkflowCommon', 'ArrangementAssistant'):
        pending += [(p, HOST / 'share/plugins' / folder / p.name)
                    for p in (ROOT.parent / folder).iterdir()
                    if p.is_file() and p.suffix in ('.qml', '.js', '.md')]
    for src, dst in pending:
        if not dst.exists() or same(src, dst):
            continue
        key = dst.relative_to(HOST).as_posix()
        actual = hashlib.sha256(dst.read_bytes()).hexdigest()
        if key in previous:
            if actual != previous[key]:
                raise RuntimeError('目标有新的修改，请合并后继续：' + key)
        else:
            committed = subprocess.run(['git', 'show', 'HEAD:' + key], cwd=HOST, capture_output=True)
            if committed.returncode or committed.stdout != dst.read_bytes():
                raise RuntimeError('目标有尚未核对的修改：' + key)
    for src, dst in pending:
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists() or not same(src, dst):
            shutil.copyfile(src, dst)
        previous[dst.relative_to(HOST).as_posix()] = hashlib.sha256(dst.read_bytes()).hexdigest()
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps(previous, indent=2), 'utf8')
    print('已更新', len(pending), '个本批文件')

if __name__ == '__main__':
    main()
