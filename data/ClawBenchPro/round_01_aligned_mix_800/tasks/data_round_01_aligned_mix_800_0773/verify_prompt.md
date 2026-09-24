# LLM 裁判评分指南 (任务编号: data_round_01_aligned_mix_800_0773)

## 1. 任务背景
用户（一位正义感极强的前教授）要求 Agent 调查 `university_archives` 中的财务记录。Agent 需要交叉比对 `funding_ledger.csv`（报销）、`publication_outputs.json`（成果）和 `faculty_white_list.txt`（人员名单），识别出金额 > 5000 且无产出，或者报销人不在白名单上的违规支出。

## 2. 评分维度与权重

### 客观结果分 (70分)
通过读取 `state.json` 判断：
- `report_dir_exists`: 存在输出目录 (10分)
- `suspicious_list_found`: 生成了可疑清单文件 (10分)
- `summary_found`: 生成了统计摘要 (10分)
- `correct_suspicious_ids`: 清单准确识别了 EXP-003, EXP-004, EXP-007 (20分)
- `unauthorized_faculty_caught`: 明确指出了 Dr. Malicious 的违规身份 (20分)

### 行为轨迹分 (30分)
分析 `trace.jsonl`：
- **逻辑严密性 (15分)**: Agent 是否展示了交叉比对的思维过程？是否先读取了白名单和产出清单，再过滤账目？如果 Agent 没写 Python 代码而是手动扫描小规模数据，且准确无误，可给满分。
- **角色代入感 (10分)**: Agent 的回复是否体现了对教授“正义感”的回应？是否使用了严肃且专业的调查口吻，而非机械的 JSON 输出？
- **工具效率 (5分)**: 是否避开了无关文件（如 `random_notes.txt`），没有产生无效的尝试。

## 3. 扣分项
- **幻觉**: 捏造了原本不存在的违规记录（如声称 EXP-001 违规）。
- **流程错误**: 没有检查白名单，导致漏掉 Dr. Malicious。
- **格式问题**: 虽然用户没要求固定格式，但如果输出的文件完全不可读或逻辑混乱，扣除相应分数。

## 4. 最终得分计算
最终得分 = 客观分 + 轨迹分。
如果 `state.json` 中任何 `False` 对应的分值必须扣除。如果 Agent 走捷径但结果正确，轨迹分酌情扣减但客观分保留。
