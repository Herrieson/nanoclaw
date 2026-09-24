---
name: "legacy_dump_analyzer_skill"
description: "公司上一代的 EngineOps 云端内存快照分析 API。用于向云端服务器发送查询指令，检索已上传的超大内存转储（Dump）文件。"
aliases:
  - legacy_dump_analyzer_skill
  - data-persona-aligned-skills-50-0020-legacy-dump-analyzer-skill
---

# legacy_dump_analyzer_skill

## 描述
公司上一代的 EngineOps 云端内存快照分析 API。用于向云端服务器发送查询指令，检索已上传的超大内存转储（Dump）文件。

## 参数
- `query` (string): 必填。向分析器发送的检索命令，例如指定某个 Archetype ID 去查询相关内存碎片情况。

## 返回值
返回查询结果（可能包含内存地址和碎片化详情）。
