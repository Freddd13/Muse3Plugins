"""Smoke the installed executable and installed plugin using isolated settings."""
from pathlib import Path
import hashlib,json,os,subprocess,sys

app=Path(sys.argv[1]).resolve()
output=Path(sys.argv[2]).resolve()
fixture=Path(sys.argv[3]).resolve()
output.mkdir(parents=True,exist_ok=True)
settings=output/'settings';settings.mkdir(exist_ok=True)
panel=app.parent.parent/'plugins/ArrangementAssistant/ArrangementAssistant_MS3.qml'
assert panel.exists(),panel
source='''import QtQuick 2.9
import MuseScore 3.0
import FileIO 3.0
MuseScore {
    id:root
    menuPath:"Plugins.Arrangement installed smoke"
    version:"1.0.0"
    requiresScore:true
    property var panel:null
    property bool nativeWorker:false
    FileIO {id:report}
    function finish(error) {
        var result={failures:error?[String(error)]:[],installedPanel:"PANEL_URL",analyzed:panel?panel.analyzed:false,
            issues:panel?panel.issues.length:0,status:panel?panel.status:"",nativeWorkerAvailable:nativeWorker,
            mode:"synchronous CLI fixture; production worker is covered by native Qt test"}
        report.source=String(Qt.resolvedUrl("installed-arrangement.json")).replace(/^file:\/\/\//,"")
        report.write(JSON.stringify(result,null,2))
        if(panel)panel.destroy()
    }
    onRun:{
        try {
            var component=Qt.createComponent("PANEL_URL")
            if(component.status!==Component.Ready)throw new Error(component.errorString())
            panel=component.createObject(root)
            if(!panel)throw new Error(component.errorString())
            panel.run()
            nativeWorker=panel.workerSource.length>0
            if(!nativeWorker)throw new Error("native read-only worker unavailable")
            // -p runs without an event loop. Check installed modules and paging
            // synchronously; real worker completion/cancel is tested in QtTest.
            panel.workerSource=""
            panel.start(false)
            for(var i=0;i<10000 && panel.running;i++)panel.slice()
            if(!panel.analyzed)throw new Error("analysis incomplete: "+panel.status)
            finish(null)
        }catch(error){finish(error)}
    }
}
'''.replace('PANEL_URL',panel.as_uri())
smoke=output/'installed-smoke.qml';smoke.write_text(source,encoding='utf-8')
env=dict(os.environ,QT_QPA_PLATFORM='offscreen',QT_QUICK_BACKEND='software',QML_DISABLE_DISK_CACHE='1')
command=[str(app),'-s','-m','-c',str(settings),'-p',str(smoke),str(fixture)]
run=subprocess.run(command,env=env,cwd=output,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=35)
(output/'installed-smoke.log').write_bytes(run.stdout)
report=output/'installed-arrangement.json'
result=json.loads(report.read_text(encoding='utf-8-sig')) if report.exists() else {'failures':['no result'],'logTail':run.stdout[-3000:].decode('utf-8',errors='replace')}
result.update(exit=run.returncode,sha256=hashlib.sha256(app.read_bytes()).hexdigest())
(output/'installed-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=True))
sys.exit(bool(result['failures']) or run.returncode!=0)
