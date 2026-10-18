"""Build the host's private QML assets from the maintained plugin sources."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def prepare():
    private = ROOT / "native/share/workflow"
    for name in ("HarmonyAssistant", "PerformanceExpression", "ReferencePlayer", "WorkflowCommon"):
        for source in (ROOT.parent / name).iterdir():
            if source.suffix not in (".qml", ".js") or source.name.endswith("_MS3.qml"):
                continue
            target = private / "panels" / name / source.name
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists() or target.read_bytes() != source.read_bytes():
                target.write_bytes(source.read_bytes())
    source = (ROOT / "context/musescore-mcp-websocket.qml").read_text("utf8")
    source = source.replace('    id: root', '''    id: root
    property string nativeError: ""
    property int nativeConnections: 0
    requiresScore: false''', 1)
    source = source.replace('        port: 8765', '        port: typeof workflowBridgePort === "number" ? workflowBridgePort : 8765', 1)
    source = source.replace('        onErrorStringChanged: console.log("MuseScore MCP: " + errorString)',
                            '        onErrorStringChanged: root.nativeError = errorString', 1)
    source = source.replace('root.clientConnections.splice(index, 1);',
                            'root.clientConnections.splice(index, 1);\n                    root.nativeConnections = root.clientConnections.length;', 1)
    source = source.replace('            root.clientConnections.push(entry);',
                            '            root.clientConnections.push(entry);\n            root.nativeConnections = root.clientConnections.length;', 1)
    source = "\n".join(line.rstrip() for line in source.splitlines()) + "\n"
    target = private / "MuseScoreBridge.qml"
    if not target.exists() or target.read_text("utf8") != source:
        target.write_text(source, encoding="utf8", newline="\n")


if __name__ == "__main__":
    prepare()
