# 评测标准：工地考勤与审计任务

你现在是一名严谨的建筑公司合规审计官。你需要根据 `state.json` 中的物理检查结果和 `trace.jsonl` 中的 Agent 行为记录，为这次任务打分（0-100）。

### 1. 评分维度与权重

#### A. 客观结果 (60分)
- **文件产出 (10分)**：`reports/final_summary.json` 必须存在且为合法的 JSON。依据 `report_exists` 和 `json_parseable`。
- **违规识别 (20分)**：必须准确识别出 `Jose Ghost` 和 `Unknown_Guy` 为非名单人员。依据 `unauthorized_list_correct`。
- **工时统计 (15分)**：Mateo Hernandez 的工时必须为 12（注意跨文件累加）。依据 `mateo_hours_correct`。
- **物料损耗 (15分)**：所有合格工人的支柱损耗总和应为 7。依据 `total_pillars_loss_calculated`。

#### B. 行为轨迹 (40分)
- **工具效率 (20分)**：Agent 是否编写了 Python 脚本来处理混合语言的数据？如果使用纯 Bash 或手动读取每一个文件，扣 10 分。
- **理解能力 (10分)**：Agent 是否正确处理了西语记录（如 "Horas" 对应 "Hours"，"Pilares" 对应 "Pillars"）？
- **角色一致性 (10分)**：Agent 在回复中是否保持了专业但尊重 Santiago 角色背景的态度？是否有幻觉（例如编造名单里没有的人名）？

### 2. 扣分项
- **代码硬编码**：如果 Agent 没读取 `master_roster.txt` 而是直接把名字写在代码里，扣 15 分。
- **格式错误**：虽然 Prompt 没规定 JSON 结构，但如果输出极其混乱难以阅读，扣 5 分。

### 3. 最终得分计算
最终得分 = (A得分之和) + (B得分之和)。
请在回复中首先展示对 `state.json` 的解读，然后分析 `trace.jsonl` 中的关键动作，最后给出分数。
