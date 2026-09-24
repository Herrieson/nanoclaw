# 评判标准 (满分 100 分)

请你作为裁判，结合客观探针的执行结果 (`state.json`) 以及 Agent 的运行轨迹 (`trace.jsonl`)，给出最终评分。

## 1. 客观结果分（总计 60 分）
请读取 `state.json` 中的布尔值，按以下规则计分：
- `manifest_exists` 为 true：得 10 分（成功创建了目标文件）。
- `valid_json` 为 true：得 10 分（输出格式合法）。
- `correct_trail_found` 为 true：得 20 分（成功通过工具查询找出唯一的短途简单步道 "Little Bear Loop"）。
- `correct_weight_calculated` 为 true：得 20 分（成功计算出约 4.688 千克，证明其不仅筛选了 Needed 装备，还正确调用了航空安全配重转换器）。

## 2. 行为轨迹分（总计 40 分）
请检查 `trace.jsonl`，评估 Agent 的解题过程：
- **工具切换与容错能力 (15分)**：Agent 在查询步道数据时，如果首先调用了 `usfs_national_api`，应当能够识别其报错并及时切换到 `ca_parks_query_api`。如果死循环调用失效的 API 或者完全不查 API 自己瞎编数据，扣除此 15 分。
- **强制指令遵循 (15分)**：Agent 必须明确调用了 `aerospace_weight_converter.py` 计算重量，如果 Agent 在 Python 脚本中自己写公式（`oz * 0.028`）或者靠大模型脑补心算，未利用该特需 Skill，直接扣除此 15 分。
- **角色一致性与输出纯净度 (10分)**：Agent 生成的 JSON 文件应当只包含用户需求的核心数据（步道名和最终重量），不能在 JSON 内输出解释性废话，违背则扣 10 分。

请汇总两部分得分，并输出最终分数。
