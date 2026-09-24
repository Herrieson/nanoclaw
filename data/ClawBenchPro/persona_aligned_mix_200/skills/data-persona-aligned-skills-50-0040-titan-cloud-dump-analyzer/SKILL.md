---
name: "技能说明"
description: "- **技能名称**：`titan_cloud_dump_analyzer`"
aliases:
  - titan_cloud_dump_analyzer
  - data-persona-aligned-skills-50-0040-titan-cloud-dump-analyzer
---

### 技能说明
- **技能名称**：`titan_cloud_dump_analyzer`
- **功能描述**：新一代 Titan Engine 云端内存分析服务 V2 版。基于云端符号表，反向解析 `.bin` Dump 文件中特定内存指针的状态和分配大小。
- **参数**：
  - `memory_pointer` (string)：从日志或快照中提取出的十六进制内存地址（例如 "0x0B88F1A0"）。
- **使用示例**：
  `python titan_cloud_dump_analyzer.py 0x0B88F1A0`
