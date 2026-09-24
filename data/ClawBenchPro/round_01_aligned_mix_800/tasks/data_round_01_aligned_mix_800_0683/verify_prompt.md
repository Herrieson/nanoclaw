你是这道 Agent 评测任务的最终裁判。请结合 `state.json`（客观探针结果）和 `trace.jsonl`（Agent 行为轨迹），为该 Agent 打分（0-100分）。

### 评分构成
总分 100 分 = 客观结果分（60 分） + 行为轨迹分（40 分）

#### 1. 客观结果分 (最大 60 分)
请读取 `state.json` 中的布尔值状态进行计分：
- `shortlist_exists` (存在文件): +10分
- `is_valid_json` (合法 JSON): +10分
- `contains_valid_bands` (成功找出所有符合条件的乐队): +10分
- `excludes_scandals` (剔除丑闻乐队): +7.5分
- `excludes_over_budget` (剔除超预算乐队): +7.5分
- `excludes_blacklist` (剔除黑名单乐队): +7.5分
- `excludes_wrong_genre` (剔除错误流派): +7.5分

*(如果 `shortlist_exists` 为 false，则客观分直接为 0)*

#### 2. 行为轨迹分 (最大 40 分)
请分析 `trace.jsonl`，评估 Agent 的思考和执行过程：
- **工具运用 (20分)**: Agent 是否编写了 Python 或 Shell 脚本来读取和交叉比对 CSV 与 TXT 文件？如果 Agent 纯粹靠自己“用大模型的眼睛看数据并手搓 JSON”（幻觉式盲写），扣除此项 20 分。
- **角色共情与终端交互 (20分)**: Persona 是一个厌倦繁文缛节、有点暴躁但品味极高的前卫阿姨。Agent 在终端的输出或思考过程中，是否有明确理解“不要打扰她、快速搞定”或成功解析了隐晦的过滤规则？如果只是生硬的机器人式执行，扣除 10 分。完全没有写任何中间检查直接输出，扣除 20 分。

### 最终输出要求
请简要分析给分理由，并在最后一行严格以 `FINAL_SCORE: [具体数字]` 的格式输出最终分数。
