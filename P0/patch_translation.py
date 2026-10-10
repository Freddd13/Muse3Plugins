"""Add P0 Chinese UI strings without rewriting existing translation contexts."""
from xml.sax.saxutils import escape
from apply_native import HOST
import re

TAP={
'Tap tempo':'点击测速','Tap BPM':'Tap BPM 测速','Estimate tempo without changing the score':'测量速度，不修改乐谱',
'Quarter BPM: %1\nTap BPM: %2':'四分音符 BPM：%1\n点击单位 BPM：%2','Tap at least four beats':'点击至少四拍开始估计',
'%1 · %2 taps':'%1 · 已点击 %2 拍','Starting':'起步','Stable':'稳定','Unstable':'不稳定',
'Metronome is following the score':'节拍器正在跟随乐谱，停播后可应用',
'Independent metronome range: 20–400 quarter BPM':'独立节拍器范围：四分音符 BPM 20–400',
'Eighth note':'八分音符','Quarter note':'四分音符','Dotted quarter':'附点四分音符','Half note':'二分音符',
'Reset':'重置','TAP':'TAP','Set independent metronome':'设为独立节拍器'}
MIDI={
'Earlier release within the same pedal':'同一踏板内提前释放','Instrument not selected':'未选择此乐器',
'Source not uniquely identified':'无法唯一确定来源','Manual performance / grace / ornament':'手工演奏／倚音／装饰音',
'Ambiguous same-pitch retrigger':'同音重触或配对有歧义','Excluded by user':'用户排除',
'Already shorter than minimum':'原音已短于最小 gate','No safe shortening':'没有安全裁剪结果',
'No holding pedal':'没有延音踏板','Unsupported pedal/control semantics':'未支持的踏板／控制语义',
'Crosses pedal-up boundary':'跨越抬踏板边界','Note':'音符','Occurrence (ticks)':'起音位置（tick）',
'Original ms':'原长度 ms','New ms':'新长度 ms','Reason':'处理依据',
'Humanized release: conservative pedal mode':'人性化裁剪：保守踏板模式','Release settings…':'裁剪设置…',
'Compare…':'查看对比…','Also export original MIDI':'同时导出未裁剪 MIDI',
'Conservative MIDI release':'保守 MIDI 裁剪','Original length':'原长度比例','Next attack interval':'后续同声部起音间隔比例',
'Minimum gate':'最小 gate','Release jitter ± (0 disables)':'释放微随机 ±（0 为关闭）',
'Repeatable seed':'固定随机种子',
'Only piano notes with both release times in the same supported pedal window are shortened. Onsets and controllers remain unchanged.':'仅裁剪新旧释放点均位于同一有效踏板区间的钢琴音符。起音、力度和控制事件保持原样。',
'MIDI release':'MIDI 裁剪','Stop playback before preparing MIDI.':'请停播后准备 MIDI。',
'MIDI export':'MIDI 导出','Could not write %1: %2':'无法写入 %1：%2',
'Stop playback before preparing a comparison.':'请停播后准备对比。','MIDI release comparison':'MIDI 裁剪对比',
'All':'全部','Shortened':'已裁剪','Preserved':'保留','Overlay':'叠加','Stacked':'上下分列',
'Outline: original · Solid: export · Pedal: bottom lane · Positions include expanded repeats and pauses':'细轮廓：原长度 · 实心：导出长度 · 下轨：踏板 · 位置包含反复展开和暂停',
'Outline: original · Solid: export · Pedal: bottom lane':'细轮廓：原长度 · 实心：导出长度 · 下轨：踏板',
'Toggle exclusion':'排除／恢复此音','Recompute':'重算','Restore defaults':'恢复默认','Return to export':'返回导出',
'Crop piano part:':'裁剪钢琴部分：','Calculating… Closing cancels the task.':'计算中…关闭窗口会取消任务。',
'All piano parts':'全部钢琴部分','All instruments':'全部乐器',' · staff %1':' · 谱表 %1'}

def context(name,messages):
    return '<context>\n    <name>'+name+'</name>\n'+''.join('    <message>\n        <source>'+escape(k)+'</source>\n        <translation>'+escape(v)+'</translation>\n    </message>\n' for k,v in messages.items())+'</context>\n'
def apply():
    f=HOST/'share/locale/mscore_zh_CN.ts';s=f.read_text(encoding='utf-8')
    for name,messages in [('Ms::TapTempo',TAP),('Ms::MidiCropPanel',MIDI)]:
        block=context(name,messages)
        pattern=r'<context>\s*<name>'+re.escape(name)+r'</name>.*?</context>\n'
        s=re.sub(pattern,lambda _:block,s,flags=re.S) if re.search(pattern,s,re.S) else s.replace('</TS>',block+'</TS>')
    # Actions use MuseScore's shared translation context.
    action={'Tap BPM':TAP['Tap BPM'],'Tap tempo':TAP['Tap tempo'],'Estimate tempo without changing the score':TAP['Estimate tempo without changing the score']}
    match=re.search(r'<context>\s*<name>action</name>.*?</context>',s,re.S)
    assert match,'action translation context missing'
    current=match.group();new=current
    for source,translation in action.items():
        if '<source>'+source+'</source>' not in current:
            message=context('action',{source:translation}).split('</name>\n',1)[1].rsplit('</context>',1)[0]
            new=new.replace('</context>',message+'</context>')
    s=s[:match.start()]+new+s[match.end():]
    if f.read_bytes()!=s.encode('utf-8'):f.write_bytes(s.encode('utf-8'))

if __name__=='__main__':apply()
