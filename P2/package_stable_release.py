"""Assemble a complete Kumo program folder and its verified ZIP archive.

The running installation remains untouched. The bundle contains the selected
MCP runtime, current program, resources and committed user guide.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from unittest.mock import patch
import zipfile


ROOT = Path(__file__).resolve().parents[1]
HOST = ROOT.parent / "muse3_dev/MuseScore"


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def current_mcp(source: Path) -> str:
    directory = json.loads((source / "bin/tools/mcp/current.json").read_text("utf8"))["directory"]
    if not isinstance(directory, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", directory):
        raise ValueError("MCP运行目录无效。")
    if not (source / "bin/tools/mcp" / directory / "MuseScoreMCP.exe").is_file():
        raise ValueError("没有找到当前MCP运行程序。")
    return directory


def include_file(relative: Path, mcp: str) -> bool:
    parts = relative.parts
    if parts[:3] == ("bin", "tools", "mcp"):
        return len(parts) >= 4 and parts[3] in (mcp, "licenses", "current.json")
    if parts[:2] == ("personal", "tools"):
        return False
    return True


def stage_program(source: Path, program: Path, destination: Path, version: str) -> dict:
    source, program, destination = source.resolve(), program.resolve(), destination.resolve()
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("版本应为三个数字，如0.156.0。")
    if not (source / "bin/MuseScore3Evo.exe").is_file() or not program.is_file():
        raise ValueError("没有找到程序及完整运行文件。")
    if destination.exists() or destination.is_relative_to(source):
        raise ValueError("请选择安装目录外、尚不存在的目标文件夹。")
    binary = program.read_bytes()
    if not all(value in binary for value in (version.encode(), b"Kumo branch", b"Freddd13")):
        raise ValueError("程序版本或作者标识与本次发布不符。")
    mcp = current_mcp(source)
    files = sorted(p for p in source.rglob("*") if p.is_file() and include_file(p.relative_to(source), mcp))
    destination.mkdir(parents=True)
    for path in files:
        relative = path.relative_to(source)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(program if relative == Path("bin/MuseScore3Evo.exe") else path, target)
    (destination / "personal/VERSION").write_text(version + "\n", encoding="utf8")
    return {"version": version, "mcpVersion": mcp,
            "programSha256": digest(destination / "bin/MuseScore3Evo.exe"),
            "mcpSha256": digest(destination / "bin/tools/mcp" / mcp / "MuseScoreMCP.exe"),
            "copiedFiles": len(files)}


def export_committed_guide(destination: Path) -> dict:
    """Read the published main chapter, retaining unrelated local guide edits."""
    spec = importlib.util.spec_from_file_location("stable_guide", HOST / "personal/tools/package_user_guide.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    guide = HOST / "personal/USER_GUIDE.md"
    committed = subprocess.check_output(["git", "-C", str(HOST), "show", "HEAD:personal/USER_GUIDE.md"]).decode("utf8")
    original = Path.read_text

    def read_text(path, *args, **kwargs):
        return committed if path == guide else original(path, *args, **kwargs)

    repositories = [module.Repository.read(HOST, "https://github.com/Freddd13/MuseScore"),
                    module.Repository.read(ROOT, "https://github.com/Freddd13/Muse3Plugins"),
                    module.Repository.read(ROOT.parent / "mcp-musescore", "https://github.com/Freddd13/mcp-musescore")]
    aliases = {("personal/docs/USABILITY_REWORK_20261019.md", "review-images/20261019/"):
               ROOT / "Planning/review-images/20261019"}
    with patch.object(Path, "read_text", read_text):
        report = module.export_guide(HOST, destination, repositories, aliases)
    report["navigation"] = module.check_export(destination)
    if report["unresolved"] or report["navigation"]["broken"]:
        raise ValueError("程序包说明中有未找到的文件：" + json.dumps(report["unresolved"] + report["navigation"]["broken"], ensure_ascii=False))
    for name in ("VERSION", "CHANGELOG.md"):
        value = subprocess.check_output(["git", "-C", str(HOST), "show", "HEAD:personal/" + name])
        (destination / "personal" / name).write_bytes(value)
    return {"documents": report["documents"], "rewrittenLinks": len(report["updated_links"]),
            "localLinks": report["navigation"]["local_links"]}


def write_manifest(folder: Path, metadata: dict) -> dict:
    files = {p.relative_to(folder).as_posix(): {"bytes": p.stat().st_size, "sha256": digest(p)}
             for p in sorted(folder.rglob("*")) if p.is_file() and p != folder / "release-manifest.json"}
    manifest = dict(metadata, files=files)
    (folder / "release-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    return manifest


def archive_program(folder: Path, archive: Path) -> dict:
    if archive.exists() or archive.with_suffix(archive.suffix + ".partial").exists():
        raise ValueError("压缩包已存在，请选择新文件名。")
    manifest = json.loads((folder / "release-manifest.json").read_text("utf8"))
    temporary = archive.with_suffix(archive.suffix + ".partial")
    archive.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as output:
        for file in sorted(folder.rglob("*")):
            if file.is_file():
                output.write(file, (Path(folder.name) / file.relative_to(folder)).as_posix())
    # Re-read every member: catches missing files, corruption and staging changes.
    with zipfile.ZipFile(temporary) as output:
        expected = {folder.name + "/" + p for p in manifest["files"]} | {folder.name + "/release-manifest.json"}
        if set(output.namelist()) != expected:
            raise ValueError("压缩包文件与发布清单不同。")
        for relative, value in manifest["files"].items():
            raw = output.read(folder.name + "/" + relative)
            if len(raw) != value["bytes"] or hashlib.sha256(raw).hexdigest() != value["sha256"]:
                raise ValueError("文件校验不符：" + relative)
    temporary.replace(archive)
    result = {"archive": str(archive), "bytes": archive.stat().st_size,
              "sha256": digest(archive), "files": len(manifest["files"]) + 1}
    archive.with_suffix(archive.suffix + ".sha256").write_text(result["sha256"] + "  " + archive.name + "\n", encoding="ascii")
    return result


def main():
    parser = argparse.ArgumentParser(description="整理完整程序，附带说明、校验清单和ZIP压缩包")
    parser.add_argument("destination", type=Path)
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--source", type=Path, default=HOST / "msvc.install_repair_current_x64")
    parser.add_argument("--program", type=Path, default=HOST / "msvc.build_harmony_release_x64/main/Release/MuseScore3Evo.exe")
    args = parser.parse_args()
    version = (HOST / "personal/VERSION").read_text("utf8").strip()
    metadata = stage_program(args.source, args.program, args.destination, version)
    metadata["guide"] = export_committed_guide(args.destination)
    metadata["sourceCommit"] = subprocess.check_output(["git", "-C", str(HOST), "rev-parse", "HEAD"]).decode().strip()
    shutil.copy2(HOST / "LICENSE.GPL", args.destination / "LICENSE.GPL")
    write_manifest(args.destination, metadata)
    if args.archive:
        metadata["zip"] = archive_program(args.destination, args.archive)
    print(json.dumps(metadata, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
