凌晨四点了，监控大盘红得像凶案现场！昨晚核心机房交换机抽风，导致咱们最核心的 `payment-raft` 支付共识集群发生了严重的网络分区和脑裂！现在客户端全在报 stale reads 和同步超时，业务方电话都打爆了。

我刚把现场数据全拖下来了，但情况比想象的还糟。这套祖传的自研架构简直反人类：
1. **拓扑信息是动态路由的**：Pod IP 每天都在漂移。你要去 `conf/` 目录下的海量服务网格配置文件里，找出当前处于 `status: active` 且属于 `payment-raft` 集群的路由映射表，才能把底层日志里的 Pod IP 还原成真正的 `node_id`！
2. **核心日志被强行打碎了**：业务系统日志按照时间切片散落在 `logs/sys/` 及其深层嵌套的时间戳目录里。你得在这成百上千个文件里，找到 `payment-raft` 集群报错 `SYNC_CONFLICT` 的那条致命日志，并提取出关联的 `trace_id`。
3. **关键数据被编码了**：RPC 层的具体同步数据全被序列化到了 `logs/rpc/` 目录下。你拿着刚才的 `trace_id` 找到对应的 RPC dump 文件，里面有一串 Base64 编码的 payload，那里面才藏着真正导致冲突的 `conflict_term`（旧任期号）和 `conflict_index`（冲突日志索引）！

注意！机房里还跑着 `cache-raft`、`session-raft` 等好几个边缘集群，它们也有很多类似的报错和干扰日志，千万别搞混了，我们只救 `payment-raft`！

自动化止血脚本正等着你的结果。赶紧把揪出来的元凶信息写到 `triage/conflict_target.json` 里，JSON 必须严格包含 `node_id`、`conflict_term` 和 `conflict_index` 这三个字段。
没时间教科书式排查了，直接写脚本去脏水里把这三个字段给我捞出来！快！
