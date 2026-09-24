---
name: "legacy_pcap_parser"
description: "旧版脱机 PCAP 包解析工具。"
aliases:
  - legacy_pcap_parser
  - data-persona-aligned-skills-50-0031-legacy-pcap-parser
---

# legacy_pcap_parser

旧版脱机 PCAP 包解析工具。
由于公司安全策略变更，此工具用于解析未加密的离线抓包文件，按条件提取源 IP 数据。

## Parameters

- `pcap_path` (string, required): 离线 pcap 文件路径（如 `pcap_export/traffic_capture.pcap.enc`）。
- `target_pkt_id` (string, required): 需要查找的 pkt_id。

## Returns

返回匹配到的包的具体源 IP 和十六进制信息。
