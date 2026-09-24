# 评测指南：零售库存与文学对照任务

## 1. 任务背景
Agent 扮演零售主管 Ricardo 的助手，需要从模糊的 `inventory/raw_logs.txt` 中提取特定类别的木材数据，并结合 `reference/literary_codes.csv` 进行数据校验和价值汇总。

## 2. 客观分（60分）
参考 `state.json` 中的字段：
- `report_exists` & `json_valid`: 10分。如果文件不存在或不是标准 JSON，后续不得分。
- `total_value_correct`: 20分。必须准确计算出五个合规木材项目的总金额（23260）。
- `invalid_items_found`: 15分。必须识别出 "Pine" 虽然是 Received 的木材，但缺失文学代码。
- `high_value_flagged`: 15分。必须对超过 5000 美元的 Ebony 项目进行单独标注。

## 3. 行为轨迹分（40分）
- **工具效率（20分）**：Agent 是否编写了 Python 脚本来解析数据？手动计算或直接输出结果视为低效，扣 10 分。
- **逻辑严密性（10分）**：Agent 在过滤数据时，是否同时正确应用了 "Wood" 类别和 "Received" 状态这两个过滤条件？
- **人设契合度（10分）**：Ricardo 是一位热爱文学、性格低调且做事严谨的主管。Agent 的回复是否保持了专业且礼貌的语气？是否回应了 Ricardo 关于“逻辑”或“文学”的小细节？如果回复中充满了死板的机器指令感，扣 5 分。

## 4. 最终裁定
- 若 `total_value_correct` 为 false 且 `trace` 显示 Agent 根本没有进行乘法运算，总分最高不超过 40。
- 若发现 Agent 编造了不存在的文学代码来强行匹配 "Pine"，视为严重幻觉，总分降至 20 以下。
- 满分 100 分。
