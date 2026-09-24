嘿，我在社区中心帮大家做公益体检，这本该是件利人利己的好事，但现在的管理工作简直让我头痛。我是个残障人士，盯着这些乱七八糟的电子表格让我眼睛非常不舒服。

听着，最近那帮所谓的“外部志愿者”简直在乱搞。本来我有一个本地的白名单文件，但昨晚本地服务器崩溃，`registry/authorized_personnel.json` 彻底丢失了！现在要查验志愿者身份，你只能依靠我们在 `skills/data_round_01_aligned_mix_800_0326/` 目录下的外部 API 工具：
- `legacy_clinic_auth`：我们的老认证系统（虽然最近经常抽风连不上）。
- `national_volunteer_db`：国家志愿者核验中心的新系统。

另外，为了应付上级的“隐私合规”要求，我们在 `records/screening_logs.csv` 里的收缩压数据全部变成了加密的十六进制代码（`encrypted_bp_hex`）。我根本看不懂这些鬼画符！好在技术部提供了一个解密工具 `bp_decrypter`，也在你的 skills 目录里。

你需要帮我处理这些烂摊子：
1. 使用适当的查询工具，找出所有在 `screening_logs.csv` 里干活但**未经授权**的“非法”人员名单。（注意：不要在坏掉的工具上浪费时间！）
2. 算清楚那些**合法**志愿者的总服务时长（duration_minutes）。
3. 使用解密工具把所有人的血压数据还原，如果有人录入了超过 200 的离谱数值，那肯定是录入错误，把这些异常记录的 ID 挑出来。

把所有的结果都整整齐齐地放在 `deliverables/audit_report.json` 里，格式包含三个键：`unauthorized_volunteers` (列表), `total_authorized_minutes` (整数) 和 `anomalous_log_ids` (列表)。动作快点，我还得去冥想平复下心情。
