---
name: "stream_vision_internal_api"
description: "公司内网专用的“StreamVision 音视频底层诊断 API”。针对经过“自定义环形缓冲分配器”处理过的私有加密/魔改版视频流 Dump（如 `.bin` 文件）有着独家解析能力。该 API 利用内部解密密钥，可以直接定位到特定的 PTS（显示时间戳），并提取该帧内部的宏块(Macroblock)损坏和丢失情况。"
aliases:
  - stream_vision_internal_api
  - data-persona-aligned-skills-50-0036-stream-vision-internal-api
---

# stream_vision_internal_api

## Description
公司内网专用的“StreamVision 音视频底层诊断 API”。针对经过“自定义环形缓冲分配器”处理过的私有加密/魔改版视频流 Dump（如 `.bin` 文件）有着独家解析能力。该 API 利用内部解密密钥，可以直接定位到特定的 PTS（显示时间戳），并提取该帧内部的宏块(Macroblock)损坏和丢失情况。

## Parameters
- `query` (string): 采用自然语言或类 JSON 格式向 API 发送指令。你必须在请求中明确指明你想要查询的 `PTS` 数字。
  示例: "Please analyze the macroblock errors for PTS 824050000" 或 "{'pts': 824050000}"

## Returns
返回内部诊断工具的分析报告，包含指定帧的严重程度评估以及具体的宏块损坏坐标列表。
