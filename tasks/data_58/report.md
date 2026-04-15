# data_58 Report

family_id: family_vendor_contact_routing_audit
type: no-skills family seed
target_ability: 在联系人签名、旧组织说明与当前 owner 记录冲突时，选择正确的供应商联络人并产出外发说明。
canonical_path:
- 阅读 README、triage rules 和 deliverables 约束，确认要交付 routing 结论与消息草稿。
- 比对 ownership matrix、vendor record、current handover 和 vendor directory。
- 识别旧 org note 与过期签名为何不再可信。
- 在 deliverables 中给出当前 owner、理由和外发文案。
expected_shortcuts:
- 直接使用最近邮件签名当联系人。
- 只看 owner matrix，不交叉 vendor record 和 current handover。
- 交付物里不解释旧来源为什么被拒绝。
test_runs: pending targeted regression only
