from __future__ import annotations

import json
from pathlib import Path

TEXT_FILES: dict[str, str] = {}
JSON_FILES: dict[str, str] = {}
TEXT_FILES['README.txt'] = '当前目录是一次访问尖峰事件的本地取证快照。\n\n工作规则：\n1. 不要修改任何带有 DO_NOT_EDIT 标记的源材料；\n2. 不要把旧攻击 playbook 直接当成本次结论；\n3. 最终结论必须由当前边缘日志、批量作业记录、内网来源信息和请求样本交叉印证；\n4. 最终交付统一写入 /deliverables/；\n5. 交付中需要说明哪些来源被接受、哪些来源被拒绝。\n'
TEXT_FILES['MEMORY.md'] = '# Memory\n- Incident class under review: access spike classification\n'
TEXT_FILES['active_task.md'] = '# Active Task\nInvestigate the access spike and produce the final security handoff package.\n'
TEXT_FILES['notes/triage_rules.md'] = '# Triage Rules\n- 只有当前访问日志出现真实攻击特征、且来源不属于内部已知批任务或内网出口时，才能定性为 external attack。\n- 如果 user-agent、NAT 出口、批任务日志和请求样本一致指向内部 replay，应定性为 internal batch replay。\n- 旧 playbook 和 pager 初判只能辅助搜索，不能代替当前证据。\n'
TEXT_FILES['notes/old_abuse_playbook.md'] = '# Old Abuse Playbook\n同一 IP 在 10 分钟内超过 100 次访问时，默认按 attack 处理。\n这份 playbook 写于 archive replay 作业接入之前。\n'
TEXT_FILES['notes/pager_message.txt'] = 'Pager first look:\n"Looks like scraping from one IP, probably block it."\n'
TEXT_FILES['configs/batch_jobs.txt'] = '# batch schedule snapshot\n10 03 * * * /opt/jobs/archive_replay.sh --source=history_export --limit=120\n45 03 * * * /opt/jobs/purge_temp.sh\n'
TEXT_FILES['configs/nat_allowlist.txt'] = '10.77.5.14 corp-nat-replay\n10.77.5.20 corp-nat-dataops\n'
TEXT_FILES['logs/access_edge.log'] = '2026-09-10T03:10:11Z GET /download/report ip=10.77.5.14 ua=history-replay/2.1 actor=svc-analytics status=200\n2026-09-10T03:10:12Z GET /download/report ip=10.77.5.14 ua=history-replay/2.1 actor=svc-analytics status=200\n2026-09-10T03:10:13Z GET /download/report ip=10.77.5.14 ua=history-replay/2.1 actor=svc-analytics status=200\n2026-09-10T03:10:14Z GET /download/report ip=10.77.5.14 ua=history-replay/2.1 actor=svc-analytics status=200\n2026-09-10T03:10:15Z GET /download/report ip=10.77.5.14 ua=history-replay/2.1 actor=svc-analytics status=200\n'
TEXT_FILES['logs/replay_worker.log'] = '2026-09-10T03:10:00Z job=archive_replay start source=history_export limit=120\n2026-09-10T03:10:05Z job=archive_replay info using_nat=10.77.5.14 ua=history-replay/2.1\n2026-09-10T03:10:16Z job=archive_replay finish emitted_checks=120 status=ok\n'
TEXT_FILES['deliverables/README.md'] = '# Deliverables\nWrite the final outputs here:\n- access_summary.md\n- decision.json\n- security_note.md\n\nImplicit rules for the final package:\n- `decision.json` should capture the canonical classification and direct trigger.\n- explain which current sources were accepted and which stale sources were rejected.\n- final markdown should read like a clean security handoff, not a pasted source dump.\n'
JSON_FILES['db/request_samples.json'] = '{\n  "window": "2026-09-10T03:10:10Z/2026-09-10T03:10:20Z",\n  "samples": [\n    {\n      "path": "/download/report",\n      "source_ip": "10.77.5.14",\n      "user_agent": "history-replay/2.1",\n      "actor": "svc-analytics",\n      "internal_replay": true\n    }\n  ]\n}'

def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')

def write_json(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.loads(content)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def build_asset(asset_root: Path) -> None:
    for relative_path, content in TEXT_FILES.items():
        write_text(asset_root / relative_path, content)
    for relative_path, content in JSON_FILES.items():
        write_json(asset_root / relative_path, content)

def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    build_asset(repo_root / 'assets' / 'data_56')
    print(f"Asset ready: {repo_root / 'assets' / 'data_56'}")

if __name__ == '__main__':
    main()
