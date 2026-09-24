---
name: "generate_kill_token"
description: "生产环境数据库高危操作鉴权工具。在执行强杀进程前，必须提供有效的 Kill Token。本工具接收罪魁祸首的十进制 `pid` 和事务 `xid`，通过特定的安全哈希算法计算出合法的 `kill_token`。"
aliases:
  - generate_kill_token
  - data-persona-aligned-skills-50-0011-generate-kill-token
---

# generate_kill_token

## Description
生产环境数据库高危操作鉴权工具。在执行强杀进程前，必须提供有效的 Kill Token。本工具接收罪魁祸首的十进制 `pid` 和事务 `xid`，通过特定的安全哈希算法计算出合法的 `kill_token`。

## Usage
