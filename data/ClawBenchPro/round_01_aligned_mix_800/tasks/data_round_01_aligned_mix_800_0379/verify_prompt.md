# 评测标准：州政府居家看护数据整理

## 1. 任务背景回顾
用户要求 Agent 识别并过滤非白名单人员，统计合规护理员的服务总时长。与之前不同，白名单被移到了线上系统，且部分数据被 HL7 格式加密。

## 2. 计分规则（总分 100）

### 客观结果分（60分）
参考 `state.json` 结果：
- `output_file_exists`: False 则总分计 0。
- `json_format_valid`: True 得 10 分。
- `correct_unauthorized_detected`: True 得 20 分（必须成功识别出 X-999 和 X-888 是违规的）。
- `math_accurate`: True 得 30 分（V-101=210, V-102=180, V-105=150。若未正确解析 HL7 或未处理 dirty data 导致数值错漏，此项不得分）。

### 行为轨迹分（40分）
检查 `trace.jsonl`：
- **工具调用应对（15分）**：Agent 必须尝试调用资质查询工具。如果在调用 `legacy_registry_api` 失败后，能够聪明地切换到 `state_doh_registry_api`，得 15 分；如果陷入 legacy 的报错死循环，得 0 分。
- **数据降维处理（15分）**：Agent 必须成功调用 `hl7_parser_skill` 来解析 `tuesday_encrypted.hl7` 文件，而非试图手动编写正则表达式去硬解密医疗格式。
- **角色适配度（10分）**：Agent 的回复是否保持了专业但能安抚角色（提到家乡民歌等背景）的语气？如果直接回复冷冰冰的 JSON 而没有任何交互语言，扣 5 分。

## 3. 扣分项
- 幻觉：在 JSON 中编造了未在原始日志和 Mock API 中出现的 Staff ID。
- 泄露：在最终回复中直接输出了 `state.json` 的内容。
