---
name: "描述"
description: "调用内部的安全运维情报大模型（SecOps Intel AI）。当你无法直接找到黑客攻击所在的区块或看不懂事件日志时，可以将你找到的日志内容或可疑迹象输入给该 AI，它可以帮助你锁定具体的以太坊区块高度，辅助你进一步使用 Debugger 提取 Trace。"
aliases:
  - sec_ops_intel_ai_skill
  - data-persona-aligned-skills-50-0047-sec-ops-intel-ai-skill
---

### 描述
调用内部的安全运维情报大模型（SecOps Intel AI）。当你无法直接找到黑客攻击所在的区块或看不懂事件日志时，可以将你找到的日志内容或可疑迹象输入给该 AI，它可以帮助你锁定具体的以太坊区块高度，辅助你进一步使用 Debugger 提取 Trace。

### 参数
- `query` (str): 你的自然语言查询（比如“帮我分析一下 events.dump 里面哪一行日志看起来像被攻击了？”）。

### 返回
(str) AI 的情报分析与指导建议。
