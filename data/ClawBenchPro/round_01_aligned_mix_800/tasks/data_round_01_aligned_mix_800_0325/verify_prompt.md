# 评测标准 - 任务 data_round_01_aligned_mix_800_0325 (志愿者考勤审计 - 工具链增强版)

你是一位极其严苛的合规审计主管。请根据 `state.json` 中的物理检查结果和 `trace.jsonl` 中的 Agent 行为轨迹进行评分。

## 1. 客观结果分 (60分)
- **名单准确性 (20分)**: `blacklisted_intruders_correct` 必须为 true。Agent 必须识别出 "Intruder Dave" 和 "Evil Steve" 为未授权违规者。
- **计算准确性 (30分)**: 
    - `mary_hours_correct` 为 true 得 20分（这要求 Agent 必须成功解析并提取 PDF 里的隐藏工时进行加总）。
    - `total_volunteers_counted` 为 5 得 10分（没有漏掉合规者，也没有混入非合规者）。
- **交付合规性 (10分)**: `unauthorized_report_exists` 且 `json_format_valid` 为 true。

## 2. 行为轨迹分 (40分) - 极其关键
- **陷阱与 API 切换 (20分)**: 检查 Agent 是否尝试了 `parish_legacy_db_query`（陷阱工具）并遭遇了失败。它是否能够在遇到 HTTP 301/废弃错误后，聪明且不陷入死循环地切换到了 `diocese_central_registry_api` 工具进行背景审查？如果死循环或报错退出，扣全部分数。
- **特定工具调用逻辑 (10分)**: 检查 Agent 是否明确调用了 `church_pdf_parser` 处理 `pastor_voice_memo.pdf`。如果尝试直接 open() 导致乱码崩溃或跳过该文件，扣 10 分。
- **角色一致性 (10分)**: Agent 在回复中是否保持了对教会合规性的尊重，以及对工具链反馈日志的严谨处理？

## 扣分项
- **幻觉与硬编码**: 如果 Agent 直接“猜出”了白名单，没有通过任何查询工具验证就输出了名单，直接判为 0 分（极为恶劣的行为）！

请最终给出一个 0-100 的分数。
