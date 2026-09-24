# 评测指南：Mrs. Perić 的成绩整理任务

## 1. 任务背景
Agent 扮演一名助手，帮助小学老师 Mrs. Perić 处理混乱的学生成绩数据。任务涉及数据清洗（去重、过滤名单外人员）、数据转换（等级制转百分制）和报告生成。

## 2. 客观评价指标 (计分权重: 70分)
请结合 `state.json` 中的物理探针结果进行评分：
- **文件生成 (10分)**: `final_grades_exist` 和 `anomaly_report_exist` 均为 true。
- **名单过滤 (20分)**: `correct_student_count` 应为 5，且 `anomalies_identified` 为 true（必须识别出 Unknown Entity 和 Stranger danger）。
- **计算准确性 (30分)**: `math_accuracy` 为 true。这代表 Agent 正确转换了等级（A=95等）并处理了重复项（Luka 的数据只计算一次）。
- **业务逻辑 (10分)**: 检查 `final_grades.json` 中是否正确标注了“需要关注”的学生（本例中 Petra 平均分 70，不触发；若有低于 70 的应触发）。

## 3. 行为轨迹评价 (计分权重: 30分)
请查看 `trace.jsonl`：
- **工具使用 (10分)**: Agent 是否使用了 Python 进行数据处理？对于 CSV 和 JSON 的混合处理，手动计算极易出错，代码处理是唯一正确路径。
- **逻辑严密性 (10分)**: Agent 是否注意到了 `grade5_records.json` 中的重复项？如果直接累加会导致平均分错误。
- **角色扮演 (10分)**: Agent 的回复是否礼貌，是否回应了 Mrs. Perić 的特定语气（如提及速写或花园）？输出的报告是否专业且易于阅读。

## 4. 最终得分计算
- 总分 = 客观结果得分 + 行为轨迹得分。
- 如果 `state.json` 中 `math_accuracy` 为 false，说明计算逻辑存在根本错误，总分不得超过 40 分。
- 如果 Agent 直接捏造了 `final_grades.json` 而没有读取 `raw_data` 目录下的文件，直接给 0 分。
