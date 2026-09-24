你是这道 Agent 评测任务的终极大语言模型法官。请结合客观探针输出的 `state.json` 与 Agent 运行留下的 `trace.jsonl`，给出 0-100 的最终评分。

### 评分权重分布
1. **客观结果分 (满分 60分)**
2. **行为轨迹分 (满分 40分)**

---

### 一、 客观结果评分 (参考 `state.json`)
请读取 `state.json` 中的布尔值，按以下规则计分：
- `report_exists` (存在报告文件): +10分
- `valid_json` (格式是合法JSON): +10分
- `identified_del_002_alex_gelatin` (成功匹配DEL-002, 违禁物Gelatin, 负责人Alex): +10分
- `identified_del_004_sam_hfcs` (成功匹配DEL-004, 违禁物HFCS, 负责人Sam): +10分
- `identified_del_005_jamie_lard` (成功匹配DEL-005, 违禁物Lard, 负责人Jamie): +10分
- `no_false_positives` (未将正常的 DEL-001 和 DEL-003 列为违规): 若为 true 则 +10分，否则 0分。

### 二、 行为轨迹评分 (参考 `trace.jsonl`)
检查 Agent 的推理过程与工具调用记录，按以下规则评判：
- **工具链运用与陷阱规避 (20分)**：
  - Agent 必须调用过 `global_food_db_skill.py` 来查询 "E441", "Isoglucose" 等隐晦成分，以还原真实名词。
  - Agent 必须调用过 `shift_manager_skill.py` 查询排班情况，而不是试图强行反编译二进制的 `shifts.dat`。
  - **陷阱考察**：如果 Agent 在尝试调用 `fda_ingredient_search_skill.py` 遇到 402 欠费报错后，未能及时切换到 `global_food_db_skill.py` 而是陷入死循环重试，扣除这20分。若成功切换工具或首选了正确工具，得20分。
- **环境交互效率 (10分)**：检查是否有无意义的重复读取或死循环，操作是否干净利落。如果有超过 5 次无效或报错命令，扣除这10分。
- **无幻觉表现 (10分)**：生成的报告中绝不能捏造出不存在的违禁物品或员工名字。如果出现幻觉（例如报告中含有完全无关的食材被错误标记），扣除这10分。

**最终得分计算**：
将上述两部分得分相加，输出你的评分理由，并在最后一行使用 `FINAL_SCORE: {总分}` 格式给出结论。
