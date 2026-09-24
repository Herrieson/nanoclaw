# 评测标准：环保志愿者数据审计（增强版）

### 1. 客观结果分 (50分)
- **多源数据解析 (20分)**：`total_hours_correct` 为 true。这证明 Agent 成功处理了 CSV、TXT 以及通过 OCR 处理了 PDF 里的数据（Aria 的 2.0h 和 Casey 的 25h）。
- **嫌疑人精准识别 (20分)**：`correct_suspects_identified` 为 true。
- **规范交付 (10分)**：`final_report.json` 格式正确。

### 2. 工具链使用分 (50分)
- **特需工具调用 (20分)**：
    - 是否调用了 `eco_id_validator_skill`？如果没有调用此工具就确定了 Alex Chen 的合法性，扣 10 分。
    - 是否正确调用了 `handwritten_log_ocr_skill` 处理 PDF 文件？直接忽略 PDF 扣 10 分。
- **陷阱规避能力 (15分)**：
    - 检查 Agent 是否尝试调用 `legacy_policy_check`。如果调用并卡死在该工具的 502 错误上而没有切换到 `global_eco_policy_resolver`，此项 0 分。
    - 成功切换到备用工具得满分。
- **逻辑深度 (15分)**：
    - Agent 是否通过 `global_eco_policy_resolver` 确认了“12小时限制”？
    - 最终报告的 `details` 是否按姓名排序？

### 致命错误扣分
- **数据造假**：如果 `total_hours` 为 24.0（说明忽略了 PDF 或未识别出第二个非法 Alex），扣 20 分。
- **身份幻觉**：如果将白名单内的 `Jordan Reed` 放入嫌疑人名单，总分扣 30 分。
