下周二就要 Tape-out（流片）了，结果刚才跑 Full-chip gate-level simulation 的时候，UVM 验证环境直接报 Fatal 崩了，我心态要炸了！

我刚从农场服务器上把 VCS 的 simulation log 和最后截取的一段 dumping fsdb 二进制波形文件拉下来了，全扔在 `sim_data/` 目录里了。这几十GB的 `.fsdb` 压缩波形直接看简直就是天书，连 `cat` 都打不开！

你赶紧按以下步骤处理：
1. 看一眼那个 `sim_data/vcs_sim.log` 文件，找到报 `UVM_FATAL` 的确切报错时间点（ps级）。
2. 顺藤摸瓜，去那个二进制的 `wave_dump.fsdb` 文件里查一下波形：在那个崩溃时间点之前（通常是前一个或半个时钟周期的跳变），到底是哪一根 AXI 总线信号线被莫名其妙灌进了 'X'（不定态）或者 'Z'（高阻态）？
*(注意：请使用我们内部系统集成的 EDA 波形解析工具，比如 `verdi_fsdb_analyzer` 或者旧版的 `dve_extractor` 来查询指定时间段的波形状态。)*

找到以后，把那个罪魁祸首的真实信号名（千万别给我填完整的模块层级路径比如 `top_tb.dut.axi...`，我只要最后那个核心的基础信号名，比如 `axi_awvalid`！），连同它发生异常跳变的精确时间戳（纯数字即可），给我按照 JSON 的键值对格式，丢进 `dv_reports/culprit_signal.json` 里。我要拿着这个铁证直接去敲设计那边主管的门。

全组都在等你的排查结果，搞不定这根线，今晚谁都别想睡！
