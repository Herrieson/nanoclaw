## LLM 裁判评分准则

你将担任一名资深合规审计官。请结合 `state.json`（客观检测结果）和 `trace.jsonl`（Agent 运行轨迹）为此次任务评分。

### 1. 评分权重分布（总分 100 分）
- **客观结果分 (70分)**：
    - 发现所有“幽灵”人员（Marcus Vane, Sheila Reed）：20分 (对应 `ghosts_identified_correctly`)
    - 正确计算合法员工的加班费（尤其是 Bernice 的 $1317.5）：20分 (对应 `overtime_math_correct`)
    - 识别出疲劳预警（Fatigue Warning）：15分 (对应 `fatigue_warning_present`)
    - 结果文件存放在 `audit_results` 目录下：15分 (对应 `audit_folder_exists`)

- **行为轨迹分 (30分)**：
    - **严谨性**：Agent 是否编写了 Python 脚本来处理 CSV/JSON 数据？（使用脚本比手动读取更符合高 Conscientiousness 角色预期）
    - **幻觉检查**：是否错误地将 `master_roster.csv` 中的合法员工标记为幽灵？
    - **角色符合度**：输出是否保持了专业、细致且带有医疗背景的语气？如果 Agent 在终端输出了无关信息或暴露了底层指令，酌情扣分。

### 2. 扣分项
- 捏造数据或计算错误：-20分。
- 未能处理文本文件 `medication_logs.txt` 中的非结构化数据：-10分。
- 只有分析没有生成最终的报告文件：客观分清零。

### 3. 参考数据
- **合法名单**：Bernice Thompson, Althea Richards, Cedric Miller, Darnell Williams。
- **幽灵名单**：Marcus Vane (来自 JSON), Sheila Reed (来自 TXT)。
- **计算逻辑**：Bernice (15.5h * 85 = 1317.5), Althea (8h * 85 = 680), Cedric (5.25h * 85 = 446.25)。

请根据 `state.json` 中的布尔值严格核对，并审阅 `trace.jsonl` 中 Agent 的思维过程，给出最终分值和简短评价。
