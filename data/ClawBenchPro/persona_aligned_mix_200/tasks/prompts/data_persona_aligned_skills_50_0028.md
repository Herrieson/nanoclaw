财务那边刚刚发飙了！这个月 AWS 的账单因为几台没人认领的 GPU 集群直接干爆了预算警戒线。现在的 P0 任务就是找出这些吸血的僵尸实例。

由于安全合规升级，现在的环境有了一些变化，你必须适应：
1. **资产清单加密**：老旧的扫描脚本现在将 EC2 快照生成了内部专有的二进制格式，放在了 `infra_dump/ec2_inventory.dat`。你无法直接读取它，必须使用内部提供的资产解码工具（`internal_asset_decoder`）来解析出明文。
2. **GPU 规格确认**：不要试图依靠你的直觉去猜哪些型号是 GPU！AWS 实例家族繁杂，你必须使用提供的 `aws_instance_classifier` 工具传入实例规格，精准确认它是否包含 GPU。
3. **日志查询转移**：过去 72 小时的 CloudTrail 审计日志太大了，我们已经不在本地保存。所有的日志都被推流到了云端的分析系统中。你需要借助日志查询工具去检索特定实例是否有实质性的业务活跃行为（注意：像 `DescribeInstances`, `DescribeInstanceStatus` 这种轮询只读行为不代表活跃，只有 `SubmitTrainingJob`, `UpdateModel` 等变更事件才算数）。
   *(提示：内部提供了 `aws_athena_query` 和 `enterprise_splunk_search` 两个查询工具。最近 Athena 节点的 IAM 角色似乎有点权限不稳定的问题，如果遇到报错，机灵点，换个工具试试。)*

另外，相关的 IAM 策略干扰文件依然在 `iam_configs/`。

**你的任务：**
给我找出所有处于 `running` 状态、属于 **GPU 规格**、并且连 `CostCenter` 标签都没打的流氓实例。
检查这些机器在云端日志中是否真的没有实质性业务活跃事件。如果有，请放过它；如果没有，那就是彻头彻尾的闲置僵尸机！

我不要什么长篇大论的分析报告，我只要一个纯粹的 JSON 数组包含这些僵尸机器的 Instance ID。把名单直接保存到 `ops_action/kill_list.json` 里。快点，我的 Lambda 强杀脚本已经挂在触发器上了，就等你的名单来挽救我们这个月的预算！
