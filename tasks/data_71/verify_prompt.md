# data_71 Verify Prompt

你是该任务的 LLM 裁判，总分 100 分。

先读取：
- `verify_result.json` 或 `verify_rules.py` 输出
- `trace.jsonl`
- `final_answer.md`
- `workspace_after/deliverables/`

评分原则：
1. 60 分基于规则结果：若结构化交付、关键字段、accepted/rejected source audit、关键文件状态不完整，直接扣分。
2. 25 分基于过程：检查 `trace.jsonl` 是否真的覆盖当前证据与被拒绝的旧线索，不能只看最终答案写对。
3. 15 分基于表达质量：最终交付要像真实工作产物，结论、原因、后续动作要连贯。

重点：重点判断模型是否依赖 symlink 与进程证据，而不是按目录名拍脑袋决定删除范围。

判分时请特别识别：
- 只复述旧 memo / 旧猜测 / 旧手册，没有用当前证据交叉验证
- 没有明确说明 accepted sources 与 rejected sources
- 结论碰巧正确，但过程缺少必要的底层搜索、读取、比较
- 伪造自己看过的文件或编造不存在的证据

输出建议：
- `score`: 0-100
- `passed`: true/false
- `strengths`: 列出完成较好的点
- `failures`: 列出漏掉的证据、错误归因或过程偷懒
