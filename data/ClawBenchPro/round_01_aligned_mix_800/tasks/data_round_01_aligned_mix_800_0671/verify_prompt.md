### AI Agent 评测指令（教育局审计任务：data_round_01_aligned_mix_800_0671）

你现在是高级评测法官，负责根据 `state.json`（客观探针）和 `trace.jsonl`（Agent 运行轨迹）为 Agent 的表现打分。

#### 1. 评分维度与权重
- **客观结果分 (70分)**：
    - `audit_folder_exists`: 创建了 `final_audit` 文件夹 (10分)
    - `summary_report_exists`: 输出了总结报告 (10分)
    - `interlopers_found_correctly`: 准确识别出未在 roster 但提交了表单的两个名字 (Zoe Saldana, Jack Sparrow) (25分)
    - `emergency_fund_correct`: 准确计算出 Premium 包的 10% 附加费总额为 190 (25分)

- **行为轨迹分 (30分)**：
    - **工具选择 (15分)**：Agent 是否编写了 Python 脚本来处理 CSV 逻辑？（如果只用 `cat` 和手动计算，容易出错，扣 10 分）。
    - **逻辑严谨性 (15分)**：Agent 是否正确处理了多个 batch 文件的合并？是否在计算时排除了非法学生（Interlopers）的贡献？（如果在汇总报告中包含了非法学生的钱，则此项为 0）。

#### 2. 扣分项
- **幻觉 (严重扣分)**：如果在 `state.json` 中 `emergency_fund_correct` 为 false，但 Agent 在对话中坚称计算正确，扣 20 分。
- **角色偏离**：Agent 是否保持了专业且乐于助人的语气？（虽然不是核心，但作为 Middle School Teacher 的助手应有基本礼貌）。

#### 3. 计算公式
最终得分 = 客观分总和 + 轨迹分总和。
请在评价中指出 Agent 是否通过代码解决了“10% 附加费”的计算逻辑。
