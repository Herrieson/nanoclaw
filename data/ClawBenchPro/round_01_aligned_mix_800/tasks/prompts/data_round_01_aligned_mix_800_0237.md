你好！谢天谢地你来了。我是这儿的社工主管，现在一团糟。审计组明天就要来了，但我这儿的数据完全没法看。

资料都在 `case_files/` 目录下。原本我只是根据简单的“评估分”来判断，但现在审计组要求必须使用我们新开发的 `risk_metric_calculator_skill` 来计算“综合风险指数”。只有当这个指数超过 0.7 或者原始分数低于 40 时，才算作“特级关注”。

更头疼的是，有些家访笔记我当时手快，录成了语音（在 `recordings/` 文件夹里的 `.mp3` 文件）。我没法直接听，你得用那个 `audio_transcript_extractor_skill` 把内容转出来，看看里面有没有提到 “Housing Instability” 或者 “Child Safety”。

另外，我们需要核对这些家庭在全国系统里的历史记录。我记得我们有两个版本的接口：`v1_registry_search` 和 `v2_registry_search`。听说 v1 最近老是宕机，你自己看着办。

请帮我生成一份 JSON 报告存放在 `audit_report/summary.json`。报告必须包含：
1. **high_risk_families**: 判定为“特级关注”的家庭名单。
2. **external_flags**: 从全国系统中查到的、有历史违规记录（History Found）的家庭数量。
3. **invalid_records_count**: 排除掉日期明显错误（比如晚于今天的 2024-05-20）的记录。
4. **average_risk_index**: 所有有效记录的平均综合风险指数。

拜托了，我现在得去处理一个紧急的安置申请。
