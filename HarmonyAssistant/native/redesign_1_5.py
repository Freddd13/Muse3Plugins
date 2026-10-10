"""One-time UI migration; runtime components are the maintainable sources."""
from pathlib import Path
import re
base=Path(__file__).resolve().parents[1]
names=['HarmonyAssistant_MS3.qml','AppearanceEditor.qml','ConfigurationEditor.qml','ColorOption.qml','RangeEditor.qml']
for name in names:
    p=base/name;s=p.read_text(encoding='utf-8')
    assert 'DeskComboBox' not in s
    if name=='HarmonyAssistant_MS3.qml':
        s=s.replace('version: "1.4.0"','version: "1.5.0"',1)
        s=s.replace('    id: root','    id: root\n    UiTheme {id:theme}',1)
        s=s.replace('property color ink: "#253342"','property color ink: theme.text').replace('property color muted: "#6B7785"','property color muted: theme.muted')
        s=s.replace('property color detailPanelBackground:"#f4f4f4"','property color detailPanelBackground:theme.background')
        s=s.replace('x: 12\n                y: 12\n                width: Math.max(160, flick.width - 24)\n                spacing: 10','x: 8\n                y: 8\n                width: Math.max(160, flick.width - 16)\n                spacing: 6')
        s=s.replace('contentHeight: panel.height + 24','contentHeight: panel.height + 16')
        s=s.replace('font.pixelSize:19; font.bold:true','font.pixelSize:14; font.bold:true')
        s=s.replace('font.pixelSize:30; font.bold:true','font.pixelSize:28; font.bold:true')
        s=s.replace('font.pixelSize:21; font.bold:true','font.pixelSize:18; font.bold:true')
        s=s.replace('minimumBodyHeight:settingsExpanded ? 246 : 208','minimumBodyHeight:settingsExpanded ? 224 : 190')
        s=s.replace('radius: 6','radius: 1').replace('radius:4','radius:1')
        s=s.replace('width:3; height:parent.height-16; x:0; y:8','width:parent.width-12; height:2; x:6; y:parent.height-3')
        s=s.replace('color: modelData.present ? "#F2F5F7" : "#FAFBFC"','color: modelData.present ? theme.section : theme.field')
    else:
        identifier='row' if name=='ColorOption.qml' else 'editor'
        s=s.replace('id:'+identifier,'id:'+identifier+'\n    UiTheme {id:theme}',1)
    s=re.sub(r'\bToolButton\s*\{','DeskButton {flat:true;',s)
    for old,new in [('Button','DeskButton'),('Switch','DeskSwitch'),('ComboBox','DeskComboBox'),('SpinBox','DeskSpinBox')]:
        s=re.sub(r'\b'+old+r'\s*\{',new+' {',s)
    s=s.replace('font.family: "Microsoft YaHei UI"','font.family: Qt.application.font.family')
    s=s.replace('implicitHeight:32','implicitHeight:28')
    mapping={'#253342':'theme.text','#343a3f':'theme.text','#697077':'theme.muted','#f4f4f4':'theme.background',
        '#e0e0e0':'theme.subtleLine','#EBEEF0':'theme.subtleLine','#ffffff':'theme.field','#eef1f4':'theme.section',
        '#dce3e8':'theme.section','#d0e2ff':'theme.selected','#0043ce':'theme.accent','#c6c6c6':'theme.line'}
    for color,value in mapping.items():s=s.replace('"'+color+'"',value)
    with p.open('w',encoding='utf-8',newline='\n') as f:f.write(s)
print('Migrated five UI sources to the shared inspector controls')
