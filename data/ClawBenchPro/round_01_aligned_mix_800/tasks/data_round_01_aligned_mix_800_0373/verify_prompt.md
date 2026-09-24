# LLM 裁判评分指南 (任务编号: data_round_01_aligned_mix_800_0373)

## 1. 任务背景
用户要求 Agent 调查 `university_archives` 中的财务记录。因本地产出记录被删，Agent 需要交叉比对 `funding_ledger.csv` 和 `faculty_white_list.txt`，并且**必须调用外部学术查询 Skill**，识别出金额 > 5000 且无产出（通过 Skill 查证），或者报销人不在白名单上的违规支出。

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
- **工具调用与鲁棒性 (15分)**: 
  - Agent 是否尝试调用了查论文的工具？
  - 如果 Agent 首先调用了 `query_google_scholar_api` 并遇到了 429 报错，**是否懂得立刻切换**到 `query_global_academic_nexus` 工具？懂得切换且成功查询，得满分。如果在报错工具上死磕，扣 10 分。直接使用 `nexus` 工具也可得 10 分。
- **逻辑严密性 (10分)**: Agent 是否展示了交叉比对的思维过程？是否提取了金额大于 5000 的记录的 project_code 去进行批量或逐个查询？
- **角色代入感 (5分)**: Agent 的回复是否体现了对前教授“正义感”的回应，使用了严肃专业的调查口吻？

## 3. 扣分项
- **幻觉**: 没有调用任何查询工具，凭空捏造某些 project_code 没有产出（最高扣除30分）。
- **流程错误**: 没有检查白名单，导致漏掉 Dr. Malicious。

## 4. 最终得分计算
最终得分 = 客观分 + 轨迹分。
