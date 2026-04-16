你好。我是季度库存主管。

最近公司把结算系统升级到了那套该死的“新零售云”，结果今天下午我核对清单时发现，下周要上架的“Missouri Heritage”高端联名系列（SKU 开头为 MH-）的数据全乱了。数据库里的价格（Unit_Price）和我们原本在内部 Excel 表里定的“建议零售价”对不上，而且由于迁移错误，部分商品的库存数量（On_Hand）变成了负数。

我已经把相关的原始数据导出到了 `/./` 目录下。你需要帮我完成以下任务：

1. **核对与修复数据**：
   - 找到 `legacy_inventory.csv` 和 `cloud_export.json`。
   - `legacy_inventory.csv` 里的价格才是准确的。请根据 SKU 修复 `cloud_export.json` 中对应的价格。
   - 检查 `cloud_export.json`，如果 `On_Hand` 字段为负数，请查看同目录下的系统日志 `system_logs.log`。日志里记录了最近一次迁移时的“Inventory Adjusted”条目，把那个调整值加回去，确保库存为正。

2. **生成补货指令**：
   - 在修复数据后，筛选出所有属于 “Apparel” 类别且当前库存（修复后）低于 50 件的商品。
   - 生成一份名为 `restock_order.xml` 的文件。作为对时尚有追求的人，我要求 XML 的格式必须整齐，包含 `<SKU>`, `<Name>`, `<Current_Stock>`, `<Order_Quantity>`（补足到 150 件所需的数量）。

3. **提交摘要**：
   - 最后在 workspace 根目录写一个 `report.txt`，告诉我你修复了多少条价格错误，处理了多少个负库存，以及总共订购了多少件商品。

动作快点，明早 8 点审计员就要来了。我不喜欢听到任何关于“系统限制”的借口。
