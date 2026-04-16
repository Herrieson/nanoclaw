# Verification for data_218

请根据所提供的 `trace.jsonl`（Agent 运行轨迹）和 `verify_result.json`（规则验证输出）对 Agent 的表现进行客观打分。

## 任务背景
Agent 需要模拟帮助一位极度内向的护理机构前台，从混乱的系统导出文件（日志文件 `signups.log` 和 SQLite 数据库 `clinic.db`）中筛选出参加“春季观鸟”活动的合格名单，生成 `approved_roster.csv`，并根据健康状态按需分配有限的空闲护工。

## 评分维度 (总分: 100)
1. **文件与格式 (30分)**: 
   - `approved_roster.csv` 是否成功创建？(10分)
   - CSV列名是否严格为 `Resident Name`, `Status`, `Assigned Staff`？(20分)
2. **数据解析与过滤 (25分)**: 
   - 是否准确从日志提取了报名者 (Alice, Bob, Charlie, Diana, Edward, Fiona, George)？
   - 是否正确查询了数据库并过滤掉了 `Restricted` 的 Bob 以及因护工不足无法成行的 George？
3. **资源分配逻辑 (25分)**:
   - 是否精准识别 `Needs Escort` 并在可用的护工池(`Nurse_Sarah`, `Orderly_Mike`, `Orderly_Anna`)中为相关人员做了唯一分配？
   - `OK` 状态的居民护工列是否保持为空？
4. **排序 (20分)**:
   - 最终输出的表格行是否按照长者姓名的字母升序排列？

## 评分参考
请查阅 `verify_result.json` 中的 `score` 与 `details` 字段。
- 如果 `score` 为 100，且 trace 中显示 Agent 是通过正当代码逻辑获取的，给予满分。
- 如果因为护工分配逻辑错误或居民缺失扣分，请在评语中详细说明。
- 输出格式请包含一段分析，最后在单独行输出：`FINAL SCORE: [你的分数]`。
