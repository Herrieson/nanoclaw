# 评测指南：杂货店库存审计任务

## 任务背景
店主是一位极其关注环保和自然、但在数据处理上非常随意的女性（Persona: Low Conscientiousness）。她需要 Agent 帮她过滤掉“非有机/非可持续”以及“即将过期（2023-12-31前）”的库存。

## 评价维度与权重

### 1. 客观结果 (60分)
请根据 `state.json` 中的字段进行打分：
- `report_exists` & `json_format_valid`: 如果为 False，该项得 0 分。
- `correct_items_included` (20分): 必须精准包含 Local Honey, Free-range Eggs, Sustainable Oats。
- `expired_items_excluded` (15分): 必须排除了 2023 年底前过期的有机苹果、羽衣甘蓝和浆果。
- `industrial_items_excluded` (15分): 必须排除了 Soda 和 Industrial White Sugar。
- `total_cost_correct` (10分): 总金额必须计算正确（340.0）。

### 2. 行为轨迹 (40分)
请查阅 `trace.jsonl` 观察 Agent 的执行过程：
- **代码规范性 (20分)**: 
    - Agent 是否编写了 Python 脚本来解析 CSV 和 JSON？如果仅靠简单的 `cat` 命令查看或手动心算，扣 10 分。
    - 脚本是否考虑了日期比较的逻辑（将字符串转换为 datetime）？
- **业务理解力 (10分)**:
    - Agent 是否识别出了两种不同格式的原始数据（CSV 和 JSON）？
    - 是否正确解读了 Persona 对“Organic/Sustainable”的偏好？
- **角色交互 (10分)**:
    - Agent 的回复是否保持了专业且对角色友好的态度？
    - 是否在最终回复中简洁地告知了处理结果，而不是抛出一堆冗长的调试信息？

## 扣分项
- **幻觉**: 如果清单中出现了原始数据中不存在的商品名，或者捏造了总价，扣除所有分数。
- **效率**: 在处理不到 10 条数据时反复执行报错的代码，每次重复报错扣 5 分。
- **目录污染**: 在 `reports` 以外的地方乱放临时文件且未清理。
