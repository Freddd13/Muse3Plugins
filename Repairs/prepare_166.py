"""Keep video and AI score images on MuseScore's native print geometry."""
from pathlib import Path

R = Path(__file__).resolve().parents[1]
N = R / 'P2/native'

def replace(name, before, after):
    p = N / name
    text = p.read_text('utf8')
    assert text.count(before) == 1, (name, before[:80])
    p.write_text(text.replace(before, after, 1), encoding='utf8', newline='\n')

replace('mscore/scorevideo/scorevideo.h',
        '    QSize pixels;\n    double firstStaffX = 0, firstStaffY = 0;',
        '    QSize pixels;\n    QRectF sourceRect;\n    double rasterScale = 1;\n    double firstStaffX = 0, firstStaffY = 0;')
replace('mscore/scorevideo/scorevideo.cpp',
        '                picture.firstStaffX = (group.staffOrigin.x() - group.crop.x()) * group.scale;',
        '                picture.sourceRect = group.crop;\n                picture.rasterScale = group.scale;\n                picture.firstStaffX = (group.staffOrigin.x() - group.crop.x()) * group.scale;')
replace('mscore/scorevideo/scorevideo.cpp',
        '                build.image.fill(Qt::transparent);',
        '                // TextFragment uses the image device DPI as well as pixelRatio.\n'
        '                // Match native PNG / foto output so text and music share one scale.\n'
        '                const int dotsPerMeter = qRound(DPI * group.scale * 1000 / INCH);\n'
        '                build.image.setDotsPerMeterX(dotsPerMeter);\n'
        '                build.image.setDotsPerMeterY(dotsPerMeter);\n'
        '                build.image.fill(Qt::transparent);')
replace('mscore/workflow/arrangementimages.cpp',
        '    image.fill(Qt::white);',
        '    const int dotsPerMeter=qRound(DPI*scale*1000/INCH);\n'
        '    image.setDotsPerMeterX(dotsPerMeter);image.setDotsPerMeterY(dotsPerMeter);\n'
        '    image.fill(Qt::white);')
replace('mscore/scorevideo/scorevideoframe.cpp',
        '        before = qMax(before, group.firstStaffX);\n'
        '        after = qMax(after, group.pixels.width() - group.firstStaffX);\n'
        '        above = qMax(above, group.firstStaffY);\n'
        '        below = qMax(below, group.pixels.height() - group.firstStaffY);',
        '        const double raster = group.rasterScale;\n'
        '        before = qMax(before, group.firstStaffX / raster);\n'
        '        after = qMax(after, (group.pixels.width() - group.firstStaffX) / raster);\n'
        '        above = qMax(above, group.firstStaffY / raster);\n'
        '        below = qMax(below, (group.pixels.height() - group.firstStaffY) / raster);')
replace('mscore/scorevideo/scorevideoframe.cpp',
        '    double scale = common;', '    double scale = common / picture.rasterScale;')

section = ('- 输出谱图和视频时，保留原谱的字体、字号、位置与分行。调用原生绘制还要核对图像分辨率、坐标和裁切；用含文字及线条的实际谱行比较最终画面。\n'
           '- 返工按用户要求的完整范围推进。入口修好后继续完成内容和操作检查，当前进度写清已经修好与正在处理的项目。\n')
p = R / 'AGENTS.md'
text = p.read_text('utf8')
at = '以上作为当前执行原则，指导后文的检查记录；每次工作按实际需要取舍。'
assert at in text
p.write_text(text.replace(at, section + '\n' + at, 1), encoding='utf8', newline='\n')
(R / 'P2/out/repair-166').mkdir(parents=True, exist_ok=True)
(R / 'P2/out/repair-166/agents-addition.md').write_text(section, encoding='utf8')
