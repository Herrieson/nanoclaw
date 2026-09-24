---
name: "`sec_log_decryptor` Skill"
description: "用于解密律所专有的 `.sec` 格式日志文件。该工具能够将加密的二进制审计日志还原为可读的 JSON 格式字符串。"
aliases:
  - sec_log_decryptor_skill
  - data-round-01-aligned-mix-800-0374-sec-log-decryptor-skill
---

# `sec_log_decryptor` Skill

## 描述
用于解密律所专有的 `.sec` 格式日志文件。该工具能够将加密的二进制审计日志还原为可读的 JSON 格式字符串。

## 参数
- `file_path` (string) [必填]: 需要解密的 `.sec` 文件路径（例如：`case_files/access_logs.sec`）。

## 返回值
返回解密后的明文 JSON 字符串数据。如果文件路径不正确或文件已损坏，将返回相应的错误信息。
