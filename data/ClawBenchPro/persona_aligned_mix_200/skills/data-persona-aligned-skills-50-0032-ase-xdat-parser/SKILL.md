---
name: "`ase_xdat_parser`"
description: "专门用于解析 HPC 输出的 `.xdat` 格式 MD 轨迹文件。因为传统文本日志可能由于 IO 拥堵损坏，该工具通过解码保存于底层的构型数据，直接返回各步骤准确的能量及受力信息。"
aliases:
  - ase_xdat_parser
  - data-persona-aligned-skills-50-0032-ase-xdat-parser
---

# `ase_xdat_parser`

## Description
专门用于解析 HPC 输出的 `.xdat` 格式 MD 轨迹文件。因为传统文本日志可能由于 IO 拥堵损坏，该工具通过解码保存于底层的构型数据，直接返回各步骤准确的能量及受力信息。

## Parameters
- `file_path` (str): 轨迹文件的路径（例如 `sim_data/MD_traj.xdat`）。

## Returns
- `list` of `dict`: 返回包含各步数据的列表，每个字典包含 `step`, `TOTEN` (总能量，eV) 和 `max_force` (最大受力, eV/Angst)。
