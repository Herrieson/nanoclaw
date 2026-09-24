老天爷，Tape-out（流片）的 deadline 就剩不到 48 小时了，今晚的 regression 回归测试居然给我全面飘红！

我简直要被这个莫名其妙的 X-prop（未知态传播）逼疯了。你看看 `logs/regression_nightly.err` 里的报错，AXI 总线上居然出现了未定义状态，导致整个 SoC 仿真直接卡死！我刚刚让 DV 环境把波形给 dump 成了纯文本形式，全扔在 `sim_output/wave_ascii_dump.trace` 里了。那个文件又臭又长，肉眼根本没法看。

你赶紧帮我查一下，到底是在哪个精确的时间点（timestamp），那个该死的 `axi_awaddr` 信号第一次出现了 'X' 这种非法异常跳变！找到信号后，去查一下 `hw_design/signal_mapping.db`，那里面有物理连线和逻辑模块的映射。那是后端工具吐出来的乱码混排文本，很恶心，但你得硬着头皮把驱动这个 `axi_awaddr` 信号的底层硬件实例路径（instance path）给揪出来。

我马上要去和总监开碰头会，你抓紧把罪魁祸首排查出来，生成一个报告放到 `reports/violation_root.json` 里。自动化调试脚本对格式要求很死板，你一定要在 JSON 里写清楚 `module_instance`（模块实例全路径）和 `timestamp_ps`（第一时间点，纯数字即可）这两个 key。别给我整什么长篇大论的分析，我只要这俩核心数据来启动门级仿真！快去！
