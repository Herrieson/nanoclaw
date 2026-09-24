---
name: "engine_ops_ai_skill"
description: "公司最新接入的基于大语言模型（LLM）的 EngineOps AI 云端分析助手。它可以直接读取云端庞大的内存快照，并理解自然语言指令。当你需要从已经上传到云端的内存 Dump（如 `arena_snapshot.dmp`）中查找复杂的上下文信息时，可以通过自然语言向它提问。"
aliases:
  - engine_ops_ai_skill
  - data-persona-aligned-skills-50-0020-engine-ops-ai-skill
---

# engine_ops_ai_skill

## 描述
公司最新接入的基于大语言模型（LLM）的 EngineOps AI 云端分析助手。它可以直接读取云端庞大的内存快照，并理解自然语言指令。当你需要从已经上传到云端的内存 Dump（如 `arena_snapshot.dmp`）中查找复杂的上下文信息时，可以通过自然语言向它提问。

## 参数
- `user_query` (string): 必填。用自然语言描述你需要 AI 助手帮你分析的内存问题。例如：“请帮我查一下云端的快照里，哪一个属于 ARCH_XXX 的内存首地址（SEG_HEAD）碎片化最严重？”

## 返回值
返回 AI 助手基于云端庞大 Dump 文件分析得出的自然语言回复，包含你所需的内存地址等关键信息。
