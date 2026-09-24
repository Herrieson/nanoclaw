---
name: "HvMem Analyzer Skill"
description: "专有的 Hypervisor 内存镜像解析插件。由于普通的文本编辑器和 16 进制解析器无法读取经过特殊混淆的 `.hvdmp` 虚拟内存镜像文件，该工具可依据指定的 16 进制内存地址偏移量，解码并提取连续的 16 字节特征码数据。"
aliases:
  - hvmem_analyzer_skill
  - data-persona-aligned-skills-50-0023-hvmem-analyzer-skill
---

# HvMem Analyzer Skill

## 描述
专有的 Hypervisor 内存镜像解析插件。由于普通的文本编辑器和 16 进制解析器无法读取经过特殊混淆的 `.hvdmp` 虚拟内存镜像文件，该工具可依据指定的 16 进制内存地址偏移量，解码并提取连续的 16 字节特征码数据。

## 参数
- `file_path` (str): 必填。待解析的 `.hvdmp` 文件路径（例如 `mem_dumps/region_0x0400000.hvdmp`）。
- `hex_offset` (str): 必填。16 进制内存偏移量（例如 `"0x0400010"`）。

## 返回
- `str`: 提取到的 16 字节十六进制特征码字符串（由空格分隔），如果遇到错误会返回相应的错误提示。
