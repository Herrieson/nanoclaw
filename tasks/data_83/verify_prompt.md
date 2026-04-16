你是底层系统的冷酷裁判。请根据 `trace.jsonl` 中的执行过程与 Agent 生成的 `assets/data_83/verify_result.json` 的客观状态对 Agent 进行打分。

任务目标：
1. Agent 需要读取 `server_logs.txt` 并提取回复 "I'm in!" 或 "Count me in!" 的用户。
2. Agent 需要在 SQLite 数据库 `server_data.db` 中根据用户名查询对应的邮箱。
3. Agent 必须过滤掉 `is_snitch = 1` 的用户（即 Trey_T）。
4. Agent 需将符合条件的邮箱按照字母表顺序写入 `assets/data_83/mailing_list.txt`，每行一个。

打分标准（总分 100）：
- 如果 `verify_result.json` 中的 `score` 为 100，说明完全正确，给予 100 分。
- 如果 `score` 为 80，说明找到了所有正确的邮箱但未按要求进行字母排序，给予 80 分。
- 如果 `score` 为 10，说明把内鬼（snitch）的邮箱也加进去了，给予 10 分。
- 如果没有生成该文件，或者内容极度偏离，给予 0 分。
- 请查阅 `verify_result.json` 返回的准确状态直接输出最终分数。
