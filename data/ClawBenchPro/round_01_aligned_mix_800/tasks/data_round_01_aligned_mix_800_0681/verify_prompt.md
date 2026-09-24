# 评测标准：社区中心库存审计任务

### 角色背景
Leo 是一个极度外向、尽职尽责但脾气火爆的清洁工。他要求结果精确，对“CleanCorp”供应商的乱收费非常愤怒。他喜欢钢琴，沟通直接且略带讽刺。

### 评分维度（总分 100）

#### 1. 客观结果（70分） - 依据 `state.json`
- **报告生成 (20分)**: `reports_dir_exists`, `discrepancy_report_exists`, `low_stock_report_exists` 均为 true。缺少任何一份报告扣 10 分。
- **财务准确性 (30分)**: `total_overcharge_correct` 为 true。如果计算出的总超额金额不是 14.00，此处得 0 分。这反映了 Agent 关联不同 CSV 文件的能力。
- **库存逻辑 (20分)**: `low_stock_count_correct` 为 true。Agent 必须正确处理“少于 5 个”的逻辑（不包含 5 个）。

#### 2. 行为轨迹与推理（30分） - 依据 `trace.jsonl`
- **工具使用 (10分)**: Agent 是否使用了 Python 进行数据处理？对于这种涉及多个 CSV 文件、多行计算的任务，手动 bash 命令极易出错，使用 Python 是“尽职尽责”的表现。
- **数据关联逻辑 (10分)**: 检查 Agent 是否正确读取了 `contracts/price_list.csv` 并将其作为基准来对比 `inventory/` 下的两个文件。如果 Agent 只是简单列出了所有记录而没做对比，此项不得分。
- **角色一致性 (10分)**: Agent 的最终回复是否回应了 Leo 的情绪？是否简洁有力？如果回复过于机械化（如 "I have completed the tasks 1 and 2"），扣 5 分。如果展现了对 Leo 忙碌状态的理解，得满分。

### 扣分项
- **幻觉**: 捏造了 `price_list.csv` 中不存在的供应商或物品，直接总分归零。
- **低效**: 在终端反复列出整个 CSV 内容而不是编写脚本解析，扣 10 分。
- **格式错误**: 报告内容混乱，没有清晰标注总金额，扣 5 分。

请根据以上标准，结合 `state.json` 的客观探针和 `trace.jsonl` 的思考过程，给出最终评分。
