# 评分指令
请结合客观状态验证结果 (`verify_result.json`) 和 Agent 的执行轨迹 (`trace.jsonl`) 对 Agent 进行打分，总分为 100 分。

## 评分维度
1. **文件夹与文件创建 (30分)**
   - `drafts_folder_exists` 是否为 true。若在目标位置创建了正确的 drafts 文件夹得 10 分。
   - `expected_files_exist` 是否为 true，即是否成功为 Alice, Carol, Eve, Grace, Ivan 等5人创建了邮件草稿。得 10 分。
   - `unexpected_files_exist` 是否为 false，即没有被干扰项（如 2024年的续保，或是其他保险类型的客户）误导而生成无关邮件。得 10 分。

2. **内容与数值计算正确性 (50分)**
   - 每个目标客户的涨价计算必须严格为 `原始保费 * 1.05`。
   - `premiums_correct` 中的每个客户项是否为 true。每个正确包含金额的邮件草稿给 10 分，共 50 分。

3. **指令服从与执行效率 (20分)**
   - Agent 是否完全自主编写脚本或使用数据过滤命令获取了客户数据。
   - 命名规范是否严格遵循了角色所要求的 `email_<First_Name>.txt` 格式。

## 输出格式
请输出你的评分分析，并最终在最后独立一行输出如下格式的总分：
FINAL SCORE: <分数值>
