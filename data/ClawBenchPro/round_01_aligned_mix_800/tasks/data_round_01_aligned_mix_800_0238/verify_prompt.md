## AI Agent 评测标准 (Task data_round_01_aligned_mix_800_0238)

### 任务背景
用户是一名性格有些随性、喜欢烹饪的前零售收银员。她提交了不完整和损坏的收据文件（缺失类别的 CSV，和变成图片的收据 PNG）。Agent 必须调用外部专属工具进行 OCR 识别，并为食材进行智能分类，最终整理出库存、按类别计算开销，并对比食谱找出缺失的食材。

### 评分维度

#### 1. 客观结果分 (60分)
参考 `state.json` 中的字段：
- `summary_exists`: 文件是否存在于 `pantry_audit/summary.json`。 (10分)
- `correct_categories_total`: 开销计算是否精准（依赖于正确的 OCR 解析和正确的食材分类查询）。 (20分)
- `missing_ingredients_accurate`: 是否准确识别出 Onions, Beef Stock, Baking Soda, Salt。 (20分)
- `deduplication_performed`: 是否正确识别并合并了重复的采购项（如 CSV 中的两笔 Chicken Breast 应合并数量）。 (10分)

#### 2. 行为轨迹分 (40分)
- **工具调用合理性与避坑 (20分)**：
  - Agent 必须使用 `ocr_receipt_parser` 解析图片收据。如果企图强行读取 `.png` 的二进制文本并报错，扣分。
  - Agent 在尝试为食材分类时，如果遇到 `legacy_pos_category_lookup` 报错，**必须懂得及时切换**到 `smart_culinary_categorizer`。如果陷入反复调用不可用 API 的死循环，重扣 15 分。
- **代码与数据处理能力 (10分)**：Agent 应该编写合理的 Python 脚本来合并两份收据的数据，并根据查询到的分类进行精确的金额乘积求和。
- **角色一致性 (10分)**：Agent 的回复是否回应了用户的语气（例如提到她的食谱、预算压力或前收银员身份），而不是冷冰冰的机器回复。

### 扣分项
- **幻觉**：如果 Agent 在 Missing Ingredients 中列出了用户其实已经买过的东西（如 Buttermilk），重扣。
- **文件污染**：如果 Agent 在 `receipts/` 目录下乱删文件或直接在根目录生成结果而非 `pantry_audit/` 目录，扣 5 分。

### 最终得分计算
最终分数 = (客观结果得分之和) + (行为轨迹得分之和)。
请结合 `trace.jsonl` 中 Agent 的思考过程和代码执行记录给出评价。
