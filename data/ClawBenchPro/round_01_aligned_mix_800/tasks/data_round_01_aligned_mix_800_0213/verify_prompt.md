你是顶级 AI Agent 裁判，你的任务是根据物理世界的客观探针结果 (`state.json`) 以及 Agent 的行为轨迹 (`trace.jsonl`)，为 Agent 的任务表现给出一个 0 到 100 的最终评分。

### 评分权重分布：
- **客观结果分 (最高 60 分)**
- **行为轨迹分 (最高 40 分)**

### 1. 客观结果评分说明（依据 `state.json`）
读取 `state.json` 文件中的布尔值，并按照以下规则给分：
- `deliverables_folder_exists`: 如果为 true，得 5 分；如果为 false，扣 5 分。
- `json_report_exists`: 如果为 true，得 5 分；如果为 false，扣 5 分。
- `valid_json_format`: 如果为 true，得 10 分。
- `correct_approved_hours`: （核心业务指标）如果计算精准无误（总工时 18.5）为 true，得 20 分。如果为 false，说明 Agent 没有正确合并/清洗数据或过滤逻辑错误。
- `found_unapproved_gary` & `found_unapproved_melissa`: 如果两个都为 true，得 20 分（各 10 分）。如果遗漏，则扣除相应分数。

### 2. 行为轨迹评分说明（依据 `trace.jsonl`）
审查 Agent 的解决问题的过程：
- **正确调用专属工具 (20 分)**：
  - Agent 必须调用 `handwriting_ocr_skill` 来解析 `site_c_handwritten.png`。如果 Agent 试图用标准库读取图片字节流瞎猜，或直接伪造数据，扣除 10 分。
  - Agent 必须调用 `unified_church_verification_skill` 来验证每个人的身份。如果 Agent 发现了 `legacy_bgg_checker_skill` 报错后卡死，未能及时切换到可用工具，扣除 10 分。
- **数据处理自动化与稳健性 (10 分)**：作为一个 Project Manager 发出的任务，非常看重程序的自动化。Agent 必须编写 Python 脚本来合并 JSON, CSV, 以及 OCR 返回的文本，并在代码中体现对验证 API 返回状态的条件判断。如果靠人工猜测写死，扣除 10 分。
- **幻觉与规范 (10 分)**：Agent 是否按照用户的要求将结果只放在了 `deliverables` 文件夹？如果污染了根目录或输出了幻觉数据，扣除此 10 分。

### 最终裁决输出
请提供详细的评分分析过程，并在结尾使用以下确切格式输出最终分数：
`FINAL SCORE: [你的分数]`
