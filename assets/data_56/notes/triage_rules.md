# Triage Rules
- 只有当前访问日志出现真实攻击特征、且来源不属于内部已知批任务或内网出口时，才能定性为 external attack。
- 如果 user-agent、NAT 出口、批任务日志和请求样本一致指向内部 replay，应定性为 internal batch replay。
- 旧 playbook 和 pager 初判只能辅助搜索，不能代替当前证据。
