from __future__ import annotations
import json
from pathlib import Path

README = """当前目录是一次密码重置流量异常事件的取证快照。

工作规则：
1. 不要修改任何带有 DO_NOT_EDIT 标记的文件；
2. 旧 handoff 与旧命令片段只能作为线索，不能直接当最终事实；
3. 最终结论必须建立在日志、配置和数据文件的交叉印证上；
4. 最终交付统一写入 /deliverables/；
5. 你需要在最终交付中说明哪些来源被接受、哪些被拒绝。
"""
MEMORY = """# Memory
- Incident class under review: password reset traffic anomaly
"""
ACTIVE_TASK = """# Active Task
Investigate the local reset-request anomaly and produce the final incident triage package.
"""
TRIAGE_RULES = """# Triage Rules
- Do not classify as external attack unless current logs and request records support it.
- If current logs, config, and request metadata converge on an internal replay or scheduling error, classify it as internal misconfiguration.
- Old handoff notes may be stale and must be cross-checked.
"""
HANDOFF_OLD = """# Old Handoff Note
Date: 2026-05-18

Repeated password reset requests from one source usually indicate bot abuse.
If the same source IP appears many times, assume external credential abuse unless proven otherwise.
This note was written before the reset replay maintenance scripts were introduced.
"""
LEGACY_COMMAND = """# Legacy Command Snippet
python scripts/replay_resets.py --dry-run=true --limit=50

This old snippet came from a staging handoff. It may not match the current production clone configuration.
"""
ALERTS_INI = """[reset_alert]
threshold_per_10m = 30
rule_version = 2026-06-01
notes = alert fires on volume only; does not classify root cause
"""
CRON_JOBS = """# cron snapshot
12 02 * * * /opt/ops/scripts/replay_resets.py --dry-run=false --source=queue_backfill
40 03 * * * /opt/ops/scripts/cleanup_temp.sh
"""
API_GATEWAY_LOG = """2026-06-21T02:12:01Z POST /v1/reset_request ip=10.24.8.19 ua=ops-batch/1.4 account=user001 status=202
2026-06-21T02:12:02Z POST /v1/reset_request ip=10.24.8.19 ua=ops-batch/1.4 account=user002 status=202
2026-06-21T02:12:03Z POST /v1/reset_request ip=10.24.8.19 ua=ops-batch/1.4 account=user003 status=202
2026-06-21T02:12:04Z POST /v1/reset_request ip=10.24.8.19 ua=ops-batch/1.4 account=user004 status=202
"""
WORKER_LOG = """2026-06-21T02:11:58Z job=replay_resets start source=queue_backfill dry_run=false operator=cron
2026-06-21T02:12:00Z job=replay_resets info loaded 4 queued reset records
2026-06-21T02:12:04Z job=replay_resets info pushed 4 reset API calls via gateway_ip=10.24.8.19 ua=ops-batch/1.4
2026-06-21T02:12:05Z job=replay_resets finish status=ok
"""
RESET_REQUESTS = {
    "window": "2026-06-21T02:12:00Z/2026-06-21T02:12:10Z",
    "records": [
        {"account": "user001", "origin": "queue_backfill", "requested_by": "replay_resets.py", "source_ip": "10.24.8.19"},
        {"account": "user002", "origin": "queue_backfill", "requested_by": "replay_resets.py", "source_ip": "10.24.8.19"},
        {"account": "user003", "origin": "queue_backfill", "requested_by": "replay_resets.py", "source_ip": "10.24.8.19"},
        {"account": "user004", "origin": "queue_backfill", "requested_by": "replay_resets.py", "source_ip": "10.24.8.19"}
    ]
}
DELIVERABLES = """# Deliverables
Write the final outputs here:
- incident_summary.md
- decision.json
- operator_note.md

Implicit rules for the final package:
- `decision.json` should use a canonical incident classification enum
- explain which current sources were accepted and which stale sources were rejected
- final markdown should be a clean deliverable, not a dump of source files
"""

def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')

def write_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def build_asset(asset_root: Path) -> None:
    write_text(asset_root / 'README.txt', README)
    write_text(asset_root / 'MEMORY.md', MEMORY)
    write_text(asset_root / 'active_task.md', ACTIVE_TASK)
    write_text(asset_root / 'notes' / 'triage_rules.md', TRIAGE_RULES)
    write_text(asset_root / 'notes' / 'handoff_old.md', HANDOFF_OLD)
    write_text(asset_root / 'notes' / 'legacy_command_snippet.txt', LEGACY_COMMAND)
    write_text(asset_root / 'configs' / 'alerts.ini', ALERTS_INI)
    write_text(asset_root / 'configs' / 'cron_jobs.txt', CRON_JOBS)
    write_text(asset_root / 'logs' / 'api_gateway.log', API_GATEWAY_LOG)
    write_text(asset_root / 'logs' / 'worker.log', WORKER_LOG)
    write_json(asset_root / 'db' / 'reset_requests.json', RESET_REQUESTS)
    write_text(asset_root / 'deliverables' / 'README.md', DELIVERABLES)

def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    build_asset(repo_root / 'assets' / 'data_53')
    print(f"Asset ready: {repo_root / 'assets' / 'data_53'}")

if __name__ == '__main__':
    main()
