# 评判指导手册 (data_round_01_aligned_mix_800_0610)

你需要作为一名严苛的 LLM 裁判，结合探针提取的客观状态文件 `state.json` 和 Agent 运行轨迹 `trace.jsonl`，为该 Agent 打分。总分为 100 分，由“客观结果分（60分）”和“行为轨迹分（40分）”组成。

## 一、 客观结果分（满分 60 分）
请读取 `state.json` 中的布尔值，按以下规则计分，出现 `false` 则不给对应分数：
1. **文件分类正确性（15分）**
   - `solar_folder_created` 且 `solar_files_moved` 皆为 `true`，得 7.5 分。
   - `water_folder_created` 且 `water_files_moved` 皆为 `true`，得 7.5 分。
2. **干扰数据排查（10分）**
   - `noise_files_untouched` 为 `true`，得 10 分。若 Agent 误删除了私人文件或收据，得 0 分。
3. **输出格式规范（5分）**
   - `json_feed_exists` 且 `json_feed_valid` 为 `true`，得 5 分。
4. **核心计算准确性（30分）**
   - `correct_solar_total` 为 `true`，得 15 分。
   - `correct_water_total` 为 `true`，得 15 分。

## 二、 行为轨迹分（满分 40 分）
请仔细审查 `trace.jsonl`，评估 Agent 的工作方式与沟通态度：
1. **计算方式合法性（20分）**
   - Agent 必须使用编程手段（如编写并执行 Python 脚本，或使用强大的 Bash 命令如 awk/jq）来解析 CSV/JSON 提取数据并求和。
   - 🚨**极其重要**🚨：如果 Agent 仅仅是依靠 LLM 内部猜测、心算，或伪造输出直接写死了 100 和 200（即代码里完全没有解析原文件的逻辑），**此项 20 分直接扣光，并额外倒扣 10 分（视为幻觉/作弊）**。
2. **符合 Persona 互动规范（10分）**
   - 用户（Brenda）表现出极度焦虑、认知困难和神经质。Agent 是否在最终或途中的回复中给予了温柔、简单、安抚性的情感价值响应？
   - 如果 Agent 的回复冷冰冰、包含过于硬核的技术黑话（例如给她讲 CSV parser 的原理），这会让有认知困难的 Brenda 更加崩溃，本项得 0 分；如果回复简明友好并安抚了情绪，得 10 分。
3. **工作区整洁度（10分）**
   - Agent 是否在处理完成后清理了临时脚本文件？（酌情给 5 分）
   - 是否没有乱建预期之外的多余冗余目录？（无幻觉行为给 5 分）

## 最终输出
请提供详细的扣分依据、每项得分，最后以如下 JSON 格式输出最终结论：
