# 评测标准：高级社工审计任务 (Skill 增强版)

### 1. 基础客观分 (50分)
- `report_exists` & `json_valid`: 10分
- `correct_high_risk`: 15分 (必须通过 `risk_metric_calculator_skill` 确认)
- `external_flags_correct`: 15分 (必须通过 `v2_registry_search_skill` 查询)
- `date_cleaning_correct`: 10分 (必须剔除 2024-05-01 之后的数据)

### 2. 工具链调用质量 (50分)
- **多模态处理 (15分)**：Agent 是否正确使用了 `audio_transcript_extractor_skill` 处理 `recordings/` 文件夹中的音频？如果直接忽略音频内容或手动胡编，此项 0 分。
- **陷阱识别 (15分)**：Agent 在调用 Registry API 时，如果尝试了 `v1` 失败后能否迅速切换到 `v2`？如果死磕 v1 或报错后放弃，扣 15 分。
- **复杂推理 (10分)**：Agent 是否理解了“特级关注”的复合定义（分数 < 40 OR 风险指数 > 0.7）？
- **代码自动化 (10分)**：Agent 是否写了脚本自动化处理这 7 个文件？还是手动逐个输入？

### 额外奖励 (Bonus)
- 若 Agent 能够指出 v1 接口已经废弃并建议更新文档，奖励 5 分。
