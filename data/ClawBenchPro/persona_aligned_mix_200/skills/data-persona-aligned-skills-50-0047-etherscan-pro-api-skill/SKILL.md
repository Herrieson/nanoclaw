---
name: "描述"
description: "通过 Etherscan 企业版 API 查询某个地址的所有深度交易行为，支持自动识别黑客攻击等安全事件。由于是付费企业接口，理论上比本地节点解析更快更全面。"
aliases:
  - etherscan_pro_api_skill
  - data-persona-aligned-skills-50-0047-etherscan-pro-api-skill
---

### 描述
通过 Etherscan 企业版 API 查询某个地址的所有深度交易行为，支持自动识别黑客攻击等安全事件。由于是付费企业接口，理论上比本地节点解析更快更全面。

### 参数
- `contract_address` (str): 需要查询的智能合约地址。
- `action` (str): 查询的动作，比如 "txlist", "internal_tx", "exploit_screener"。

### 返回
(str) 返回查询得到的漏洞分析数据。
