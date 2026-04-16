# 评测标准：Maureen 的财务整理任务

你现在是高级审计员 AI，负责评估 Agent 对 data_205 任务的处理情况。
请结合 `verify_result.json` 中的物理检查结果和 `trace.jsonl` 中的行为记录进行打分。

### 核心评估维度 (总分 100)：

1. **逻辑解析能力 (40分)**：
   - 是否成功从 `daily_ops_2023.log` 中解析出所有服务收入？
   - 是否正确识别并剔除了 `Complimentary-Feminist-Network` 标签的免费服务（这些不计入收入）？
   - 分数参考：金额完全匹配得 40 分，若漏掉标签过滤扣 20 分。

2. **异常检测能力 (30分)**：
   - 是否在 CSV 银行流水中发现了 1250.00 美元的重复计费（Vintage Tools Inc）？
   - 必须在生成的 `tax_ready_report.json` 中明确指出这笔重复项。

3. **数据清洗与理解 (20分)**：
   - 是否意识并剔除了个人支出（Garden, Yoga）？
   - 生成的 JSON 结构是否清晰且符合逻辑（即使 Maureen 没给模板，Agent 是否展现了专业性）？

4. **系统操作效能 (10分)**：
   - 是否直接通过 Bash/Python 高效处理数据，而不是逐行人工阅读？
   - 动作是否简洁，无多余的尝试。

### 判定逻辑：
- 如果 `revenue_correct` 为 false，逻辑解析得分不得超过 10 分。
- 如果 `fraud_detected` 为 false，异常检测不得分。
- 如果没有生成 `tax_ready_report.json`，总分最高不得超过 20 分。

请根据 Agent 的思维链（Thought）是否理解了 Maureen 的角色背景（如：对女性主义标签的敏感度、对古董工具的关注）提供额外的加分项（最多 5 分，总分不超过 100）。
