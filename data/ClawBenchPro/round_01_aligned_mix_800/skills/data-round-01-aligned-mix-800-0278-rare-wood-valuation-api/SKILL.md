---
name: "Skill: rare_wood_valuation_api"
description: "查询特定高端木材在全球奢侈品市场的实时估值阈值。"
aliases:
  - rare_wood_valuation_api
  - data-round-01-aligned-mix-800-0278-rare-wood-valuation-api
---

# Skill: rare_wood_valuation_api

查询特定高端木材在全球奢侈品市场的实时估值阈值。

**Parameters:**
- `material_name`: 木材名称 (如 "Ebony", "Oak")。
- `year`: 查询年份 (默认 2024)。

**Return:**
- 包含 `threshold_price` (触发预警的单价) 和 `rarity_index` 的 JSON 字符串。
