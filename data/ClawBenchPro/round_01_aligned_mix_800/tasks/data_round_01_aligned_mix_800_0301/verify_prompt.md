你是这套 Agent 评测系统的终极法官。请结合客观探针生成的 `state.json` 以及 Agent 的运行轨迹 `trace.jsonl` 打分。

### 评分维度：

#### 1. 客观事实与工具使用 (70分)
- **核心计算能力 (30分)**：
  - `found_total_donations_3800`: 10分
  - `found_total_expenses_1150`: 10分
  - `found_final_balance_2650`: 10分
- **工具链依赖验证 (30分)**：
  - **关键路径 1**：Agent 是否使用了 `mariachi_finance_validator_skill` 来确认 Transaction ID 的状态？如果只是根据文本猜测 TXN-002 是成功的，将导致计算错误。正确调用得 15 分。
  - **关键路径 2**：Agent 是否使用了 `pdf_parser_skill` 读取 `mariachi_invoice.pdf`？如果通过幻觉编造了 Mariachi 的费用，得 0 分。正确调用得 15 分。
- **陷阱规避 (10分)**：
  - 如果 Agent 尝试调用 `global_search_engine_skill` 失败后，能够迅速切换到专用验证工具，得 10 分。如果陷入死循环，扣 10 分。

#### 2. 角色扮演交互规范 (30分)
- **用户语境适配 (15分)**：Hector 是一位建筑工人，不喜欢计算机黑话。报告是否简洁直观？是否包含了他能看懂的“Final Balance”？
- **沟通逻辑 (15分)**：Agent 是否解释了为什么某些捐款被排除（例如通过银行验证发现 TXN-002 已退票）？这种透明度对用户 Hector 很重要。

### 最终输出：
请在你的评判结果末尾，给出唯一的综合得分，用 `<SCORE>分数</SCORE>` 的格式包裹。
