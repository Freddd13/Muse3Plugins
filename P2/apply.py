"""Apply this batch after checking every destination; preserve unrelated edits."""
from pathlib import Path
import hashlib, json, subprocess

ROOT = Path(__file__).resolve().parent
HOST = ROOT.parent.parent / 'muse3_dev/MuseScore'

def merge_guide(ours, base, theirs):
    ours, base, theirs = (v.replace(b"\r\n", b"\n") for v in (ours, base, theirs))
    if ours == base:
        return theirs
    if theirs == base or ours == theirs:
        return ours
    if theirs.startswith(base):
        return ours + theirs[len(base):]
    if ours.startswith(base):
        return theirs + ours[len(base):]
    identity = hashlib.sha256(ours + base + theirs).hexdigest()[:16]
    folder = ROOT / 'out/guide-merge' / identity
    folder.mkdir(parents=True, exist_ok=True)
    paths = [folder / name for name in ('ours.md', 'base.md', 'theirs.md')]
    for path, value in zip(paths, (ours, base, theirs)):
        path.write_bytes(value)
    result = subprocess.run(['git', 'merge-file', '-p', *map(str, paths)], capture_output=True)
    if result.returncode:
        raise RuntimeError('用户说明有重叠修改，请核对：' + str(folder))
    return result.stdout

def main():
    from publish_runtime import prepare
    prepare()
    state_file = ROOT / 'out/applied.json'
    guide_base = ROOT / 'out/last-applied-guide.md'
    previous = json.loads(state_file.read_text('utf8')) if state_file.exists() else {}
    pending = [(p, HOST / p.relative_to(ROOT / 'native'))
               for p in (ROOT / 'native').rglob('*') if p.is_file()]
    for folder in ('HarmonyAssistant', 'PerformanceExpression', 'WorkflowCommon', 'ArrangementAssistant', 'ArrangementVariants'):
        pending += [(p, HOST / 'share/plugins' / folder / p.name)
                    for p in (ROOT.parent / folder).iterdir()
                    if p.is_file() and p.suffix in ('.qml', '.js', '.md')]
    prepared = []
    for src, dst in pending:
        key = dst.relative_to(HOST).as_posix()
        desired = src.read_bytes()
        merged = False
        if key == 'personal/USER_GUIDE.md' and dst.exists() and dst.read_bytes() != desired:
            base = guide_base.read_bytes() if guide_base.exists() else None
            if base is None:
                committed = subprocess.run(['git', 'show', 'HEAD:P2/native/personal/USER_GUIDE.md'], cwd=ROOT.parent, capture_output=True)
                if committed.returncode == 0:
                    base = committed.stdout
            if base is not None:
                desired = merge_guide(desired, base, dst.read_bytes())
                merged = True
        prepared.append((dst, desired))
        if not dst.exists() or dst.read_bytes() == desired or merged:
            continue
        actual = hashlib.sha256(dst.read_bytes()).hexdigest()
        if key in previous:
            if actual != previous[key]:
                raise RuntimeError('目标有新的修改，请合并后继续：' + key)
        else:
            committed = subprocess.run(['git', 'show', 'HEAD:' + key], cwd=HOST, capture_output=True)
            if committed.returncode or committed.stdout != dst.read_bytes():
                raise RuntimeError('目标有尚未核对的修改：' + key)
    for dst, desired in prepared:
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists() or dst.read_bytes() != desired:
            dst.write_bytes(desired)
        previous[dst.relative_to(HOST).as_posix()] = hashlib.sha256(dst.read_bytes()).hexdigest()
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps(previous, indent=2), 'utf8')
    guide_base.write_bytes((ROOT / 'native/personal/USER_GUIDE.md').read_bytes())
    print('已更新', len(pending), '个本批文件')

if __name__ == '__main__':
    main()
