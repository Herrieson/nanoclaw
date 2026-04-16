请根据以下标准为 Agent 的表现打分（总分 100 分）：

1. **报告文件生成 (20分)**：Agent 是否成功在指定目录创建了 `consolidated_report.json` 并保证其格式合法 (`report_exists` 和 `is_valid_json` 为 true)。
2. **异常数据过滤 (20分)**：Agent 是否排除了数据库中不存在的邮编数据（`TRK9999`），`filtered_invalid` 必须为 true。
3. **数据计算准确性 (20分)**：Agent 是否正确关联了 SQLite 数据库并准确计算出了总收入（71.4），`total_revenue_correct` 必须为 true。
4. **数据排序规则 (20分)**：Agent 是否严格遵循指令要求，将配送记录按照 `tracking_number` 的字母顺序进行了升序排列，`sorted_correctly` 必须为 true。
5. **字段结构严谨度 (20分)**：Agent 提取和生成的 JSON 数据结构是否完整包含所需字段 (`keys_correct` 为 true)。

请参考 `verify_result.json` 中的客观布尔值以及 Agent 运行轨迹 (`trace.jsonl`)，给出你的详细评分理由与最终分数。
