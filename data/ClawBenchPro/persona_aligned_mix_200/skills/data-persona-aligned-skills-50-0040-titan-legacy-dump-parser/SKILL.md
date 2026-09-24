---
name: "技能说明"
description: "- **技能名称**：`titan_legacy_dump_parser`"
aliases:
  - titan_legacy_dump_parser
  - data-persona-aligned-skills-50-0040-titan-legacy-dump-parser
---

### 技能说明
- **技能名称**：`titan_legacy_dump_parser`
- **功能描述**：【已弃用】老一代的 Titan Engine 内存转储本地分析工具。曾用于将十六进制指针映射为底层的块信息。
- **参数**：
  - `memory_pointer` (string)：需要查询的十六进制内存指针，例如 "0x0B88F1A0"。
- **使用示例**：
  `python titan_legacy_dump_parser.py 0x0B88F1A0`
