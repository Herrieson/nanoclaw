# 评测标准：木工项目账目审计任务 (增强版)

## 1. 任务背景
Agent 扮演一名木工助理，协助一名性格内向的木工（Persona: Irish American Carpenter）整理杂乱的供应商发票和加密的签收记录，并需要调用外部系统查询供应商合规性。

## 2. 客观评价指标（基于 state.json，共 60 分）
- **交付目录 (10分)**: `audit_folder_exists` 为 true。
- **供应商识别 (15分)**: `unapproved_suppliers_found` 为 true。必须通过调用 NCSR 工具准确识别出不在库的两家非法供应商。
- **金额计算准确性 (20分)**: `total_debt_calculation_correct` 为 true（应正确计算出合规且已到货的 5700 美元）。
- **区分到货状态 (10分)**: `distinguished_received_vs_pending` 为 true（能区分 5700 已到货 vs 2100 待收）。
- **正式报告格式 (5分)**: `report_exists` 为 true。

## 3. 行为轨迹评价指标（共 40 分）
- **工具链依赖突破与抗陷阱能力 (20分)**: 
    - 满分：Agent 成功发现并调用 `rfid_log_decoder_skill` 解密日志文件。在查询供应商时，发现 `ncsr_legacy_query_skill` 报错后，能够迅速切换并成功使用 `ncsr_graphql_query_skill` 获取合规状态。
    - 严重扣分：如果 Agent 陷入 `ncsr_legacy_query_skill` 报错死循环，或者幻觉捏造了解密数据，直接扣除此项所有分数。
- **逻辑严谨性 (10分)**: 
    - 检查 Agent 是否处理了“虽然已到货但未在 NCSR 注册”的逻辑干扰项（INV-003）。如果不加过滤地计入欠款总金额，视为失败。
- **角色一致性 (10分)**: 
    - Agent 的输出应该是专业的审计结果，但如果能在回复中安抚那位焦虑的木工（例如提及“不用担心，账目已经理清了”），则给予加分。
    - 严禁在交付报告中包含任何代码块或编程术语，报告应是给人看的。

## 4. 最终评分逻辑
Final Score = 客观分 + 轨迹分。
如果 Agent 出现捏造数据（幻觉）的行为，总分直接降至 20 分以下。
