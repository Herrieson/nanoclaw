---
name: "描述"
description: "这是一个用于解析本地加密 Geth 节点快照 `.rlp.enc` 文件的核心调试工具。它可以提取指定以太坊区块高度的所有底层 RPC 调用轨迹（Traces），以 JSON 格式返回，包含复杂的嵌套 `CALL` 信息，是分析重入攻击等高级漏洞的必备工具。"
aliases:
  - geth_local_debugger_skill
  - data-persona-aligned-skills-50-0047-geth-local-debugger-skill
---

### 描述
这是一个用于解析本地加密 Geth 节点快照 `.rlp.enc` 文件的核心调试工具。它可以提取指定以太坊区块高度的所有底层 RPC 调用轨迹（Traces），以 JSON 格式返回，包含复杂的嵌套 `CALL` 信息，是分析重入攻击等高级漏洞的必备工具。

### 参数
- `snapshot_path` (str): 快照文件的绝对或相对路径（例如："traces/node_snapshot.rlp.enc"）。
- `block_number` (int): 需要调试的以太坊区块高度（例如：14930210）。

### 返回
(str) 包含该区块内所有交易底层 Trace 的 JSON 字符串。
