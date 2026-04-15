# Triage Rules
- 只有当当前 upstream 落地记录和 landing manifest 同时缺少目标 partition 时，才能定性为 upstream missing data。
- 如果 upstream 文件已经落地，而本地 runner 因 scheduler/window 时区配置查错 partition，应定性为本地调度或时区问题。
- 旧 blame note 和手工表格只能作为线索，不得代替当前证据。
