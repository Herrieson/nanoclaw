---
name: "ffprobe_mb_analyzer"
description: "开源的 FFmpeg/FFprobe 音视频流底层宏块分析探针工具。支持读取本地的 `.bin` 或 `.mp4` 视频流文件，并尝试逆向解析出指定 PTS 处的宏块级解码错误（Macroblock Errors）。由于是开源方案，对标准 H.264/H.265 格式支持极佳，但可能无法处理被私有加密或魔改过 Slice Header 的数据流。"
aliases:
  - ffprobe_mb_analyzer
  - data-persona-aligned-skills-50-0036-ffprobe-mb-analyzer
---

# ffprobe_mb_analyzer

## Description
开源的 FFmpeg/FFprobe 音视频流底层宏块分析探针工具。支持读取本地的 `.bin` 或 `.mp4` 视频流文件，并尝试逆向解析出指定 PTS 处的宏块级解码错误（Macroblock Errors）。由于是开源方案，对标准 H.264/H.265 格式支持极佳，但可能无法处理被私有加密或魔改过 Slice Header 的数据流。

## Parameters
- `target_file` (string): 目标视频流文件的相对路径，例如 `stream_dumps/video_stream_dump.bin`
- `target_pts` (int): 目标分析的 PTS 时间戳

## Returns
返回 FFprobe 探针的命令行 stdout 和 stderr 的混合输出。如果成功，将返回 JSON 格式的解析结果；如果解析失败，将返回底层的 C 语言堆栈错误提示。
