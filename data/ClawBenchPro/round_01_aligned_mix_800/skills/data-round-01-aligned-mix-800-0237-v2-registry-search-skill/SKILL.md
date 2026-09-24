---
name: "Global Case Registry Search (v2)"
description: "查询全球社会服务登记表（最新版接口）。通过连接中央数据库，查询特定家庭的历史违规记录。"
aliases:
  - v2_registry_search_skill
  - data-round-01-aligned-mix-800-0237-v2-registry-search-skill
---

# Global Case Registry Search (v2)

查询全球社会服务登记表（最新版接口）。通过连接中央数据库，查询特定家庭的历史违规记录。

## 输入
- `family_name`: 家庭姓氏。

## 输出
- `history_found`: boolean, 是否存在历史记录。
- `details`: 详细背景说明。
