# coding: utf-8
"""Append owned P1 translations; preserve P0 and upstream messages verbatim."""
from pathlib import Path
from xml.sax.saxutils import escape
import re
HOST=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
MIDI={
 'Outside selected measures / unmapped source':'范围外小节／来源未映射',
 'Voice not selected':'未选择此声部',
 'Preserved by user melody / voice protection':'用户保护的旋律／声部',
 'Source measure / staff / voice':'来源小节／谱表／声部',
 'Whole score':'全谱',
 'From measure (file order)':'起始小节（文件顺序）',
 'Through measure':'结束小节',
 'Crop voices':'裁剪声部',
 'Protect voices':'保护声部',
 'Protect highest onset line in each piano part':'保护各钢琴部分的最高起音线',
 'Choose at least one voice and a valid measure range.':'请选择至少一个声部及有效的小节范围。',
 'Stop playback and wait for rendering before preparing MIDI.':'请停播并等待渲染结束，再准备 MIDI。',
 'Measure range does not exist in %1. Adjust the range for this export.':'%1 中没有该小节范围，请为本次导出调整范围。',
 'Explicit voices for %1':'%1 的具体声部',
 'Crop and protect individual staff voices. These selections apply to this score in this export session; the common range/voice preset remains separate.':'按谱表选择裁剪或保护声部。此选择仅用于本谱的本次导出；通用范围／声部预设单独保存。',
 'Staff / voice':'谱表／声部',
 'Crop':'裁剪',
 'Protect':'保护',
 'Staff %1 · voice %2':'谱表 %1 · 声部 %2',
 'Choose at least one voice.':'请选择至少一个声部。',
 'Staff voices…':'谱表声部…',
 'Range / voices / protection…':'范围／声部／保护…',
}
def apply():
 f=HOST/'share/locale/mscore_zh_CN.ts';s=f.read_text(encoding='utf8')
 pattern=r'<context>\s*<name>Ms::MidiCropPanel</name>.*?</context>'
 match=re.search(pattern,s,re.S)
 if not match:raise RuntimeError('P0 MIDI translation context missing')
 block=match.group()
 for source,translation in MIDI.items():
  if '<source>'+escape(source)+'</source>' not in block:
   message='    <message>\n        <source>'+escape(source)+'</source>\n        <translation>'+escape(translation)+'</translation>\n    </message>\n'
   block=block.replace('</context>',message+'</context>')
 s=s[:match.start()]+block+s[match.end():]
 if f.read_bytes()!=s.encode('utf8'):f.write_bytes(s.encode('utf8'))
if __name__=='__main__':apply()
