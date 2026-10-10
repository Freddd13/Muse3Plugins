from apply_native import replace, HOST
def apply():
    if '_analysisState;' not in (HOST/'mscore/plugin/api/scoreobserver.h').read_text(encoding='utf-8'):
        replace('mscore/plugin/api/scoreobserver.h', '      QPointer<Ms::Score> _score;', '''      ScoreContentState _analysisState;
      quint64 _analysisRevision = 0;
      quint64 _analysisSession = 0;
      QPointer<Ms::Score> _score;''')
    replace('mscore/plugin/api/scoreobserver.h', '      Q_INVOKABLE QVariantMap snapshot(', '''      Q_INVOKABLE QString analysisRevision();
      Q_INVOKABLE QVariantMap analysisScope(bool whole = false) const;
      Q_INVOKABLE QVariantMap analysisRange(int start, int end, int firstTrack, int endTrack, int fromTick, int limit, const QString& expected = QString());
      Q_INVOKABLE QVariantMap snapshot(''')
    replace('mscore/plugin/api/scoreobserver.cpp', '      _score = score;\n      _index.clear();', '      _score = score;\n      ++_analysisSession;\n      _index.clear();')
    replace('mscore/plugin/plugin.cmake', '    ${CMAKE_CURRENT_LIST_DIR}/api/scoreobserver.cpp', '    ${CMAKE_CURRENT_LIST_DIR}/api/arrangementsnapshot.cpp\n    ${CMAKE_CURRENT_LIST_DIR}/api/scoreobserver.cpp')
    replace('mscore/plugin/plugin.cmake', '    ${CMAKE_CURRENT_LIST_DIR}/api/arrangementsnapshot.cpp', '    ${CMAKE_CURRENT_LIST_DIR}/api/readonlyanalysisjob.h\n    ${CMAKE_CURRENT_LIST_DIR}/api/readonlyanalysisjob.cpp\n    ${CMAKE_CURRENT_LIST_DIR}/api/arrangementsnapshot.cpp')
    if '_readOnlyJobToken =' not in (HOST/'mscore/plugin/api/scoreobserver.h').read_text(encoding='utf-8'):
        replace('mscore/plugin/api/scoreobserver.h', '      QPointer<Ms::Score> _score;', '      QObject* _readOnlyJob = nullptr;\n      int _readOnlyJobToken = 0;\n      QPointer<Ms::Score> _score;')
    replace('mscore/plugin/api/scoreobserver.h', '      Q_INVOKABLE QString analysisRevision();', '      Q_INVOKABLE int startReadOnlyJob(const QString& source, const QVariantMap& input);\n      Q_INVOKABLE void cancelReadOnlyJob();\n      Q_INVOKABLE QString analysisRevision();')
    replace('mscore/plugin/api/scoreobserver.h', '   signals:\n      void scoreChanged();', '   signals:\n      void readOnlyJobFinished(int token, const QVariantMap& result);\n      void scoreChanged();')
    replace('mscore/plugin/api/scoreobserver.cpp', 'ScoreObserver::~ScoreObserver() { clearAllPreviews(); }', 'ScoreObserver::~ScoreObserver() { cancelReadOnlyJob(); clearAllPreviews(); }')
    replace('mtest/CMakeLists.txt', '        mscore/pluginhost', '        mscore/p0native\n        mscore/pluginhost')
if __name__ == '__main__':
    apply()
