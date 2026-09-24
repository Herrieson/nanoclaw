---
name: "cuckoo_trace_parser_skill"
description: "专门用于解析 Cuckoo Sandbox V3 安全专有格式（`.ctx`文件）的解码工具。它可以剔除文件的混淆头并解压内部有效载荷，将其还原为人类可读的明文系统调用追踪日志（System Call Trace）。"
aliases:
  - cuckoo_trace_parser_skill
  - data-persona-aligned-skills-50-0043-cuckoo-trace-parser-skill
---

# cuckoo_trace_parser_skill

## Description
专门用于解析 Cuckoo Sandbox V3 安全专有格式（`.ctx`文件）的解码工具。它可以剔除文件的混淆头并解压内部有效载荷，将其还原为人类可读的明文系统调用追踪日志（System Call Trace）。

## Parameters
- `file_path` (str): 必须传入待解析的 `.ctx` 文件相对或绝对路径，例如 `sandbox_out/trace_sys.ctx`。

## Returns
- (str): 解析成功的明文日志文本内容。如果文件不存在或格式不正确，则返回错误提示。

## Example
