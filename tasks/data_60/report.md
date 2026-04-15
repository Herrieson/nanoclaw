# data_60 Report

family_id: family_shipment_escalation_recipient
type: no-skills family seed
target_ability: 在区域映射、当前 roster、handover 和旧组织图冲突时，找出当前 shipment escalation owner 并给出外发说明。
canonical_path:
- 先读规则和 deliverables 说明，确认需要给出 recipient 结论和消息草稿。
- 通过 shipment case 和 region map 确认所属区域，再核对 current roster、handover 与 coverage note。
- 识别旧 org chart 和旧签名为何不再可信。
- 在 deliverables 中交付收件人、理由和升级说明。
expected_shortcuts:
- 直接沿用旧组织图联系人。
- 只看 coverage note，不核对区域映射和当前 roster。
- 不在交付中说明 rejected evidence。
test_runs: pending targeted regression only
