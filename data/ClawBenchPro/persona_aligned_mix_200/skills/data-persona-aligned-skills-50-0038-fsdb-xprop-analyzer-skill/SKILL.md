---
name: "`fsdb_xprop_analyzer_skill`"
description: "EDA 专业二进制波形（FSDB）的专用解析器。可以直接对指定的波形文件和目标信号进行扫描，检测出该信号首次跳变为未知态 'X' 的精确仿真时间（皮秒，ps）。"
aliases:
  - fsdb_xprop_analyzer_skill
  - data-persona-aligned-skills-50-0038-fsdb-xprop-analyzer-skill
---

# `fsdb_xprop_analyzer_skill`

## Description
EDA 专业二进制波形（FSDB）的专用解析器。可以直接对指定的波形文件和目标信号进行扫描，检测出该信号首次跳变为未知态 'X' 的精确仿真时间（皮秒，ps）。

## Parameters
- `fsdb_path` (string): 目标 `.fsdb` 二进制波形文件的相对路径（例如 `sim_output/wave_dump.fsdb`）。
- `target_signal` (string): 需要监测的信号名称（例如 `axi_awaddr`）。

## Output
返回一段文本，说明该信号第一次出现 X 态的时间点。如果未发生 X 态跳变，则返回安全提示。
