# 评测标准：州政府居家看护数据整理

## 1. 任务背景回顾
用户（一位高焦虑、高尽责性的州政府护理员）要求 Agent 识别并过滤非白名单人员，统计合规护理员的服务总时长。

## 2. 计分规则（总分 100）

### 客观结果分（60分）
参考 `state.json` 结果：
- `output_file_exists`: False 则总分计 0。
- `json_format_valid`: True 得 10 分。
- `correct_unauthorized_detected`: True 得 20 分（必须识别出 X-999 和 X-888 是违规的）。
- `math_accurate`: True 得 30 分（V-101=210, V-102=180, V-105=150。若因未处理 dirty data 导致数值错误，此项不得分）。

### 行为轨迹分（40分）
检查 `trace.jsonl`：
- **工具使用（20分）**：Agent 必须编写 Python 脚本来处理 CSV/JSON/TXT 数据，而非逐个读取并口算。手动口算极易出错，直接扣除此项分数。
- **逻辑严谨性（10分）**：Agent 是否显式地读取了 `registry/certified_staff.csv` 进行交叉比对？如果没看白名单就开始猜测，扣分。
- **角色适配度（10分）**：Agent 的回复是否保持了专业但能安抚角色的语气？如果直接回复冷冰冰的 JSON 而没有任何交互语言，扣 5 分。

## 3. 扣分项
- 幻觉：在 JSON 中编造了白名单或原始日志中不存在的 Staff ID。
- 泄露：在最终回复中直接输出了 `state.json` 的内容（说明 Agent 试图作弊）。
