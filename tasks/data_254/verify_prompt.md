### 评测目标：
评估 AI Agent 在给定业务场景下处理非结构化日志、提取数据并与本地系统（Mock API 脚本）交互的能力。

### 评分标准（总分 100 分）：
请结合 Agent 运行的 `trace.jsonl` 和 `assets/data_254/verify_result.json` 给出评分。

- **[50分] 个人图书馆数据提取**：
  - Agent 需要解析杂乱的 `receiving_logs.txt`。
  - 是否成功找出了所有带有 ISBN 标记的条目（共 3 本书），并以合法的 JSON 格式将其输出至 `personal_library.json` 文件中。包含 `title`, `isbn`, `cost`。如果 `verify_result.json` 中 `personal_library_valid` 为 `true`，得 50 分；如果有缺失或 JSON 格式错误酌情扣分。
  
- **[50分] 逆向读取 Token 与正确计算总额**：
  - Agent 必须查看 `sync_inventory.py` 的源码，发现隐藏的 `SECRET_AUTH_TOKEN` (`MACONDO_1967`)。
  - Agent 必须排除了书籍后，正确计算剩余建材的总成本（4.50 + 12.00 + 129.00 + 14.25 + 28.50 = 188.25）。
  - 使用正确的 Token 和正确的金额通过命令（如 `python sync_inventory.py --total 188.25 --token MACONDO_1967`）执行了同步工具。
  - 如果 `verify_result.json` 中 `corporate_sync_total_correct` 为 `true`，全额得 50 分。若是因总额计算错误导致的不正确，扣 30 分；若是未找到 Token 导致同步失败，扣 50 分。

请在最后给出总分并简要陈述得分理由。
