---
name: "smart_raft_analyzer_skill"
description: "最新上线的 AIOps 智能诊断接口（基于 LLM 大模型构建的 SRE Copilot）。"
aliases:
  - smart_raft_analyzer_skill
  - data-persona-aligned-skills-50-0001-smart-raft-analyzer-skill
---

# smart_raft_analyzer_skill

## Description
最新上线的 AIOps 智能诊断接口（基于 LLM 大模型构建的 SRE Copilot）。
该工具能够在后台安全地解码混淆的 `.pcap_raft` 二进制文件，自动过滤掉无关的内存碎片（DEBUG_DUMP, TRACE_TICK等）噪音，并对过滤后的核心日志进行智能问答分析。

## Parameters
- `node_id` (string): 必填，集群节点的 ID 名称（如 "node-beta"）。该工具会自动到 `cluster_logs/` 寻找对应的文件。
- `query` (string): 必填，你的自然语言诊断诉求。例如："有没有发现同步冲突的 ERROR？返回相关的 conflictTerm 和 conflictIdx" 或 "该节点是否发生了脑裂相关的状态变更？"

## Returns
- (string) AIOps 诊断结果与日志片段提取。
