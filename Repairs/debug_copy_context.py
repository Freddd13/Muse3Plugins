from pathlib import Path
ROOT=Path(__file__).resolve().parent
HOST=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
source=HOST/'mscore/workflow/workflowvariants.cpp'
text=source.read_text(encoding='utf8')
text=text.replace('#include <QBuffer>','#include <QBuffer>\n#include <QFile>\n#include <QDir>')
needle=' return {{"context",from==0?'
assert text.count(needle)==1
text=text.replace(needle,' if(from==0&&!qEnvironmentVariable("HARMONY_TEST_ARTIFACTS").isEmpty()){QFile file(QDir(qEnvironmentVariable("HARMONY_TEST_ARTIFACTS")).filePath("raw-context-"+QString::fromLatin1(QCryptographicHash::hash(context,QCryptographicHash::Sha256).toHex())+".xml"));if(file.open(QIODevice::WriteOnly))file.write(context);}\n'+needle)
target=ROOT/'native/mscore/workflow/workflowvariants.cpp';target.write_bytes(text.encode('utf8'))
test=ROOT/'native/mtest/mscore/p1native/tst_p1native.cpp'
text=test.read_text(encoding='utf8').replace('  const auto beforeContext=contextBytes(s);','  const QByteArray beforeContext;')
test.write_bytes(text.encode('utf8'))
