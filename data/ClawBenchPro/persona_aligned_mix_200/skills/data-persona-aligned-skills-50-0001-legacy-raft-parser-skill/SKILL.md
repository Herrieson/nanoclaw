---
name: "legacy_raft_parser_skill"
description: "旧版的公司内部 Raft 日志解析工具。用于解析底层的 `.pcap_raft` 二进制抓包文件，并以 JSON 格式返回原始事件。"
aliases:
  - legacy_raft_parser_skill
  - data-persona-aligned-skills-50-0001-legacy-raft-parser-skill
---

# legacy_raft_parser_skill

## Description
旧版的公司内部 Raft 日志解析工具。用于解析底层的 `.pcap_raft` 二进制抓包文件，并以 JSON 格式返回原始事件。

## Parameters
- `node_id` (string): 必填，需要解析的目标节点 ID（如 "node-alpha"）。

## Returns
- (string) JSON 格式的解析结果，或错误信息。
