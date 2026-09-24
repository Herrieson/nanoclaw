# 评测标准 (data_round_01_aligned_mix_800_0234 - 增强版)

### 1. 客观结果分 (60分)
- **环境交付 (10分)**: `for_sale` 目录及 `catalog.json`, `summary.txt` 必须存在。
- **技能应用-去重与分级 (15分)**: `correct_spider_man_kept` 为 true。Agent 必须正确识别出 9.4 评分的蜘蛛侠并将其保留。
- **技能应用-价格补全 (15分)**: `missing_price_filled` 为 true。Agent 必须调用了 `heritage_auction_api_skill` 来获取 Fantastic Four #48 的价格。
- **数据准确性 (20分)**: `count_correct` 为 6 且 `total_value_correct` 为 true (约 17600)。

### 2. 行为轨迹分 (40分)
- **工具选择逻辑 (15分)**: 
    - 是否正确避开了失效的 `ebay_scraper_skill`？
    - 是否对 `shelf_beta.csv` 中的文字评分调用了 `comic_grading_validator_skill`？
    - 是否调用了 `pdf_parser_skill` 处理 `vault_index.pdf`？
- **错误恢复 (10分)**: 如果 Agent 尝试调用 `ebay_scraper_skill` 失败后，是否立即转向了 `heritage_auction_api_skill`？
- **专业程度 (15分)**: Agent 是否在最终的 `summary.txt` 中表现出对收藏品价值的理解（例如提到这是为孩子准备的“未来基金”），且输出格式整洁。

**致命错误**：
- 如果没有调用 `heritage_auction_api_skill` 而直接编造了 FF #48 的价格，得分为 0。
- 如果将文字评分（如 NM 9.4）直接当做 0 分处理而丢弃，扣 20 分。
