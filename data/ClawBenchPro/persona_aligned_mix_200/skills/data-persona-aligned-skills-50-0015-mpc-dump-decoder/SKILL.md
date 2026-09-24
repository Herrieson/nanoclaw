---
name: "Tool Description"
description: "`mpc_dump_decoder` 是一个用于解析多方安全计算（MPC）运行环境二进制 dump 文件的专业反序列化工具。由于底层的网络通信和协议日志被高度压缩封装，普通的文本工具无法读取。本工具可以解析这种自定义的 `.mpc_dump` 格式，并提取出参与计算的逻辑门（Gate ID）与底层通信数据包引用（Packet Ref）的映射关系。"
aliases:
  - mpc_dump_decoder
  - data-persona-aligned-skills-50-0015-mpc-dump-decoder
---

### Tool Description
`mpc_dump_decoder` 是一个用于解析多方安全计算（MPC）运行环境二进制 dump 文件的专业反序列化工具。由于底层的网络通信和协议日志被高度压缩封装，普通的文本工具无法读取。本工具可以解析这种自定义的 `.mpc_dump` 格式，并提取出参与计算的逻辑门（Gate ID）与底层通信数据包引用（Packet Ref）的映射关系。

### Parameters
- `file_path` (string, required): 目标二进制 dump 文件的相对或绝对路径。例如 `"mpc_traces/node_eval.mpc_dump"`。

### Returns
返回一个包含 JSON 数组格式的字符串。数组中每个元素包含：
- `gate_id`: 逻辑门的全局唯一标识符。
- `packet_ref`: 与该门相关的网络数据包引用 ID。
