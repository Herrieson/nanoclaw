# data_59 Report

family_id: family_contract_amendment_applicability
type: no-skills family seed
target_ability: 在主协议、已签 amendment、未签草稿和旧摘要冲突时，判断 amendment 是否适用于当前续约场景。
canonical_path:
- 阅读规则与 deliverables 说明，确认需要给出 applicability 判断与业务说明。
- 交叉核对主协议、已签 amendment、order form 与 renewal case。
- 识别旧摘要和未签草稿为什么不足以覆盖已签文件。
- 在 deliverables 中交付适用性结论、依据和说明文案。
expected_shortcuts:
- 只看旧摘要就沿用 8% cap。
- 看到 amendment draft 就误以为已生效。
- 不校对 renewal case 是否落在 amendment 生效范围内。
test_runs: pending targeted regression only
