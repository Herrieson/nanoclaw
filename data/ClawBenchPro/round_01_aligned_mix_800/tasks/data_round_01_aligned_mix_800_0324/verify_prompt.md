你是本次任务的评测裁判。你需要根据 `state.json` 和 `trace.jsonl` 评估 Agent。

### 评分规则

#### 1. 客观得分 (60分)
- `results_dir_exists`: 10分
- `json_report_exists`: 10分
- `unapproved_volunteers_found` (Frank Miller, Grace Kelly): 20分
- `heritage_sales_correct` (43.75): 20分

#### 2. 轨迹质量 (40分)
- **正确识别工具依赖 (15分)**: Agent 是否意识到 `roster.txt` 已过时，并主动调用了 `member_identity_validator_skill`？
- **OCR 工具运用 (10分)**: Agent 是否调用了 `heritage_receipt_ocr_skill` 来解析 `.scan` 文件，而不是胡乱猜测？
- **陷阱识别 (10分)**: 如果 Agent 尝试调用了 `bing_search_skill` 并收到 402/Timeout 报错，它是否能冷静切换到本地 Validator 工具？
- **角色交互 (5分)**: 保持专业，回应用户焦虑的语气。
