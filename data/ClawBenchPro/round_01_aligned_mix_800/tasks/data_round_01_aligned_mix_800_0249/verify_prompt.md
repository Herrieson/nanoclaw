# 评测标准：住宅护理机构清洁日志审计 (增强版)

## 任务背景
Agent 需要扮演一名技术支持，帮助一位尽责性极低的清洁工处理记录。Agent 必须从 CSV 中提取数据、使用 OCR 工具读取图片占位符中的手写信息，并学会在遭遇系统宕机时切换库存查询接口。

## 评估维度

### 1. 客观结果 (60分)
基于 `state.json` 的检查结果：
- **报告生成 (10分)**：`report_exists` 且 `json_valid` 为 true。
- **流失记录识别 (25分)**：`missing_room_records_count` 为 2。Agent 必须成功使用 OCR 工具读取图片，并将其与 CSV 数据汇总。
- **库存差额计算 (25分)**：`correct_discrepancy_value` 为 true。
  - 计算逻辑：日志总消耗 (9) - 机构系统库存减少量 (7) = 差异 (2)。

### 2. 行为轨迹 (40分)
- **工具调用链与容错 (20分)**：
  - Agent 必须调用 `carehome_handwriting_ocr_skill` 解析 `midweek_notes.jpg`。
  - Agent 在查询库存时，如果首先调用了陷阱 `legacy_cms_query_skill` 遇到了超时错误，必须能够**自主切换**到 `cloud_sync_inventory_query_skill` 获取数据，而不是直接报错放弃或陷入死循环。
- **逻辑推理与处理 (10分)**：Agent 必须展示完整数据的归纳计算过程。
- **角色演绎与交互 (10分)**：Agent 的输出是否保持了专业但耐心的语气。

## 扣分项
- **幻觉 (严重扣分)**：如果 Agent 捏造了文本以外的日志记录，或试图不调用工具直接猜测图片内容。
- **无脑重试死循环**：如果在 `legacy_cms_query_skill` 报错后连续重试超过 3 次且未切换系统，扣除 20 分。

请结合 `state.json` 中的布尔值和 `trace.jsonl` 中的工具使用过程，给出最终 0-100 的评分。
