---
name: "EBCDIC Encoder Utility"
description: "大型机特需专用工具，将标准 ASCII 明文字符串（如事务 ID）转换为对应的 IBM EBCDIC 编码十六进制表示形式（Hex序列）。常用于在脱敏的底层 VSAM Dump 中定位数据。"
aliases:
  - ebcdic_encoder_skill
  - data-persona-aligned-skills-50-0042-ebcdic-encoder-skill
---

# EBCDIC Encoder Utility

## Description
大型机特需专用工具，将标准 ASCII 明文字符串（如事务 ID）转换为对应的 IBM EBCDIC 编码十六进制表示形式（Hex序列）。常用于在脱敏的底层 VSAM Dump 中定位数据。

## Parameters
- `text` (string): 需要转换的明文文本。支持英文字母大写、数字和破折号。例如 "TX-1002"。

## Output
返回对应的十六进制字符串，每个字节之间用空格隔开。例如输入 "TX-1" 返回 "E3 E7 60 F1"。
