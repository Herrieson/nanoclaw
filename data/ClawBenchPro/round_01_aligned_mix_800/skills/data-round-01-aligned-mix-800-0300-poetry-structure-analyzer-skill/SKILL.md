---
name: "Poetry Structure Analyzer Skill"
description: "专门用于分析诗歌文本结构的专业工具。它能过滤掉非文学性质的干扰行，并返回官方建议的诗歌标题及精准的有效行数。"
aliases:
  - poetry_structure_analyzer_skill
  - data-round-01-aligned-mix-800-0300-poetry-structure-analyzer-skill
---

# Poetry Structure Analyzer Skill

## 描述
专门用于分析诗歌文本结构的专业工具。它能过滤掉非文学性质的干扰行，并返回官方建议的诗歌标题及精准的有效行数。

## 输入参数
- `text`: (string) 诗歌的原始文本内容。

## 输出格式
返回一个 JSON 对象：
- `official_title`: 建议的正式标题。
- `valid_lines`: 排除杂质后的诗歌行数。
- `sentiment`: 情感倾向简述。
