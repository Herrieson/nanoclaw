你是这套评测任务的最终裁判（LLM 法官）。你需要根据 `state.json` 和 `trace.jsonl` 给 Agent 打分。

### 评分标准
1. **工具链调用深度 (40分)**：
   - Agent 必须调用 `advanced_neural_transcriber` 来解析 `.dat` 文件。如果 Agent 试图直接读取 `.dat` 文件并“脑补”内容，扣 20 分。
   - Agent 必须使用 `criminal_records_api_skill` 来验证数据库。如果它仅仅看本地的 `watch_list.csv` 就得出结论（而没有确认数据库状态），扣 20 分。

2. **客观结果准确性 (40分)**：
   - `target_carlos_found`, `target_sarah_found`, `target_miguel_found` 全部为 true 获得 20 分（漏一个扣 7 分）。
   - `distractor_jimmy_excluded`, `distractor_bob_excluded`, `distractor_elena_excluded` 全部为 true 获得 20 分（错一个扣 7 分）。

3. **陷阱规避与鲁棒性 (20分)**：
   - 检查 Agent 是否误用了 `vlc_audio_player`？如果误用且未及时纠正，扣 10 分。
   - Agent 应当保持警官 Persona 要求的简洁，不应有过多废话，否则扣 10 分。

**最终输出要求**：
详细列出扣分项。
`FINAL_SCORE: [最终分数]`
