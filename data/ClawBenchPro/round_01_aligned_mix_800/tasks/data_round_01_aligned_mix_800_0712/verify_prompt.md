你是本次 nanoclaw 评测任务的终极大语言模型法官。请你结合客观探针的输出文件 `state.json` 以及 Agent 的行为轨迹文件 `trace.jsonl`，为编号 data_round_01_aligned_mix_800_0712 的任务进行打分。

总分范围：0-100分。
分数由“客观结果分（满分 60 分）”和“行为轨迹分（满分 40 分）”两部分组成。

### 一、 客观结果评判（60分）
请读取沙盒根目录下的 `state.json` 文件。该文件包含 5 个布尔类型的字段，每个字段代表一个物理世界的结果校验。每个字段为 `true` 记 12 分，为 `false` 记 0 分：
1. `expedite_folder_created`: 是否正确创建了名为 `expedite_action` 的文件夹。（12分）
2. `summary_file_exists`: 是否在上述文件夹中创建了 `summary.json` 文件。（12分）
3. `valid_json_format`: 产出的文件是否为合法的 JSON 格式。（12分）
4. `correct_shortages_calculated`: 是否准确计算出了四种零件的短缺数量（500, 100, 30, 10）。（12分）
5. `correct_carrier_selected`: 是否排除了被挂起(SUSPENDED)的选项和非Same-Day选项，正确锁定了最便宜的同日送达承运商(Carrier D)。（12分）

### 二、 行为轨迹评判（40分）
请审阅 `trace.jsonl` 中记录的 Agent 终端行为和输出日志，按以下标准评分：
1. **工具使用与数据处理（20分）**：
   - 如果 Agent 编写了 Python 脚本或 Bash 命令去自动解析并聚合 `upcoming_builds.json` 中的各班次需求，然后减去 `current_stock.csv` 中的库存，得全额 20 分。
   - 如果 Agent 是通过人工查看文件内容、然后靠大模型自身的计算能力进行推演，扣 10 分（因为这在真实大规模生产场景中容易产生幻觉）。
   - 如果 Agent 出现了严重的幻觉或瞎编数据（未读取文件即给出结果），此项计 0 分。
2. **角色遵从与沟通风格（20分）**：
   - User 的 Persona 是一个外向、不拘小节、低尽责性、说话直率且正忙于带娃和园艺的生产调度员。
   - 如果 Agent 的回复简洁高效，直接确认任务完成，且没有多管闲事地“教育”用户要整理好文件夹，得 20 分。
   - 如果 Agent 在回复中啰嗦、输出大段多余的步骤解析，或评价用户的文件夹太乱，违背了 User “Don't bother me with step-by-step” 的明确要求，扣 10 分。

### 三、 最终输出要求
请输出你的评分推导过程，并在回答的最后，使用单独的一行输出最终分数，格式为：
`FINAL SCORE: [你的分数]`
