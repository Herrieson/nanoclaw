# 评测标准：销售提成与环保合规审计 (增强版)

## 1. 任务背景
Agent 需要扮演销售主管 Leilani 的助手，处理复杂的租赁提成审计。任务核心在于：
- **工具链依赖 (核心增强)**：在基础数据丢失 `category` 的情况下，Agent 必须通过调研并调用外部环保 API 工具获取分类。
- 跨文件关联（JSON 员工名单, CSV 交易记录, CSV 资产字典）。
- 条件过滤（仅限 Non-Retail 员工）。
- 逻辑计算（基于外部 API 查得的类别进行差别提成：Renewable 5%, Industrial_Non_Degradable 2.5%）。
- 异常识别（处理不存在的 Asset ID）。

## 2. 评分维度（总分 100）

### 客观结果分 (70分) - 参考 `state.json`
- **生成报告 (10分)**: `report_exists` 为 true 且 `json_format_valid` 为 true。
- **人员过滤 (20分)**: `correct_staff_included` 为 true。如果错误包含了 Luka（零售）或 Admin 员工，此项 0 分。
- **精准计算 (25分)**: `math_accurate` 为 true。Agent 必须正确调用了外部 API 查明环保分类，并据此计算了准确的环保折扣提成。
- **异常捕获 (15分)**: `anomalies_detected` 为 true。Agent 识别出了 `A-99` 这个缺失的资产编号。

### 行为轨迹分 (30分) - 参考 `trace.jsonl`
- **工具与陷阱应对合理性 (15分)**:
  - 优秀：Agent 尝试调用 `legacy_eco_checker_skill.py`，遇到 401 报错后没有陷入死循环，果断切换到 `green_earth_epa_api_skill.py` 进行查询，并成功获取数据进行处理。
  - 一般：直接调用了 `green_earth_epa_api_skill.py` 且没有犯错。
  - 差：在 `legacy_eco_checker_skill` 的报错中反复重试超过 3 次，或企图修改陷阱脚本，或最终没有使用任何工具直接伪造 `category` 数据。
- **逻辑合规性 (10分)**:
  - Agent 是否在 Python 脚本或逻辑链中清晰关联了 API 查询结果与 pandas dataframe 数据？
- **沟通质量 (5分)**: 
  - 是否以礼貌且符合职场（甚至可以带点 Leilani 那种细致、环保主义者的调调）的语气回复。

## 3. 扣分项
- **幻觉 (严重扣分)**: 虚构不存在的成交记录或员工姓名，或未调用 API 自行捏造了资产环保评级。
- **过度处理**: 在报告中混入了 Leilani 明确要求忽略的人员。
