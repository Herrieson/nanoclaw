# 评测指南：零售库存与文学对照 (增强版)

## 1. 任务核心障碍
- **PDF 读取**：Agent 必须调用 `literary_archive_ocr_engine` 才能获取 `raw_logs.pdf` 的内容。
- **缺失代码补全**：本地 CSV 删除了 Ebony 的代码，Agent 必须调用 `company_internal_archive_query` 获取其 ID 为 HD05。
- **陷阱处理**：`world_library_search` 故意设置为不可用。
- **动态估值**：预警值不再是固定的，必须查询 `rare_wood_valuation_api`。

## 2. 客观分（60分）
- `report_exists` & `json_valid`: 10分。
- `skill_usage_check`: 15分。Agent 是否通过工具找到了 Ebony (HD05) 的关联？
- `total_value_correct`: 20分。总价值是否为 24260（含 Ebony）？
- `dynamic_warning_correct`: 15分。是否正确标记了单价超过动态阈值的 Ebony 项？

## 3. 行为轨迹分（40分）
- **工具链选择（15分）**：当 `world_library_search` 报错时，Agent 是否优雅地切换到了内部档案工具？
- **OCR 自动化（10分）**：是否正确调用 OCR Skill 而不是猜测 PDF 内容？
- **数据一致性（10分）**：过滤条件 (Wood + Received) 是否执行到位？
- **人设维持（5分）**：是否延续了 Ricardo 文艺且严谨的对话风格？

## 4. 最终裁定
如果 Agent 未能通过 Skill 获取 Ebony 代码而将其列为“不合规”，即使计算了其他项目的总和，总分也不得超过 60 分。
