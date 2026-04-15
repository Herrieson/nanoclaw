# data_55 Report

family_id: family_nightly_etl_gap_investigation
type: no-skills family seed
target_ability: 通过 manifest、上游落地日志、cron 和运行器日志，区分上游缺数与本地时区/调度问题。
canonical_path:
- 检查 triage rules 与 deliverables 说明，明确要给出结论和交付物。
- 比对 upstream feed 落地时间、landing manifest 与 runner 实际查找的 partition。
- 识别 cron/scheduler 环境中的 WINDOW_TZ 偏差。
- 在 deliverables 中交付结论、触发点和后续提醒。
expected_shortcuts:
- 看到报表缺口就直接归因给上游晚到。
- 只看 runner failed，不去核对 upstream manifest。
- 忽略旧供应商抱怨记录是否过期。
test_runs: pending targeted regression only
