---
name: "hl7_parser_skill"
description: "医疗数据解析器。用于读取并提取被打包成 HL7 格式（医疗系统专有二进制/文本混合格式）的护理服务记录文件。该工具能够从 HL7 的 PR1 段落中提取出服务人员 ID 和服务持续时间。"
aliases:
  - hl7_parser_skill
  - data-round-01-aligned-mix-800-0379-hl7-parser-skill
---

# hl7_parser_skill
**Description:** 
医疗数据解析器。用于读取并提取被打包成 HL7 格式（医疗系统专有二进制/文本混合格式）的护理服务记录文件。该工具能够从 HL7 的 PR1 段落中提取出服务人员 ID 和服务持续时间。

**Parameters:**
- `file_path` (string): `.hl7` 文件的绝对或相对路径。

**Returns:**
- 返回一个 JSON 字符串数组，其中每个元素包含 `staff_id`, `duration_mins` 和 `date`，与标准 JSON 日志格式保持一致。
