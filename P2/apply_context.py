"""Copy only this batch's MCP files after checking their previous contents."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent
TARGET = ROOT.parent.parent / "mcp-musescore"


def main():
    state_file = ROOT / "out/context-applied.json"
    previous = json.loads(state_file.read_text("utf8")) if state_file.exists() else {}
    files = [p for p in (ROOT / "context").rglob("*")
             if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"]
    for source in files:
        relative = source.relative_to(ROOT / "context").as_posix()
        target = TARGET / relative
        if target.exists() and target.read_bytes() != source.read_bytes():
            actual = hashlib.sha256(target.read_bytes()).hexdigest()
            if relative in previous:
                if actual != previous[relative]:
                    raise RuntimeError("请先合并目标文件的新修改：" + relative)
            else:
                result = subprocess.run(["git", "show", "HEAD:" + relative], cwd=TARGET, capture_output=True)
                if result.returncode or result.stdout != target.read_bytes():
                    raise RuntimeError("目标文件有尚未核对的修改：" + relative)
    for source in files:
        relative = source.relative_to(ROOT / "context").as_posix()
        target = TARGET / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists() or source.read_bytes() != target.read_bytes():
            shutil.copyfile(source, target)
        previous[relative] = hashlib.sha256(target.read_bytes()).hexdigest()
    state_file.write_text(json.dumps(previous, indent=2), "utf8")
    print("已更新", len(files), "个MCP文件")


if __name__ == "__main__":
    main()
