# Hotfix Window
- 允许在不重启整套服务的情况下修改 notifier feature flag
- 如果只涉及 `enable_delta_cache`，可走单点配置修正，不需要整包回滚
- 本次值班窗口允许 10 分钟内完成热修
