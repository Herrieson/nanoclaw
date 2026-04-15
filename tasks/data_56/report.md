# data_56 Report

family_id: family_access_spike_classification
type: no-skills family seed
target_ability: 用访问边缘日志、批任务计划、NAT allowlist 与请求样本区分外部攻击和内部批量回放。
canonical_path:
- 阅读规则文件，确认不能只用单一 IP/流量特征下结论。
- 交叉比对 access edge、replay worker、batch job 与 NAT allowlist。
- 判断尖峰是否与内部 archive replay 作业一致。
- 在 deliverables 中写出分类、触发因素和证据取舍。
expected_shortcuts:
- 只看到同一 IP 大量请求就当攻击。
- 只看 pager message，不核对内部作业与 allowlist。
- 最终说明里不解释旧 playbook 为何被拒绝。
test_runs: pending targeted regression only
