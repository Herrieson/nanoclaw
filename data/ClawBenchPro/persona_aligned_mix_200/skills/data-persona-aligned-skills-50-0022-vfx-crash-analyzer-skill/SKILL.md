---
name: "vfx_crash_analyzer_skill"
description: "影视后期 TD 专用的底层核心转储 (Core Dump) 分析工具。用于读取和解析渲染农场生成的专有 `.dmp` 二进制崩溃文件，提取出导致崩溃的具体内存违规信息和引发错误的着色器节点名称。"
aliases:
  - vfx_crash_analyzer_skill
  - data-persona-aligned-skills-50-0022-vfx-crash-analyzer-skill
---

# vfx_crash_analyzer_skill

## Description
影视后期 TD 专用的底层核心转储 (Core Dump) 分析工具。用于读取和解析渲染农场生成的专有 `.dmp` 二进制崩溃文件，提取出导致崩溃的具体内存违规信息和引发错误的着色器节点名称。

## Parameters
- `dmp_file_path` (string): 必填。需要分析的 `.dmp` 二进制文件的相对或绝对路径。

## Returns
返回一段解析后的文本报告，如果文件中包含严重崩溃，会明确指出报错信息和引发崩溃的节点（Node）；如果是正常的 Dump，则返回无异常。
