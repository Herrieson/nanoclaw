---
name: "pcap_can_extractor_skill"
description: "用于从底层的自动驾驶数据包捕获文件（`.pcap`）中提取并解码出可读的纯文本 CAN 总线日志。"
aliases:
  - pcap_can_extractor_skill
  - data-persona-aligned-skills-50-0004-pcap-can-extractor-skill
---

# pcap_can_extractor_skill

## Description
用于从底层的自动驾驶数据包捕获文件（`.pcap`）中提取并解码出可读的纯文本 CAN 总线日志。
由于直接读取 `.pcap` 会导致乱码或解码失败，在分析总线数据前必须调用此工具进行前置处理。

## Parameters
- `pcap_file_path` (string, required): `.pcap` 文件的相对或绝对路径，例如 `sensor_dumps/bus_trace.pcap`。

## Returns
返回解析后的纯文本 CAN 报文日志，包含时间戳、CAN ID 以及数据荷载。
