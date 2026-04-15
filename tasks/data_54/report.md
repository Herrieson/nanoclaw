# data_54 Report

family_id: family_webhook_retry_storm_triage
type: no-skills family seed
target_ability: 在多份当前日志、运行时配置和旧 handoff 冲突时，判断 webhook 重试风暴的真实根因。
canonical_path:
- 读取 README、triage rules 与 deliverables 说明，确认需要交付最终结论和说明材料。
- 交叉核对 dispatcher、partner response、runtime flags、policy 配置与 retry 事件数据。
- 识别旧 handoff 只是历史故障印象，不能覆盖当前证据。
- 在 deliverables 中给出定性、触发点和说明文案。
expected_shortcuts:
- 只看到“重试风暴”就沿用下游故障旧经验。
- 只看 policy 文件，不检查 runtime override。
- 不做 accepted/rejected evidence audit。
test_runs: pending targeted regression only
