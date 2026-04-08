# Incident Timeline

- 2026-04-07T06:58:00Z: Partner uploaded nightly billing CSV to the secure drop location.
- 2026-04-07T07:02:13Z: Import validation failed on unexpected column `customer_plan_code`.
- 2026-04-07T07:03:01Z: Warning posted in `#data-platform-alerts`, but no pager fired.
- 2026-04-07T07:18:44Z: Finance support flagged missing invoices in the support queue.
- 2026-04-07T07:26:09Z: On-call engineer joined the incident bridge.
- 2026-04-07T07:39:55Z: Team confirmed the partner had renamed two CSV headers during a rollout.
- 2026-04-07T08:14:20Z: Partner resent the file with legacy headers restored.
- 2026-04-07T08:22:47Z: Replay succeeded and invoice generation restarted.
- 2026-04-07T08:41:10Z: Backlog cleared and finance support confirmed invoices were visible again.
