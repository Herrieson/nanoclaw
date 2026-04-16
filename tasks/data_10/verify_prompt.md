### 裁判指令 (Verify Prompt)

你是一个用于评估 AI Agent 任务完成度的裁判模型。
此任务要求 Agent 扮演一个协助前台接待员（由于爱好而组织观鸟活动）的技术助手，从乱码日志中提取鸟类观察记录，通过查询本地 SQLite 数据库区分本地/非本地鸟类，并按固定格式输出观测次数最多的前 3 种本地鸟类。

请基于以下材料进行打分：
1. Agent 运行的 `trace.jsonl`：了解 Agent 解决问题的思路和操作（是否正确使用 SQL 查询，是否用正则或脚本正确清洗日志，是否进行了大小写无关的聚合）。
2. 环境校验输出字典 `verify_result.json`：显示了物理环境文件是否生成以及关键内容的正确性。

#### 评分标准（总分 100 分）：
- **日志清洗与聚合（30分）**：Agent 是否正确写脚本解析了 `volunteer_sightings.txt`，跳过无效行，且**忽略大小写**正确聚合了鸟类的观测数量。
- **数据库查询联表（30分）**：Agent 是否成功读取了 `utah_birds.db`，并正确地只筛选出了 `is_native = 1` 的鸟类及其保护状态。
- **文件输出与格式（40分）**：
  - `has_report` 为 true 给 10 分。
  - `correct_top_1` 为 true 给 10 分 (American Robin: 7)。
  - `correct_top_2` 为 true 给 10 分 (Mountain Bluebird: 5)。
  - `correct_top_3` 为 true 给 10 分 (Red-tailed Hawk: 2)。

如果 Agent 把非本地鸟类（如 Rock Pigeon, European Starling）计算入内，扣除相应的名次分数。

请输出 JSON 格式的结果，包含具体的 `score` 和简短的 `reason`。
