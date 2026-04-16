你是评测裁判。请根据 Agent 的执行轨迹 `trace.jsonl` 和自动验证脚本输出的 `verify_result.json`，对 Agent 解决“超市库存数据清洗与逻辑筛选”任务的表现进行打分。

## 验证指标定义
1. **JSON 产出与合法性 (20分)**
   - `priority_stock.json` 是否生成并具备合法的 JSON 结构？(对应 `json_exists` 和 `json_valid_format`)
2. **逻辑推理与筛选准确性 (40分)**
   - Agent 是否正确解析了 CSV 中内嵌的 JSON 字符串？
   - 是否准确识别了满足以下任一条件的健康商品：糖<5g、有机、蛋白质>15g？
   - 是否准确移除了所有配料表含有 "Artificial Colors" 的商品？（正确结果应为包含 `ITM001`, `ITM002`, `ITM006`, `ITM007` 4项）（对应 `correct_priority_items`）
3. **数据排序 (20分)**
   - 是否按蛋白质含量从高到低对筛选结果进行了正确排序？(对应 `correct_sorting`)
4. **团队简报产出 (20分)**
   - `shift_note.txt` 是否生成，且清晰地写明了 Priority 物品数量（4）与 Junk 物品数量（4）？(对应 `txt_exists` 和 `correct_counts_in_txt` 且阅读信件内容确认语义明确)

## 评分规则
- 若 `correct_priority_items` 为 false，说明基础逻辑判断错误，扣除第2项和第3项的分数。
- 结合人工审查 `shift_note.txt` 内容，如果数字 "4" 出现但含义混淆（例如写成4个健康，0个垃圾），酌情扣除第4项分数。
- 总分满分 100。

请输出详细的扣分原因，并在最后一行严格以 `FINAL_SCORE: <分数>` 结尾。
