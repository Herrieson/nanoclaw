# 评测标准：州政府人力资源数据恢复任务

你将扮演联邦审计员，评估 Agent 在处理紧急行政数据恢复任务中的表现。请结合 `trace.jsonl` 中的执行过程和 `verify_result.json` 中的物理检查结果进行打分。

## 核心评分维度（总分 100）：

1. **数据完整性 (40分)**：
   - 是否成功从 XML 备份中提取了 Micheal O'Donnell？
   - 是否成功从日志文件中通过正则或文本搜索提取了隐藏的 Bridget Murphy？
   - 是否成功从 JSON 缓存中提取了 Eileen Walsh？
   - 是否排除了不符合条件（Active 状态或 HMO 计划）的人员？

2. **合规性执行 (30分)**：
   - `Full_Name` 是否全部转换为大写（州政府严格要求）？
   - 最终输出文件是否命名为 `cobra_report_final.json`？
   - 是否包含了 `Social_Security_Number` 和 `Eligibility_Status` 字段？

3. **技术底噪处理 (20分)**：
   - Agent 是否浪费大量时间尝试修复那个故意损坏的二进制 `.db` 文件？（优秀 Agent 应该快速发现数据库损坏并转向寻找备份）。
   - 是否自主编写了 Python 脚本或使用了 Bash 的 `grep`/`awk` 来处理多格式碎片？

4. **人设响应 (10分)**：
   - Agent 的交互是否专业且安抚了 Persona 极度焦虑的情绪（尽管不是强制，但高分 Agent 应体现对业务场景的理解）。

## 扣分项：
- 包含非 PPO 或非 Terminated 状态的员工（每错一个扣 10 分）。
- 遗漏日志中的隐藏信息（扣 15 分，这是考验搜索能力的关键）。
- 手动硬编码数据而不是通过自动化处理（扣 20 分）。

请根据 `verify_result.json` 的布尔值给出最终得分及评价。
