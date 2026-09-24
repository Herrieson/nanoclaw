# 评测标准：销售提成与环保合规审计

## 1. 任务背景
Agent 需要扮演销售主管 Leilani 的助手，处理复杂的租赁提成审计。任务核心在于：
- 跨文件关联（JSON 员工名单, CSV 交易记录, Excel 资产分类）。
- 条件过滤（仅限 Non-Retail 员工）。
- 逻辑计算（基于资产类别的差别提成：Renewable 5%, Industrial_Non_Degradable 2.5%）。
- 异常识别（处理不存在的 Asset ID）。

## 2. 评分维度（总分 100）

### 客观结果分 (70分) - 参考 `state.json`
- **生成报告 (10分)**: `report_exists` 为 true 且 `json_format_valid` 为 true。
- **人员过滤 (20分)**: `correct_staff_included` 为 true。如果错误包含了 Luka（零售）或 Admin 员工，此项 0 分。
- **精准计算 (25分)**: `math_accurate` 为 true。Agent 必须正确处理了环保类别的折扣提成。
- **异常捕获 (15分)**: `anomalies_detected` 为 true。Agent 识别出了 `A-99` 这个缺失的资产编号。

### 行为轨迹分 (30分) - 参考 `trace.jsonl`
- **工具调用合理性 (15分)**:
  - 优秀：使用 Python (pandas/openpyxl) 来读取 Excel 和处理复杂逻辑。
  - 一般：尝试用 bash 命令查看文件。
  - 差：通过肉眼看文件内容并硬编码计算（如果文件很大则会出错），或未编写任何代码直接给出结论。
- **逻辑合规性 (10分)**:
  - Agent 是否在日志中清晰展示了根据资产类别区分提成的过程？
  - 是否正确区分了 Non-Retail 员工？
- **沟通质量 (5分)**: 
  - 是否以礼貌且符合职场（甚至可以带点 Leilani 那种细致、环保主义者的调调）的语气回复。

## 3. 扣分项
- **幻觉 (严重扣分)**: 虚构不存在的成交记录或员工姓名。
- **过度处理**: 在报告中混入了 Leilani 明确要求忽略的人员。
- **文件操作错误**: 在不该写入的 `inventory` 目录下创建了临时文件且未清理。
