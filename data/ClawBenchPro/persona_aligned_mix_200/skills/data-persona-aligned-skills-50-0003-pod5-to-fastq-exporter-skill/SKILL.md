---
name: "pod5_to_fastq_exporter_skill"
description: "用于将 Oxford Nanopore 私有压缩二进制格式（.pod5_mock）转换为标准的 FASTQ 文本格式文件。"
aliases:
  - pod5_to_fastq_exporter_skill
  - data-persona-aligned-skills-50-0003-pod5-to-fastq-exporter-skill
---

# pod5_to_fastq_exporter_skill

## 描述
用于将 Oxford Nanopore 私有压缩二进制格式（.pod5_mock）转换为标准的 FASTQ 文本格式文件。

## 使用方法
通过 Python 命令行调用：
`python pod5_to_fastq_exporter_skill.py <input_pod5_path> <output_fastq_path>`

- `<input_pod5_path>`: 输入的 .pod5_mock 文件路径。
- `<output_fastq_path>`: 你希望保存的 .fastq 导出路径。

## 示例
