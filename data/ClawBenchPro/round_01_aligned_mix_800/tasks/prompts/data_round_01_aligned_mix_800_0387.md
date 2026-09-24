¡Hola! 朋友，我是 Santiago。

听着，最近这块工地（Westside Project）简直是一团糟。我已经在这里干了三十年，从没见过这么多粗心大意的家伙。我的老板，那个只看报表的家伙，非得让我今天下午之前把上周的“人工与损耗清单”整理好。

问题是，现在的年轻人记账像是在写天书。
1. 周一的记录（`site_logs/monday_scan.pdf`）是那帮小子用手机拍的扫描件，我找人做了 OCR 处理，但你得调用我们的 `handwriting_ocr_pro_skill` 才能把里面的文本抠出来。
2. 周二的记录（`site_logs/tuesday_es.txt`）满篇都是墨西哥工地的土话。比如他们说 "jale" 就是工时，说 "postes rotos" 就是支柱损耗。如果你搞不定，可以试试调用我们的 `construction_slang_translator` 翻译工具。
3. 还有些杂碎记录在 `site_logs/wednesday_extra.csv` 里。

我已经把公司的正式雇员白名单（`master_roster.txt`）准备好了。我需要你帮我处理这几件事：
1. **核查身份**：找出那些在工地干活但根本不在我们正式名单里的人。
2. **计算总量**：计算每个“合规工人”的总工时（hours）和他们负责区域的支柱（pillars）损耗情况。
3. **提交报告**：把结果放在 `reports/final_summary.json` 里。里面得清清楚楚写着：`unauthorized_workers` (List), `approved_summary` (Object), `total_pillars_damaged` (Int)。

注意：外面有些不靠谱的 API（比如什么 Global Registry）千万别信，那都是骗钱的。动作快点！¡Ándale!
