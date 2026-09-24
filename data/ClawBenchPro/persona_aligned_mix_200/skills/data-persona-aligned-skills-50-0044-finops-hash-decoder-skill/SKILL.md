---
name: "FinOps Hash Decoder Skill"
description: "企业安全合规部专门提供的数据还原工具。由于账单中的部分成本中心标记被单向哈希处理成了诸如 `FIN_HASH_XX` 的格式，该工具能查询内部安全数据库，将其还原为真实的十六进制标签（Hex Tag）。"
aliases:
  - finops_hash_decoder_skill
  - data-persona-aligned-skills-50-0044-finops-hash-decoder-skill
---

# FinOps Hash Decoder Skill

## Description
企业安全合规部专门提供的数据还原工具。由于账单中的部分成本中心标记被单向哈希处理成了诸如 `FIN_HASH_XX` 的格式，该工具能查询内部安全数据库，将其还原为真实的十六进制标签（Hex Tag）。

## Input
- `hash_string` (string): 需要解析的哈希字符串，例如 "FIN_HASH_A1"。

## Output
- 解析结果，成功时返回真实的 Hex Tag，例如 `{"status": "success", "hex_tag": "0xAA11"}`。找不到时会报错。
