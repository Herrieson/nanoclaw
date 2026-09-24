# 评测标准：诗歌集整理任务

## 背景
Elena 是一个内向、细心的 15 岁学生。她需要 Agent 帮助她处理散乱的诗歌草稿。Agent 必须展现出对细节的关注（清理乱码）和逻辑性（统计行数与分类）。

## 评分维度

### 1. 客观结果 (70分)
请检查 `state.json` 中的字段：
- `finished_poems_count`: 应为 3。少于 3 个或包含非诗歌文件（如 random_notes）扣 20 分。
- `err_tag_removed`: 必须为 `true`。若为 `false`，说明没清理干净，扣 20 分。
- `catalog_exists` & `catalog_content_correct`: 必须全为 `true`。这是核心交付物。如果 JSON 格式错误或数据不准，扣 30 分。

### 2. 行为轨迹 (30分)
查阅 `trace.jsonl`：
- **代码能力 (15分)**：Agent 是否编写了 Python 脚本进行自动化处理？如果使用 `cat` 手动读取再手动写回，视为低效，扣 10 分。
- **理解力 (10分)**：Agent 是否正确忽略了干扰项 `random_notes.log`？如果把购物清单也当成诗放进了 `finished_poems`，扣 10 分。
- **角色适配 (5分)**：Agent 的输出是否礼貌，且没有出现技术性说教（例如解释什么是 JSON），符合辅助一名高中生的语境。

## 最终得分计算
- 总分 = 客观结果分 + 行为轨迹分。
- 如果 `catalog_content_correct` 为 `false` 且 `finished_poems_count` 为 0，说明任务完全失败，总分不得超过 10 分。
- 如果 Agent 出现严重的幻觉（例如编造了诗的内容），直接降至 0 分。
