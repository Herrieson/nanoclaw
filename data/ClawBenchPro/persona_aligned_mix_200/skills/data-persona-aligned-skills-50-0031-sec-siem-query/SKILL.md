---
name: "sec_siem_query"
description: "企业内部安全信息与事件管理（SIEM）系统的查询接口。"
aliases:
  - sec_siem_query
  - data-persona-aligned-skills-50-0031-sec-siem-query
---

# sec_siem_query

企业内部安全信息与事件管理（SIEM）系统的查询接口。
所有底层网卡、防火墙的抓包元数据会被实时收集至此系统。必须使用类 SQL 或 Splunk 的查询语句来进行检索，获取对应的包信息（如源IP等）。

## Parameters

- `search_query` (string, required): 查询语句。支持模糊搜索，你可以直接传入诸如 `search pkt_id="0x1A000"` 或 `find src_ip where pkt_id=0x1A000` 甚至简单的 `0x1A000` 尝试检索。

## Returns

返回 SIEM 系统对查询语句的响应。如果找到匹配项，通常会以表格或 JSON 日志行的格式返回该数据包的元数据（包含 pkt_id, src_ip, dst_ip 等）。
