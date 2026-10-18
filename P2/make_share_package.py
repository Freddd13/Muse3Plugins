"""Create a separate program folder with personal tools switched off."""
from pathlib import Path
import argparse
import shutil


def main():
    parser = argparse.ArgumentParser(description="生成关闭个人扩展的分享文件夹")
    parser.add_argument("destination", type=Path, help="尚不存在的目标文件夹")
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[2] / "muse3_dev/MuseScore/msvc.install_repair_current_x64"
    destination = args.destination.resolve()
    if destination.exists():
        parser.error("目标文件夹已经存在，请选择新位置。")
    if destination.is_relative_to(source.resolve()):
        parser.error("请选择程序目录以外的位置。")
    shutil.copytree(source, destination)
    (destination / "bin/kumo.ini").write_text("[features]\nenable_exp_feature=false\n", encoding="utf8")
    print("分享程序已放在：", destination / "bin/MuseScore3Evo.exe")


if __name__ == "__main__":
    main()
