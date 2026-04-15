# Schema Change Note
生效时间：2026-09-15 00:00 UTC

投放最终 KPI 从 signup_complete 切换到 lead_submit。
迁移后 signup_complete 将不再回填，旧字段会保持 0；
所有日常报表导出都应改读 lead_submit。
