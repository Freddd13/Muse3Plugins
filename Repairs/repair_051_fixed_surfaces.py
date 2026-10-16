from pathlib import Path
import re
ROOT=Path(__file__).resolve().parent.parent
def end(s,a):
 level=0;quote='';esc=False
 for i in range(a,len(s)):
  c=s[i]
  if quote:
   if esc:esc=False
   elif c=='\\':esc=True
   elif c==quote:quote=''
  elif c in "\"'":quote=c
  elif c=='{':level+=1
  elif c=='}':
   level-=1
   if level==0:return i+1
 raise ValueError('Unclosed block')
def component(s,key,identifier,loaders):
 a=s.index(key);b=end(s,s.index('{',a));inner=s[a:b]
 inner=re.sub(r'\n\s*parent:root\.(?:dualDetailActive|dualSummaryActive|ribbon)[^\n]*','',inner,count=1)
 if identifier=='harmonyDetails':
  inner=inner.replace('id: flick','id: flick\n            function scrollRange(){contentY=Math.max(0,rangeCard.y-6)}')
  inner=inner.replace('visible:!root.ribbon || detailPopup.opened || root.dualDetailActive','visible:true')
 elif identifier=='arrangementDetails':inner=inner.replace('visible:!root.ribbon || (typeof root.detailPanelVisible==="boolean" && root.detailPanelVisible) || floatingDetails.visible','visible:true')
 elif identifier=='harmonySummary':inner=inner.replace('visible:root.ribbon || root.dualSummaryActive','visible:true')
 else:inner=inner.replace('id:summary;parent:root.dualSummaryActive?root.summaryPanelHost:root','id:summary').replace('visible:root.ribbon||root.dualSummaryActive','visible:true')
 return s[:a]+f'Component {{id:{identifier}\n'+inner+'\n}\n'+loaders+s[b:]

p=ROOT/'HarmonyAssistant/HarmonyAssistant_MS3.qml';s=p.read_text(encoding='utf8')
models={'keyTonic':('currentIndex','int','0'),'keyMode':('currentIndex','int','0'),'autoChord':('checked','bool','true'),'pedalContext':('checked','bool','true'),'arpeggioWindow':('currentIndex','int','0'),'scope':('currentIndex','int','0'),'rootCombo':('currentIndex','int','0'),'qualityCombo':('currentIndex','int','0'),'followPlayback':('checked','bool','true'),'scoreColoring':('checked','bool','false'),'allColor':('checked','bool','false'),'showChords':('checked','bool','false'),'showFunctions':('checked','bool','false')}
props='\n    // Settings outlive the widgets in each dock surface.\n'
for name,(value,typ,default) in models.items():
 props+=f'    property QtObject {name}: QtObject {{property {typ} {value}:{default}}}\n'
 marker='id:'+name;at=s.index(marker);opening=s.rfind('{',0,at);closing=end(s,opening);block=s[opening:closing];block=block.replace(marker,marker+'Control',1)
 if value=='checked':
  block=re.sub(r'checked:(?:true|false)',f'checked:root.{name}.checked',block,count=1)
  if 'onToggled:' in block:
   block=block.replace('onToggled:{',f'onToggled:{{root.{name}.checked=checked;',1) if 'onToggled:{' in block else block.replace('onToggled:',f'onToggled:{{root.{name}.checked=checked;',1).rstrip()[:-1]+'}}'
  else:block=block[:-1]+f'onToggled:root.{name}.checked=checked'+'}'
 else:
  block=block.replace(marker+'Control',marker+f'Control;currentIndex:root.{name}.currentIndex;onCurrentIndexChanged:root.{name}.currentIndex=currentIndex',1)
 s=s[:opening]+block+s[closing:]
s=s.replace('    property bool expanded: flick.width >= 680',props+'    property var detailFlick:root.dualDetailActive?auxHarmonyDetails.item:root.ribbon?popupHarmonyDetails.item:inlineHarmonyDetails.item\n    property bool expanded:detailFlick?detailFlick.width>=680:false')
s=s.replace('Qt.callLater(function(){flick.contentY=Math.max(0,rangeCard.y-6)})','Qt.callLater(function(){if(root.detailFlick)root.detailFlick.scrollRange()})')
s=component(s,'Flickable {\n            id: flick','harmonyDetails','''        Loader {id:inlineHarmonyDetails;anchors.fill:parent;active:!root.ribbon;sourceComponent:harmonyDetails}
        Loader {id:popupHarmonyDetails;parent:detailPopup.contentItem;anchors.fill:parent;active:root.ribbon&&!root.dualDetailActive;sourceComponent:harmonyDetails}
        Loader {id:auxHarmonyDetails;parent:root.detailPanelHost;anchors.fill:parent;active:root.dualDetailActive&&!!root.detailPanelHost;sourceComponent:harmonyDetails}
''')
s=component(s,'Item {\n            id:summarySurface','harmonySummary','''        Loader {anchors.fill:parent;active:root.ribbon&&!root.dualSummaryActive;sourceComponent:harmonySummary}
        Loader {parent:root.summaryPanelHost;anchors.fill:parent;active:root.dualSummaryActive&&!!root.summaryPanelHost;sourceComponent:harmonySummary}
''')
p.write_text(s,encoding='utf8',newline='\n')

p=ROOT/'ArrangementAssistant/ArrangementAssistant_MS3.qml';s=p.read_text(encoding='utf8');s=s.replace('    property var current:list.currentIndex','    property int currentIssueIndex:-1\n    property var details:root.dualDetailActive?auxArrangementDetails.item||root:root.ribbon?popupArrangementDetails.item||root:inlineArrangementDetails.item||root\n    property var current:list.currentIndex')
s=s.replace('list.currentIndex','root.currentIssueIndex');s=s.replace('id:list;objectName:', 'id:list;currentIndex:root.currentIssueIndex;onCurrentIndexChanged:root.currentIssueIndex=currentIndex;objectName:')
s=component(s,'Item {\n        id:details','arrangementDetails','''    Loader {id:inlineArrangementDetails;anchors.fill:parent;active:!root.ribbon;sourceComponent:arrangementDetails}
    Loader {id:popupArrangementDetails;parent:floatingDetails.contentItem;anchors.fill:parent;active:root.ribbon&&!root.dualDetailActive;sourceComponent:arrangementDetails}
    Loader {id:auxArrangementDetails;parent:root.detailPanelHost;anchors.fill:parent;active:root.dualDetailActive&&!!root.detailPanelHost;sourceComponent:arrangementDetails}
''')
s=component(s,'RowLayout {\n        id:summary;','arrangementSummary','''    Loader {anchors.fill:parent;active:root.ribbon&&!root.dualSummaryActive;sourceComponent:arrangementSummary}
    Loader {parent:root.summaryPanelHost;anchors.fill:parent;active:root.dualSummaryActive&&!!root.summaryPanelHost;sourceComponent:arrangementSummary}
''')
p.write_text(s,encoding='utf8',newline='\n')
print('摘要和详情各自在固定窗口建立控件，共用设置与分析数据。')
