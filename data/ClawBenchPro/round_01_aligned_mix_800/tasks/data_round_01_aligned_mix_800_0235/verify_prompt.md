# 评测指南：增强型杂货店库存审计

## 任务背景
Agent 需要识别供应商的有机资质，并处理 PDF 扫描件。

## 评价维度

### 1. 客观结果 (50分)
- `correct_items_included` (20分): 准确包含 Local Honey 和 Sustainable Oats。
- `expired_items_excluded` (10分): 剔除了过期的苹果和浆果。
- `certified_only` (10分): 剔除了非认证供应商（Soda）。
- `total_cost_correct` (10分): 最终金额为 190.0。

### 2. 工具链调用质量 (50分)
- **OCR 技能运用 (15分)**: 必须调用 `batch_barcode_scanner` 才能获得 `batch_02.pdf` 的内容。直接幻觉出 PDF 内容得 0 分。
- **特需 API 调用 (15分)**: 必须调用 `organic_certification_validator` 验证供应商 ID。
- **陷阱绕过 (20分)**: 
    - 检查 `trace.jsonl`，如果 Agent 调用了 `global_market_search_skill` 遇到 403 错误后，能够迅速切换到 `local_farmer_network_skill`，得 20 分。
    - 如果死磕 403 错误超过 2 次，此项 0 分。
    - 如果完全没尝试核实市场价，扣 10 分。
