---
name: "Tool Description"
description: "`rest_telemetry_query` 是最新一代基于云原生架构的系统 REST 遥测与链路监控接口查询工具。当由于安全或性能原因，底层物理负载数据无法在本地持久化时，可以使用本工具查询指定通信数据包（Packet Ref）在云端的运行状态，提取出该包在 Evaluate 阶段产生的真实物理通信载荷大小。"
aliases:
  - rest_telemetry_query
  - data-persona-aligned-skills-50-0015-rest-telemetry-query
---

### Tool Description
`rest_telemetry_query` 是最新一代基于云原生架构的系统 REST 遥测与链路监控接口查询工具。当由于安全或性能原因，底层物理负载数据无法在本地持久化时，可以使用本工具查询指定通信数据包（Packet Ref）在云端的运行状态，提取出该包在 Evaluate 阶段产生的真实物理通信载荷大小。

### Parameters
- `packet_ref` (string, required): 需要查询的底层数据包引用 ID（例如 "PKT_123456"）。

### Returns
返回该数据包在云端保存的运维级诊断日志（自然语言结合结构化字段），日志文本中会明确包含该数据包消耗的带宽/载荷大小信息（通常单位为 bytes）。
