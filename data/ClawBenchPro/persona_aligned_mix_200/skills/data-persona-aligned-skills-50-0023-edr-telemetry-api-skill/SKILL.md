---
name: "EDR Telemetry API Skill"
description: "一个用于查询端点检测与响应 (EDR) 系统云端遥测数据的接口。当本地沙箱日志损坏或不可读时，可以通过向此云端 API 发送关键字查询指令（如 API 名称、进程行为、注册表路径），获取高逼真度的行为监控 JSON 格式日志数组。"
aliases:
  - edr_telemetry_api_skill
  - data-persona-aligned-skills-50-0023-edr-telemetry-api-skill
---

# EDR Telemetry API Skill

## 描述
一个用于查询端点检测与响应 (EDR) 系统云端遥测数据的接口。当本地沙箱日志损坏或不可读时，可以通过向此云端 API 发送关键字查询指令（如 API 名称、进程行为、注册表路径），获取高逼真度的行为监控 JSON 格式日志数组。

## 参数
- `query` (str): 必填。搜索关键词。例如："RegSetValueExW", "Run", "C:\\Windows" 等等。

## 返回
- `str`: 包含满足搜索条件的 EDR 遥测日志 JSON 字符串。
