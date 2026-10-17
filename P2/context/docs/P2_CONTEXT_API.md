# P2 当前谱与局部编配接口

软件个人版 0.60.0；QML 桥 2.2.0。

用户操作见 MuseScore 仓库 `personal/docs/P2_CONTEXT_060_GUIDE.md`。这里说明服务分工和数据，便于维护与接入。

## 操作顺序

`read_arrangement_context` 读取当前内存谱。传入选区或小节范围及 `taskBrief`，取得 `contextId` 和 `snapshotId`。同一份乐谱版本可以对应几个不同任务；每份任务保留自己的范围和要求。

`submit_arrangement_options(context_id, options, task_brief)` 接收一至三版写法。软件在副本中检查，结果进入“视图 → 编配建议”。`arrangement_option` 提供差异、MIDI 事件、试听、采用、保存另一种写法和停止。

采用使用一次原生撤销，记录随 MSCZ 保存。预览、读取和准备副本保留源谱。用户明确要求直接采用时，可在指定范围完成采用和读回核对。

## 三个位置分别负责什么

| 位置 | 职责 |
|---|---|
| MuseScore | 内存谱、准确选区、逐声部读取、对象引用、排版、播放、保存和撤销 |
| `src/context/service.py` | 分页读取、独立任务、资料整理、不可变任务结果和操作查询 |
| `src/tools/arrangement.py` | MCP 工具参数与返回，供 Codex 使用 |

服务处理 JSON 值。音乐计算可以单独替换，Codex 负责本轮交流和候选生成。

## 读取

请求示例：

```json
{
  "scope": {"start": 0, "end": 1920, "firstTrack": 0, "endTrack": 8},
  "fields": ["geometry"],
  "taskBrief": {"goal": "左手更疏", "preserveTracks": [0], "preserveHarmony": true}
}
```

省略范围时使用当前选择；`whole: true` 读取全谱，`firstMeasure/lastMeasure` 使用从1开始的小节序号。原生接口每页至多64个谱段，服务按实际用时调整页大小，以约2 ms为目标。首批演奏数值准备、反复及边界资料的时间也计入返回值。

音符保留原生 tick、以四分音符为单位的精确分数、记谱／发声音高、TPC1／TPC2、声部、延音、指法、分手和力度。`quarterTime`、`quarterDuration` 使用 `{numerator, denominator}`，保留七连音等时值；整数 tick 继续用于现有接口。

`snapshotId` 绑定这次乐谱版本。音符引用形如 `{snapshotId, id}`；相同实音在不同声部中各有记录。装饰音另带 `graceIndex`。演奏秒数、原生 tick 和展开后的出现位置分别返回。几何按 `fields` 请求读取。

块级资料包括 `notes/rests/meters/harmonies/hands/pedals/parts/tempos/boundaryRelations/occurrences`。原曲信息、人工和弦及新鲜度随任务提供；已发布的和弦分析由和弦助手、检查和 AI 共用。

较长任务可用 `start_arrangement_read`、`arrangement_task`、`get_arrangement_context`。完成时返回 `contextId`；取消后结束任务。服务保留至多4份、合计32 MiB的任务资料；单份8 MiB。更大的乐谱通过 `get_arrangement_state/get_arrangement_page` 逐页读取。

现有 `get_score_data` 在新宿主上使用分页，并保留原来的 measures/staff 返回形式；该查询使用临时结果，保留编配任务。旧桥继续使用原读谱入口。

## 保存资料

`save_arrangement_information(snapshot_id, information)` 接收 `assertions/materials/alignments/analysisRuns` 条目。每条有 `id`、来源 `origin` 或 `provenance`，以及相应的范围和状态。同编号补充字段，新编号追加。采用记录由宿主生成。

解释与材料是任务资料。文本文字和链接按内容读取，操作范围来自用户要求及工具参数。

## 局部写法

每项提供 `title/summary/scope`，以及下面两种修改：

- `changes`：已有音符的 `ref`，及新 `pitch/tpc1/tpc2/velocity/finger/hand/handEnd`。
- `voices`：完整声部的 `track/events/tuplets`。事件按时间排列，空 `pitches` 表示休止。

示例：

```json
{
  "title": "左手拆开",
  "summary": "第一拍先弹低音和五度，第二拍接内声。",
  "voices": [{
    "track": 4,
    "events": [
      {"quarterDuration": {"numerator": 1, "denominator": 1},
       "pitches": [{"pitch": 36, "tpc1": 14, "tpc2": 14}]},
      {"quarterDuration": {"numerator": 3, "denominator": 1}, "pitches": []}
    ]
  }]
}
```

和弦中的音可分别提供 `velocity: 1..127`。连音组示例：

```json
{"quarterTime": {"numerator": 0, "denominator": 1},
 "quarterDuration": {"numerator": 1, "denominator": 1},
 "actual": 3, "normal": 2}
```

对应三个事件各占 `1/3` 个四分音符。宿主使用原生音符、休止、延音和连音组命令。

`taskBrief.preserveTracks/preserveNotes` 保留指定对象；默认旋律为track 0。`allowMelodyChanges` 和 `preserveHarmony` 表达本次要求。默认支持现有和弦音的重排、加倍和节奏变化。新范围限制在读取任务以内。

整段写法检查边界连线、拍数和谱表，再在副本生成。跨段连接沿用分段试写的连接资料。采用后读回比较音符、时值、拼写、力度与连线，结果一致后结束这次撤销操作。

`arrangement_option` 的 action：

| action | 结果 |
|---|---|
| preview | 原谱差异叠加及变化位置 |
| performance | 本段原／新 MIDI 起音事件，含原生和展开 tick、声部、音高与力度 |
| original / audition | 同一范围试听谱中／新写法 |
| apply | 采用，一次撤销 |
| variant | 存为分段写法，一次撤销 |
| stop | 停止比较并收起叠加 |

## 连接与退出

写入有 `operationId`。响应丢失时，使用 `arrangement_operation_result` 查询结果。相同编号及内容返回已有结果；新的操作使用新编号。

Windows安装包含匹配的 `Qt5WebSockets.dll`。桥创建时登记应用关闭清理，在Qt和OpenSSL都有效时释放SSL／DTLS默认配置；运行期间沿用现有连接设置。QML对象结束时解除该桥的回调和连接。

完整操作检查由插件仓库 `P2/test_context_host.py` 启动独立宿主，连接真实QML桥及MCP工具，核对采用、撤销、活动连接重载和正常退出。其它平台的部署情况另行记录。
