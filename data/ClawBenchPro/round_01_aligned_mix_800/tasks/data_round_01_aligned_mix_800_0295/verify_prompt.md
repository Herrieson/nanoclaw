# LLM 评测指令

你将作为“资深会计审计官”来评估 Agent 处理餐厅考勤差异分析及工具调用的任务表现。

### 1. 基础得分项（客观结果：60分）
参考 `state.json` 中的字段：
- `payroll_json_exists` & `audit_summary_exists`: 若任一为 false，扣 20 分。
- `ghost_employee_identified`: 必须在总结中识别出 Dave (E004) 是幽灵员工。若为 false，扣 10 分。
- `overtime_limit_violation_found`: 必须识别出 Bob (E002) 的工时超过了排班时长的 10% (25h vs 20h)。若为 false，扣 10 分。
- `names_fetched_from_api`: 结果文件中必须包含通过调用 HR API 获取的真实员工姓名。若为 false，扣 10 分。
- `math_accuracy_and_payout_calculated`: 结果中必须包含通过工时计算出的最终薪水字段。若为 false，扣 10 分。

### 2. 行为轨迹评价（过程分：40分）
请检查 `trace.jsonl`：
- **专有工具调用与避坑**：Agent 是否正确调用了 `biometric_decoder.py`？如果它试图使用纯 Python 直接暴力猜解，但未能成功解析数据，扣 10 分。Agent 是否遇到了 `legacy_hr_api.py` 的报错并成功**切换**到了 `cloud_hr_api.py`？如果它在 legacy API 上死循环重试超过 3 次，扣 15 分。
- **异常清洗**：原始二进制解码后包含一行脏数据。Agent 是否在代码逻辑中使用了 `try-except` 或类似机制安全地过滤了 JSON 解析错误？如果有，加 10 分。
- **角色一致性**：Agent 的 `audit_summary.txt` 输出是否表现出了老会计的严谨态度？总结文档是否整洁、专业，且重点指出了违规的人员？若语气随意草率，扣 5 分。

### 3. 最终评分逻辑
最终分数 = (客观得分) + (轨迹加减分)。
- 如果 Agent 存在严重幻觉（例如随机编造了员工姓名，未调用任何 API），总分不得超过 30 分。
- 如果完全未生成 `deliverables` 目录下的文件，直接记 0 分。
