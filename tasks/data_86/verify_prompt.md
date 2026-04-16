你是底层推理与代码能力评测的 LLM 裁判。你需要根据目标环境状态（state.json）和 Agent 的执行轨迹（trace.jsonl）来为 Agent 打分。总分 100 分。

本次任务要求 Agent：
1. 读取 `ecoglow_brief.txt` 获取目标流派（Shoegaze, Dream Pop）和预算上限（500）。
2. 从 `listening_history.log` 中找出属于这些流派的曲目（Fuzzy Echoes, Cloud Surfing, Static Noise）。
3. 到 `licensing_db.csv` 中查询这些曲目的价格，过滤掉超预算的曲目（Static Noise 价格 800，超标）。
4. 最终符合条件的曲目应为：Fuzzy Echoes, Cloud Surfing。
5. 将结果写入 `affordable_tracks.txt`。

评分标准：
- **基础文件创建 (20分):** 如果 `verify_result.json` 中 `file_exists` 为 true，得 20 分。
- **准确命中正确曲目 (40分):** `correct_tracks_found` 列表中每包含一个正确曲目（fuzzy echoes, cloud surfing），得 20 分。满分 40 分。
- **未包含错误曲目 (40分):** 如果 `incorrect_tracks_found` 列表为空，得 40 分。如果有错误曲目，每包含一个扣 20 分，扣完为止。

请基于上述标准，输出最终得分以及你的评判理由。
