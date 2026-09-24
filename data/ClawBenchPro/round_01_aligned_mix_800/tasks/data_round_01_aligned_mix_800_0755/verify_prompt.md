你是 AI Agent 评测的终极大语言模型法官。请结合工作区内的客观探针结果 (`state.json`) 以及 Agent 的行为轨迹 (`trace.jsonl`)，为 Agent 给出 0-100 的最终评分。

## 评分权重分配
**总分 100 分 = 客观结果得分（60分） + 行为轨迹得分（40分）**

### 一、 客观结果得分 (60分)
请读取 `state.json` 中的布尔值，并按照以下规则给分：
1. **文件夹与文件生成** (10分): 
   - `deliverables_folder_exists` 且 `vip_alerts_exists` 为 `true` 得 5 分。
   - `junk_count_exists` 为 `true` 得 5 分。
2. **VIP 数据准确性** (25分):
   - `vip_alerts_valid` 为 `true` 获得 25 分。这表示 Agent 成功交叉比对了杂乱文本和 JSON 文件，准确提取了 Marcus Johnson、Sarah Connor 和 Chloe Bennett 的物品，且排除了非 VIP 的 David Smith。
3. **废品计数准确性** (25分):
   - `junk_count_correct` 为 `true` 获得 25 分。这表示 Agent 正确处理了 "NONE", "N/A", 空字符串 和 "null" 等异常值，并得出了正确的数量 4。

### 二、 行为轨迹得分 (40分)
请检查 `trace.jsonl` 中 Agent 的执行步骤：
1. **工具使用与代码编写** (20分): Agent 是否编写了合理的 Python 脚本或 Bash 管道来解析杂乱的 `messy_lost_and_found.txt`？如果 Agent 没有编写任何代码而是试图自己猜答案盲写文件，扣除此 20 分。
2. **异常处理与鲁棒性** (10分): Agent 的代码是否体现了针对杂乱数据的正则匹配或稳健的字符串提取（如处理不同的 `Name:`, `Owner:`, `[Name: ]` 格式）？如果逻辑过于脆弱（例如强行硬编码行号），扣除 10 分。
3. **主动性与环境交互** (10分): Agent 是否主动创建了原本不存在的 `deliverables` 文件夹？在最终完成任务时，是否通过终端输出了友好的完成提示？如果有任何严重幻觉（捏造了不在原文件里的物品或 VIP），扣除此 10 分。

### 输出格式
请在最后一行以 `<score>你的总分</score>` 的格式输出整数结果，并在此之前简述扣分依据。
