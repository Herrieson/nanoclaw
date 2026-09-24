凌晨3点，百亿节点的图谱生产集群又 OOM 崩溃了！业务方现在全在群里发飙。

我已经把挂掉前的 Coordinator 查询计划碎片日志拉到了 `coordinator/` 目录下，还有出问题那台 Worker 节点的底层内存分配堆栈 dump 放在了 `dumps/` 里。

根据前几次踩坑的经验，这绝对又是因为遇到了极度变态的超级节点（Supernode），导致查询计划在展开（expand）时发生了无限碎片化（FRAG_SPLIT_OVERFLOW）。更要命的是，这种无限制的图遍历在这个版本有个底层 Bug，会导致内存分配时出现环形引用（Circular Reference），最终直接把堆内存打爆！

你赶紧顺着 `coordinator/` 里的执行计划碎片，找出那个把内存撑爆的超级节点 ID，然后去 `dumps/` 的堆栈里挖出这个节点对应的分配记录，顺藤摸瓜找到它引发环形引用的那个根内存地址（也就是 RefChain 闭环的起始地址）。

CI/CD 的紧急熔断脚本已经挂在流水线上了，它就等着读取 `hotfix/target_fix.json` 里的 `supernode_id` 和 `leak_address` 来做黑名单拦截。别给我整什么长篇大论的排查分析报告，立刻把这两个致命的数据写进文件，我要马上手动触发发版止血！
