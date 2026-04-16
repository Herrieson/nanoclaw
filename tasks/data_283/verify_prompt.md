# 零售库存逻辑修复任务 - 评测标准

你现在是高级技术审计员，负责评估 Agent 处理 Brenda 提交的库存危机的表现。
请结合 `trace.jsonl`（记录了 Agent 的操作步骤）和 `verify_result.json`（物理状态检测结果）进行打分。

### 评分维度：
1. **原因分析 (20分)**：
   - Agent 是否查看了 `system.log` 并正确识别出 `auto_reorder.py` 中的错误 SQL 逻辑是导致 Premium 商品库存清零的原因？
2. **脚本修复 (30分)**：
   - `verify_result.json` 中的 `script_fixed` 必须为 true。
   - Agent 是否删除了有害的 `UPDATE` 语句，或者将其逻辑修正为合理的补货逻辑？
3. **数据一致性 (40分)**：
   - `verify_result.json` 中的 `data_accuracy` 分数。按比例给分（100% 正确得 40 分）。
   - Agent 必须按照 CSV 里的 `actual_quantity` 修正了数据库。
4. **沟通与专业性 (10分)**：
   - Agent 的回复是否符合 Brenda 的期望（直接、高效、不啰嗦）？
   - 是否在操作完成后给出了清晰的简报？

### 注意事项：
- 如果 Agent 仅仅修改了数据库而没有修复脚本，脚本在下次运行时会再次破坏数据，这属于“治标不治本”，脚本修复分项应得 0 分。
- 如果 Agent 能够编写一个通用的 Python 脚本来同步 CSV 到 DB，属于加分表现。

请输出最终得分和简短的评价。
