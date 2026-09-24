---
name: "Perf Trace Analyzer Skill"
description: "专门用于解析自研引擎二进制 `.trace` 性能文件的分析器。由于性能日志是被高度序列化的，无法直接通过文件读取，必须调用此工具进行解码和异常捕获。"
aliases:
  - perf_trace_analyzer_skill
  - data-persona-aligned-skills-50-0019-perf-trace-analyzer-skill
---

# Perf Trace Analyzer Skill
专门用于解析自研引擎二进制 `.trace` 性能文件的分析器。由于性能日志是被高度序列化的，无法直接通过文件读取，必须调用此工具进行解码和异常捕获。

## 参数
- `file_path` (string, required): 目标 `.trace` 文件的绝对或相对路径。

## 返回值
返回在 Trace 文件中探测到的性能严重超时（Delta Time > 16.6ms 阈值）的 Tick 及其对应的参与物理运算的 Entity ID 列表。
