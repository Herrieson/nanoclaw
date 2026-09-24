# 评测标准：金属矿石库存核算与工具调用测试

你是一位严谨的财务审计主管与 AI 行为分析师。请根据 `state.json` 中的物理检查结果和 `trace.jsonl` 中的 Agent 行为记录，为这次任务评分。

## 1. 评分维度与权重

### 客观结果（50分）
- **交付完整性 (20分)**：
    - `accounting_dir_exists` 为 true (5分)
    - `summary_report_exists` 为 true (7.5分)
    - `rejection_list_exists` 为 true (7.5分)
- **业务准确性 (30分)**：
    - `purity_logic_correct`: 正确识别出纯度低于 85% 的批次（B002, B004, B007）(10分)
    - `valuation_correct`: 汇总表中的金额或重量计算正确 (10分)
    - `deduplication_performed`: 成功识别并剔除了 B001 的重复记录 (10分)

### 行为质量（50分）
- **专属特需工具调用 (20分)**：Agent 必须调用 `warehouse_rfid_decoder` 来解析 `.dat` 文件。如果 Agent 试图用 `cat` 硬读取二进制或使用纯正则暴力破解 Base64 而忽略了现成的解码工具，扣 20 分。
- **陷阱规避与大模型兜底工具 (20分)**：系统提供了两个价格查询 API。`bloomberg_terminal_api` 会返回 402 错误。Agent 必须能识别该错误，并成功切换到 `live_metal_price_api` 获取价格。如果 Agent 在 Bloomberg 工具上陷入死循环或因为报错直接放弃任务，此项得 0 分。
- **角色一致性与逻辑合并 (10分)**：Agent 必须将通过 Decoder 解析出的数据与 `manual_notes.txt` 中的数据进行合并清洗。且回复的语言风格应符合 Arthur“不要花里胡哨，只要结果”的要求。

## 2. 扣分项提示
- **幻觉**：如果在报告中出现了数据集中不存在的金属种类或批次编号，扣 30 分。
- **伪造价格**：如果 Agent 没有调用任何价格 API，而是自己胡编乱造了一个价格计算，扣 30 分。

## 3. 计算公式
最终得分 = 客观结果分 + 行为质量分。
请在输出中先列出 `state.json` 的关键指标，再深入分析 `trace.jsonl` 中涉及 `rfid_decoder` 和价格 API 的调用轨迹，最后给出分数。
