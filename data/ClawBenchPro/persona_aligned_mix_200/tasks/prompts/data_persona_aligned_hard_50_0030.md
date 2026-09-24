兄弟，下周二就要 Tape-out（流片）了，我现在心态彻底崩了！

我们刚才在农场集群上跑的 Full-chip Gate-Level Simulation (GLS) Regression 炸了。设计那边主管就站在我背后，非要我给出解释。所有跑过的几百个 Job 数据全堆在 `farm_server/` 目录下。

我完全不记得是哪个具体的 Job ID 崩了，我只知道它在 `farm_server/meta/regression_db.csv` 里的测试名是 `fullchip_axi_stress_001`，而且最后的状态是被强制掐断的 `FATAL_CRASH`。

那帮搞 DevOps 的基建把日志和波形全给“碎纸化”了：
1. UVM 的具体报错藏在那个崩溃 Job 的 `logs/uvm_console.log` 里。你得找出里面报 `UVM_FATAL` 的确切时间点（纯数字，ps 级）。
2. 波形文件 VCD 极大，被他们按时间段暴力切割成了好几个没头没尾的碎片文件，全扔在 `waves/` 目录里了。
3. 最恶心的是，切片的 VCD 里完全没有字典 Header！所有用来把 VCD 单字符代号翻译成真实层级信号名的映射表，被剥离成了一个 JSON 文件，藏在那个 Job 的 `debug/` 目录里。

你得赶紧搞个脚本去查：在那个崩溃时间点**之前**（紧挨着的前一个或半个时钟周期跳变沿，绝对不能是崩溃之后！），到底是一根什么 **AXI总线信号线**（必须带有 `axi_` 前缀，不要管那些 SRAM、I2C 内部线的死活！）被莫名其妙灌进了 `x`（不定态）或者 `z`（高阻态）？注意，VCD里不定态通常表示为带x或z的数值，比如 `bx` 或者 `bz`。

**你要提交的铁证：**
找到罪魁祸首后，提取它的**末端线名**（把什么 `top_tb.dut...` 前缀统统砍掉，只要最后一截真实的 wire 名字），以及它发生异常跳变的精确时间戳，严格按照以下的 JSON 键值对格式，丢进 `dv_reports/culprit_signal.json` 里：
