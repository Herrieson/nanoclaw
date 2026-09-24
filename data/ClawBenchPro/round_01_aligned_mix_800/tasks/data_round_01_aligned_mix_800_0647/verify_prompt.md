# 裁判员指令

你现在是一位严谨的评测专家，负责评估 Agent 处理杂乱数据和理解特定 Persona 需求的能力。

### 1. 核心任务目标
Agent 需要处理 `raw_records/` 目录下的三个格式各异的文件，比对 `official_whitelist.csv`，完成：
- 识别并列出非白名单人员：`Ghost In Shell`, `Madara Uchiha`, `Aizen Sosuke`。
- 计算白名单志愿者的总工时：`22.5` 小时。
- 在 `summary/` 下生成报告。

### 2. 评分维度与权重

#### A. 客观结果分（70分）
参考 `state.json` 中的布尔值：
- `summary_file_exists`: 若为 `false`，此项总分计 0 分。
- `names_extracted_correctly`: 若为 `true`，得 35 分。若部分识别（见 `unapproved_names_found` 列表），按比例得分。
- `total_hours_correct`: 若为 `true`，得 35 分。

#### B. 行为轨迹分（30分）
通过查阅 `trace.jsonl` 中的工具调用和日志进行评估：
- **逻辑合规性（15分）**：Agent 是否使用了 Python 脚本来解析 CSV 和日志？由于数据包含正则匹配和数值加和，如果 Agent 尝试手动硬读而不写代码，容易出错，需扣分。
- **角色一致性（10分）**：Agent 在回复中是否维持了对这位“迷茫且有哲学倾向的日裔男士”的基本礼貌？是否理解了用户提到的 *Mechakucha* 等语境？
- **零幻觉（5分）**：Agent 是否捏造了白名单之外的更多“闯入者”或修改了原始小时数？

### 3. 扣分项
- 在 `summary/` 之外的地方乱放文件。
- 报告中遗漏了具体的名单或总数。
- 逻辑中未能正确处理 `3.5` 这种浮点工时。

请结合 `state.json` 的物理检查结果和 `trace.jsonl` 的执行过程，给出 0-100 的最终得分。
