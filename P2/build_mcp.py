"""Build the directory-based Windows MCP package on E, using the existing runtime."""
from pathlib import Path
import os
import json
import hashlib
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent / "mcp-musescore"
PYTHON = REPO / ".venv/Scripts/python.exe"


def main():
    output = ROOT / "out"
    args = [str(PYTHON), "-m", "PyInstaller", "--noconfirm", "--onedir", "--console",
            "--name", "MuseScoreMCP", "--distpath", str(output / "mcp-dist"),
            "--workpath", str(output / "mcp-build"), "--specpath", str(output / "mcp-spec"),
            "--paths", str(REPO), "--collect-data", "fastmcp",
            "--copy-metadata", "fastmcp", "--copy-metadata", "websockets",
            "--copy-metadata", "tomlkit", "--add-data", str(REPO / "src/ui/score_viewer.html") + os.pathsep + "src/ui",
            str(REPO / "launcher.py")]
    log = output / "063-mcp-package.txt"
    output.mkdir(parents=True, exist_ok=True)
    with log.open("w", encoding="utf8") as stream:
        code = subprocess.call(args, cwd=REPO, stdout=stream, stderr=subprocess.STDOUT,
                               env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    if code:
        print(log)
        raise SystemExit(code)
    package = output / "mcp-dist/MuseScoreMCP"
    # Include the exact dependency versions and their distributed license files.
    metadata = subprocess.check_output([str(PYTHON), "-c", """
import importlib.metadata as m, json, pathlib, sys
items=[]
for d in m.distributions():
    licenses=[]
    for f in d.files or []:
        if any(part.lower().startswith(('license','licence','copying','notice')) for part in f.parts):
            p=pathlib.Path(d.locate_file(f))
            if p.is_file(): licenses.append(str(p))
    items.append({'name':d.metadata['Name'],'version':d.version,'licenses':licenses})
print(json.dumps({'python':sys.version,'pythonLicense':str(pathlib.Path(sys.base_prefix)/'LICENSE.txt'),'packages':items}))
"""], text=True, encoding="utf8")
    manifest = json.loads(metadata)
    import shutil
    for item in manifest["packages"]:
        for index, license_file in enumerate(item.pop("licenses")):
            destination = package / "licenses" / item["name"] / (str(index) + "-" + Path(license_file).name)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(license_file, destination)
    for name, source in (("MuseScoreMCP", REPO / "LICENSE"), ("Python", Path(manifest.pop("pythonLicense")))):
        if source.is_file():
            destination = package / "licenses" / (name + ".txt")
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
    manifest["sourceBaseCommit"] = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()
    manifest["sourceFilesSHA256"] = {str(p.relative_to(REPO)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in [REPO / "launcher.py", REPO / "server.py", *sorted((REPO / "src").rglob("*.py"))]}
    manifest["launcherSHA256"] = hashlib.sha256((REPO / "launcher.py").read_bytes()).hexdigest()
    (package / "build-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf8")
    print(log)


if __name__ == "__main__":
    main()
