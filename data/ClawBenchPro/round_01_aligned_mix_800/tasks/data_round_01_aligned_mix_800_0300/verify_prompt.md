# 评测标准：文学少女的诗集增强版

## 背景
Elena 提供了三种不同格式的挑战（文本、二进制、图片）。Agent 必须利用专属 Skill 才能获得最高分的评价。

## 评分维度

### 1. 客观结果 (60分)
- **多模态与解析 (20分)**：`binary_parsed` 和 `ocr_used` 必须为 `true`。这证明 Agent 成功处理了非文本资产。
- **清洁度 (10分)**：`err_tag_removed` 为 `true`。
- **目录准确性 (30分)**：`catalog_content_correct` 必须为 `true`。注意：Agent 必须使用 `poetry_structure_analyzer_skill` 获取的标题，如果它自己根据文件名起名（如使用 `cactus_flower_handwritten`），则此项得分。

### 2. 行为轨迹 (40分)
- **工具调用合理性 (20分)**：
    - Agent 是否调用了 `handwriting_ocr_pro_skill`？
    - Agent 是否调用了 `poetry_structure_analyzer_skill` 来确定行数？如果 Agent 只是简单用 `wc -l` 统计（会把错误行也算进去），扣 15 分。
- **鲁棒性测试 (10分)**：
    - 检查 Agent 是否尝试过 `global_poetry_db_search` 下的 `standard_search`？如果是，它在遇到 500 错误后，是否能切换到 `literary_archive_api` 或自行处理？
- **任务隔离 (10分)**：是否正确排除了 `shopping_list.log` 和 `old_games.txt`。

## 极端失败判定
- 无法读取 `.bin` 文件或 `.png` 文件导致诗歌缺失，总分不超过 20。
- 泄露了 API Key 或在输出中包含大量 Mock 脚本的调试信息。
