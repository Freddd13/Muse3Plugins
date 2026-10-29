"""Create a separate program folder with personal tools switched off."""
from pathlib import Path
import argparse
import re
import shutil


def disable_personal_features(path):
    """Change this one setting while retaining the copied installation's others."""
    raw = path.read_bytes() if path.is_file() else b""
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    newline = "\r\n" if "\r\n" in text else "\n"
    lines = text.splitlines()
    in_features = False
    section_end = None
    found = False
    for index, line in enumerate(lines):
        section = re.fullmatch(r"\s*\[([^]]+)\]\s*(?:[;#].*)?", line)
        if section:
            if in_features and section_end is None:
                section_end = index
            in_features = section.group(1).strip().casefold() == "features"
        elif in_features and re.match(r"\s*enable_exp_feature\s*=", line, re.I):
            lines[index] = "enable_exp_feature=false"
            found = True
    if not found:
        if section_end is not None:
            lines.insert(section_end, "enable_exp_feature=false")
        elif in_features:
            lines.append("enable_exp_feature=false")
        else:
            if lines and lines[-1].strip():
                lines.append("")
            lines.extend(["[features]", "enable_exp_feature=false"])
    output = (newline.join(lines) + newline).encode("utf8")
    path.write_bytes((b"\xef\xbb\xbf" if bom else b"") + output)


def make_share_package(source, destination):
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if not (source / "bin/MuseScore3Evo.exe").is_file():
        raise ValueError("没有找到完整的程序文件夹。")
    if destination.exists():
        raise ValueError("目标文件夹已经存在，请选择新位置。")
    if destination.is_relative_to(source):
        raise ValueError("请选择程序目录以外的位置。")
    shutil.copytree(source, destination)
    disable_personal_features(destination / "bin/kumo.ini")
    return destination / "bin/MuseScore3Evo.exe"


def main():
    parser = argparse.ArgumentParser(description="生成关闭个人扩展的分享文件夹")
    parser.add_argument("destination", type=Path, help="尚不存在的目标文件夹")
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[2] / "muse3_dev/MuseScore/msvc.install_repair_current_x64"
    try:
        program = make_share_package(source, args.destination)
    except ValueError as error:
        parser.error(str(error))
    print("分享程序已放在：", program)


if __name__ == "__main__":
    main()
