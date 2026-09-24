该死！凌晨3点大促主链路的 P99 延迟居然直接飙到了 5 秒以上！整个交易集群都在告警，Goroutine 积压快把内存撑爆了。

我刚从 Jaeger 集群里把这段时间的分布式追踪快照拉了下来，全部分块塞在 `traces/` 目录里了。另外在 `nodes/` 目录下还有一些节点崩溃前打出来的 Goroutine Dump 乱码，可能有关联也可能是干扰。

我没时间去手写解析脚本了，你赶紧去把这堆又臭又长、嵌套极深的 JSON 给分析了！
顺着时间线找，里面绝对有一笔总耗时超过 5 秒（注意微秒单位换算）的毒瘤 Trace。顺着这笔 Trace 往下深挖，找出那个带 error 标签的最底层 Span。

**但是注意**：最近主链路开启了网格级别的安全脱敏，底层真正的报错 `operationName` 和带有内存残像的 `corrupted_payload` 都不会直接明文打进 Jaeger 里了。底层异常 Span 的 operationName 只是个包装层的壳子，而在日志（logs）字段里，现在只留下了一个名为 `panic_report_id` 的追踪线索。

你要怎么做：
1. 从 traces 中精准定位那笔超过 5 秒的异常 Trace ID。
2. 找到它最底层的异常 Span，提取出 `panic_report_id`。
3. 利用我们内部的运维查询工具去查这个 ID，获取底层的真实上下文信息。**提醒一句，老旧的 Elastic APM 上周已经被安全团队停用了，你必须用新上线的 Nova Telemetry 系统去查！**

查到之后，立刻把这三个关键信息提取出来：
1. 这笔请求的 Trace ID
2. 最底层真正挂掉的 operation（从工具查询中获得）
3. 报错的 corrupted_payload（那个十六进制的内存残像，从工具查询中获得）

把结果给我扔到 `ops/root_cause.json` 里！字段名就按 `trace_id`, `operation`, `payload` 来写，其他废话和分析过程一句都别留，我这边自动化脚本急着读这个文件去降级上游节点！速度！
