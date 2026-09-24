---
name: "eco_id_validator_skill"
description: "此工具用于连接到“全球生态志愿者数据库”，验证志愿者的姓名与 Eco_ID 是否匹配。"
aliases:
  - eco_id_validator_skill
  - data-round-01-aligned-mix-800-0330-eco-id-validator-skill
---

# eco_id_validator_skill

此工具用于连接到“全球生态志愿者数据库”，验证志愿者的姓名与 Eco_ID 是否匹配。

### 输入参数
- `name`: 志愿者姓名 (string)

### 输出
- 返回该姓名对应的官方 `eco_id`。如果该志愿者有多个条目或存在身份异常，将返回警告信息。
