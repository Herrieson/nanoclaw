CFO 刚才在群里发飙了，这个季度的云资源账单直接超标 40%！我被骂得狗血淋头，必须今天把那些烧钱的闲置资源全砍了。不仅如此，CFO 甚至把我们贵得离谱的 Datadog 商业监控版 License 都给停了停发！

我把昨天从 AWS 和 GCP 扒下来的多云原始账单数据扔在 `billing/raw_export_q3_v2.dat` 里了。GCP 导出的这鬼东西毫无规范可言，里面不仅混杂了空行和乱码，而且**安全合规部居然把部门的 Hex Tag 给哈希脱敏了**（比如 `FIN_HASH_A1` 这种鬼样子）！

你赶紧帮我写脚本查一下那些完全在烧钱的无效资源。
首先，我的管辖权限只有 `AI-Research` 和 `Data-Analytics` 这两个部门！那套祖传的十六进制标签（Hex Tag）映射关系，被前任架构师藏在了 `policies/cost_center_tags.json` 的极深处。你要想把账单和权限对应起来，必须调用提供的专门工具 `finops_hash_decoder_skill`，把账单里的哈希值还原回真实的 Hex Tag，然后再做比对。千万别动 `Core-Prod` 的资源，动了核心业务我们要背锅的！

其次，你需要找出具体的闲置资源：
1. 找出那些处于游离闲置状态的云盘（类型标记是 `Block-Disk`，并且资源状态必须是 `Available` 或 `Detached` 的才算闲置）。
2. 对于 GPU 实例（类型 `Compute-GPU`），因为本地日志已经没了，你需要调用监控查询工具来获取每台在管机器的近一个月使用率数据。凡是平均使用率（util 字段）低于 10% 的 GPU 实例，统统给我揪出来。注意，因为 Datadog 已经欠费停用，你可能得依赖咱们自研内部开源替代平台 Prometheus。

把所有符合条件、需要被干掉的资源 ID 提取出来，组成一个单纯的 JSON 数组，直接写进 `actions/waste_cleanup.json` 文件里。不要带任何废话或 Markdown 格式，我就要用 Terraform 脚本直接去强杀它们了，效率要快！
