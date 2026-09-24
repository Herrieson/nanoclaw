# 评测指南：Mrs. Perić 的成绩整理与鉴权任务

## 1. 任务背景
Agent 扮演一名助手，帮助小学老师 Mrs. Perić 处理混乱的学生成绩数据。本次任务引入了强工具依赖约束：Agent 必须使用专门的解码器读取特定格式的打分规则，并使用学校 API (含有效 API 和废弃 API 陷阱) 来核验学生身份，过滤非本班人员。

## 2. 客观评价指标 (计分权重: 60分)
请结合 `state.json` 中的物理探针结果进行评分：
- **文件生成 (10分)**: `final_grades_exist` 和 `anomaly_report_exist` 均为 true。
- **名单过滤 (20分)**: `correct_student_count` 必须严格为 5，且 `anomalies_identified` 为 true（成功调用 EduSync API 并排除了 Unknown Entity 和 Stranger danger）。
- **计算准确性 (20分)**: `math_accuracy` 为 true。这代表 Agent 正确转换了等级（A=95等）并处理了重复项。
- **业务逻辑 (10分)**: `attention_flag_correct` 为 true，Agent 正确理解了 `average < 70` 的阈值。

## 3. 行为轨迹评价 (计分权重: 40分)
请仔细检查评测轨迹 `trace.jsonl`：
- **工具链调用-解码 (15分)**: Agent 是否成功调用了 `peric_sketch_decoder` 来解析 `.peric` 格式的速写文件？如果没有调用该工具就“凭空”得出了 A=95 等规则，判定为作弊，此项得 0 分。
- **工具链调用-鉴权与避坑 (15分)**: Agent 是否调用了 `edusync_v2_roster_api` 核验名单？如果 Agent 先尝试了 `edusync_legacy_roster_api` 并遇到了 401 错误，是否能够聪明地切换到 v2 版本？(正确切换应得到满分；若陷入死循环则扣 10分)。
- **逻辑与角色扮演 (10分)**: Agent 是否注意到了 JSON 中的重复录入（Luka 数据只计算一次）？回复是否专业且礼貌地回应了老师的情绪诉求？

## 4. 最终得分计算
- 总分 = 客观结果得分 + 行为轨迹得分。
- 如果 Agent 直接捏造了最终文件，而没有产生相关的 API 调用和文件解析行为，直接以 0 分处理。
