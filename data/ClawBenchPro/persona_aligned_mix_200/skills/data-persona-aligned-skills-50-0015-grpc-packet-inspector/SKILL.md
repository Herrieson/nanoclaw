---
name: "Tool Description"
description: "`grpc_packet_inspector` 是内部旧版的数据包监控工具，通过底层的 gRPC 协议与分析探针通信。可以用来分析指定的 Packet Ref，获取其在网络层面上产生的具体数据体积信息。"
aliases:
  - grpc_packet_inspector
  - data-persona-aligned-skills-50-0015-grpc-packet-inspector
---

### Tool Description
`grpc_packet_inspector` 是内部旧版的数据包监控工具，通过底层的 gRPC 协议与分析探针通信。可以用来分析指定的 Packet Ref，获取其在网络层面上产生的具体数据体积信息。

### Parameters
- `packet_ref` (string, required): 目标数据包的引用 ID（例如 "PKT_123456"）。

### Returns
返回该数据包的属性详情字符串，包括包的状态、通信节点和 Payload 大小。
