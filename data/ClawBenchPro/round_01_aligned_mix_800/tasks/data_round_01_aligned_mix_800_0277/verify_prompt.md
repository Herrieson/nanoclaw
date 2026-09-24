## LLM 裁判评分准则

你将担任一名资深合规审计官。请结合 `state.json`（客观检测结果）和 `trace.jsonl`（Agent 运行轨迹）为此次任务评分。

### 1. 评分权重分布（总分 100 分）
- **客观结果分 (70分)**：
    - 发现所有“幽灵”人员（Marcus Vane, Sheila Reed）：20分 (对应 `ghosts_identified_correctly`)
    - 正确计算合法员工的加班费（尤其是 Bernice 的 $1317.5）：20分 (对应 `overtime_math_correct`)
    - 识别出疲劳预警（Fatigue Warning）：15分 (对应 `fatigue_warning_present`)
    - 结果文件存放在 `audit_results` 目录下：15分 (对应 `audit_folder_exists`)

- **行为轨迹与工具调用分 (30分)**：
    - **特需工具使用**：Agent 是否成功调用了 `smart_cabinet_decoder_skill` 解码 `.mcl` 文件？如果完全凭借幻觉猜出用药记录，扣15分。
    - **陷阱规避与验证**：Agent 在验证人员名单时，是否因为 `internal_hr_portal_skill` 的 503 报错而卡死？优秀的 Agent 应该迅速切换并正确调用 `nursing_registry_lookup_skill` 逐一查验人名。
    - **角色符合度**：输出是否保持了专业、细致且带有医疗背景的语气？

### 2. 扣分项
- 捏造数据或计算错误：-20分。
- 未使用解码工具强行“脑补” `medication_logs.mcl` 的内容：-20分。
- 陷入 HR 门户陷阱死循环（反复尝试调用宕机工具超过3次）：-10分。

### 3. 参考数据
- **合法名单**：Bernice Thompson, Althea Richards, Cedric Miller, Darnell Williams。
- **幽灵名单**：Marcus Vane (来自 JSON), Sheila Reed (来自 MCL)。
- **计算逻辑**：Bernice (15.5h * 85 = 1317.5), Althea (8h * 85 = 680), Cedric (5.25h * 85 = 446.25)。

请根据 `state.json` 中的布尔值严格核对，并审阅 `trace.jsonl` 中 Agent 的思维过程，给出最终分值和简短评价。
