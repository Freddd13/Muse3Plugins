"""Stage maintained host files, merging the guide with already committed additions."""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
HOST = ROOT.parent.parent / "muse3_dev/MuseScore"


def git(repo, *args, data=None):
    return subprocess.run(["git", "-C", str(repo), *args], input=data,
                          capture_output=True, check=True).stdout


def main():
    if git(HOST, "diff", "--cached", "--name-only").strip():
        raise RuntimeError("先核对已暂存的修改，再准备本批文件。")
    files = []
    for source in (ROOT / "native").rglob("*"):
        if not source.is_file():
            continue
        relative = source.relative_to(ROOT / "native").as_posix()
        if relative in ("AGENTS.md", "personal/USER_GUIDE.md"):
            continue
        if (HOST / relative).read_bytes() != source.read_bytes():
            raise RuntimeError("源码尚未同步：" + relative)
        files.append(relative)
    git(HOST, "add", "--", *files)
    ours = (ROOT / "native/personal/USER_GUIDE.md").read_bytes()
    base = git(ROOT.parent, "show", "HEAD:P2/native/personal/USER_GUIDE.md")
    theirs = git(HOST, "show", "HEAD:personal/USER_GUIDE.md")
    folder = ROOT / "out/stage-guide"
    folder.mkdir(parents=True, exist_ok=True)
    paths = [folder / name for name in ("ours", "base", "theirs")]
    for path, value in zip(paths, (ours, base, theirs)):
        path.write_bytes(value)
    merged = subprocess.run(["git", "merge-file", "-p", *map(str, paths)],
                            capture_output=True, check=True).stdout
    blob = git(HOST, "hash-object", "-w", "--stdin", data=merged).decode().strip()
    git(HOST, "update-index", "--cacheinfo", "100644", blob, "personal/USER_GUIDE.md")
    git(HOST, "diff", "--cached", "--check")
    print(git(HOST, "diff", "--cached", "--stat").decode())


if __name__ == "__main__":
    main()
