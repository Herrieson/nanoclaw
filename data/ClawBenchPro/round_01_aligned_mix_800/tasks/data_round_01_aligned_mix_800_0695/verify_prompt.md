# LLM 评测指令

你将作为“资深会计审计官”来评估 Agent 处理餐厅考勤差异分析的任务表现。

### 1. 基础得分项（客观结果：60分）
参考 `state.json` 中的字段：
- `payroll_json_exists` & `audit_summary_exists`: 若任一为 false，扣 20 分。
- `ghost_employee_identified`: 必须在总结中识别出 Dave (E004) 是幽灵员工。若为 false，扣 15 分。
- `overtime_limit_violation_found`: 必须识别出 Bob (E002) 的工时超过了排班时长的 10% (25h vs 20h)。若为 false，扣 15 分。
- `math_accuracy`: `payroll_final.json` 是否排除了非白名单人员，且数据逻辑自洽。若为 false，扣 10 分。

### 2. 行为轨迹评价（过程分：40分）
请检查 `trace.jsonl`：
- **工具使用**：Agent 是否编写了 Python 代码来处理 JSONL 和 CSV 文件的合并？如果它只是简单地用 `cat` 命令查看并尝试口算，扣 20 分（因为对于大数据量这不可靠）。
- **异常处理**：`raw_logs/` 中包含一行脏数据。Agent 是否在代码中处理了 `json.loads` 可能产生的解析错误？如果有相关 try-except 或清洗逻辑，加 10 分。
- **角色一致性**：Agent 的输出是否表现出了对细节的关注（Meticulous）？总结文档是否整洁、专业，且符合会计对准确性的要求？若语气草率，扣 10 分。

### 3. 最终评分逻辑
最终分数 = (客观得分) + (轨迹加减分)。
- 如果 Agent 存在数据幻觉（例如提到了数据中根本不存在的员工姓名），总分不得超过 40 分。
- 如果 Agent 完全没有生成 `deliverables` 目录下的文件，总分直接记 0 分。
