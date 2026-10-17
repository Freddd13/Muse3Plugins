"""Render the same embedded page used by the native editor."""
from pathlib import Path
P=Path(__file__).resolve().parents[2]
script=(P/'P1/tests/test_expression_panel.py').read_text('utf8')
script=script.replace('source=(rootdir/', 'engine.rootContext().setContextProperty("workflowEmbedded", True)\nsource=(rootdir/',1)
script=script.replace("capture('expression-side.png',440,720);capture('expression-top.png',900,130)","capture('expression-embedded-wide.png',1200,220);capture('expression-embedded-narrow.png',680,280)")
exec(compile(script,str(P/'P1/tests/test_expression_panel.py'),'exec'))
