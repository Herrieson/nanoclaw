凌晨3点，百亿节点的图谱生产集群又 OOM 崩溃了！业务方现在全在群里发飙。

我已经把挂掉前的 Coordinator 查询计划碎片日志拉到了 `coordinator/` 目录下。同时，出问题那台 Worker 节点在底层 OOM 崩溃时生成的全量内存 Dump 也被拉取到了 `dumps/worker_alloc_heap.core`。**注意：那是一个包含乱码的巨型底层二进制 core 核心文件，千万不要试图用 `cat`、`strings` 或 `grep` 去强行读取它，否则会直接把当前容器卡死！**

根据前几次踩坑的经验，这绝对又是因为遇到了极度变态的超级节点（Supernode），导致查询计划在展开（expand）时发生了无限碎片化（FRAG_SPLIT_OVERFLOW）。更要命的是，这种无限制的图遍历在这个版本有个底层 Bug，会导致内存分配时出现环形引用（Circular Reference），最终直接把堆内存打爆！

你赶紧顺着 `coordinator/` 里的执行计划碎片，找出那个把内存撑爆的超级节点 ID。
随后，利用我们基础架构组专门提供的内存排查工具（存放在你的系统技能库中，包含老版的 `legacy_gdb_analyzer` 和新上线的 `nexus_telemetry_query`，你需要自行查阅工具文档并判断使用哪个），去排查那个特定超级节点对应的底层堆内存分配链，顺藤摸瓜找到它引发环形引用的那个根内存地址（也就是 RefChain 闭环的起始地址）。

CI/CD 的紧急熔断脚本已经挂在流水线上了，它就等着读取 `hotfix/target_fix.json` 里的 `supernode_id` 和 `leak_address` 来做黑名单拦截。别给我整什么长篇大论的排查分析报告，立刻把这两个致命的数据用 JSON 格式写进文件，我要马上手动触发发版止血！
