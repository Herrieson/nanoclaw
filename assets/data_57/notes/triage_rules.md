# Triage Rules
- 如果当前表单日志显示同一表单 token 被用户重复提交，并生成不同 request_id，才能定性为 user double submit。
- 如果表单侧只有一次提交，但 sync consumer 重复处理同一 message_id，且幂等配置未真正拦截重复消费，应定性为 sync consumer idempotency bug。
- 旧经验和 war-room 初判只能辅助搜索，不能代替当前证据。
