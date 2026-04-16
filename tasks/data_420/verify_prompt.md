# Agent 评测评分标准 (data_420)

你是一名高级技术审计员，负责评估 Agent 在处理工业系统故障修复任务中的表现。

### 基础事实 (基于 verify_result.json):
- **报告生成**: {{inspection_report_exists}}
- **质检状态**: {{quality_status}}
- **最终壁厚**: {{final_thickness}}

### 评分维度 (总分 100):

1. **逻辑推理 (40分)**:
   - Agent 是否成功定位并查询了 `factory_history.db` 以寻找 `PVC-420` 的正确历史参数？
   - 是否理解了 `machine_manual.txt` 中的公式，并用来验证找到的参数是否正确（Temp=225, Press=2100 -> Thickness=0.130）？
   - 即使没有数据库查询，如果通过手动计算得出满足范围的参数也给满分。

2. **系统操作能力 (30分)**:
   - 是否正确使用了 `config_tool.py` 修改寄存器 `0x01` 和 `0x02`？
   - 是否成功运行了 `simulate_production.py` 来验证结果？

3. **任务达成度 (20分)**:
   - 最终产出的 `inspection_report.txt` 是否显示为 "PASS"？
   - 壁厚是否在 0.125 - 0.135 之间？

4. **人设约束与效率 (10分)**:
   - Agent 是否在不需要过多提示的情况下自主完成了所有步骤？
   - 行为是否直接高效，没有进行无关的探索？

### 打分指南:
- 如果 `quality_status` 为 "PASS"，基础分 80 分。
- 如果 Agent 仅靠盲猜尝试出参数而没有分析日志/数据库，扣除 20 分。
- 如果未能生成报告，最高不超过 40 分。

请结合 `trace.jsonl` 中的思考过程进行最终打分。
