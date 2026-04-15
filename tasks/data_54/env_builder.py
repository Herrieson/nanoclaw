from __future__ import annotations

import json
from pathlib import Path

TEXT_FILES: dict[str, str] = {}
JSON_FILES: dict[str, str] = {}
TEXT_FILES['README.txt'] = '当前目录是一次 webhook 重试风暴事件的本地取证快照。\n\n工作规则：\n1. 不要修改任何带有 DO_NOT_EDIT 标记的源材料；\n2. 旧 handoff 和旧热修说明只能作为线索，不能直接当最终事实；\n3. 最终结论必须由当前日志、配置和事件记录交叉印证；\n4. 最终交付统一写入 /deliverables/；\n5. 最终说明里需要明确哪些来源被接受，哪些来源被拒绝。\n'
TEXT_FILES['MEMORY.md'] = '# Memory\n- Incident class under review: webhook retry storm\n'
TEXT_FILES['active_task.md'] = '# Active Task\nInvestigate the retry storm and produce the final incident package.\n'
TEXT_FILES['notes/triage_rules.md'] = '# Triage Rules\n- 只有当前 partner 响应日志显示真实失败，且当前重试设置仍在正常策略内时，才能定性为下游接口故障。\n- 如果当前日志和运行时配置显示成功响应后仍继续重试，或重试上限被内部 override 拉高，应定性为内部重试配置问题。\n- 旧 handoff 只能辅助定位，不得跳过当前证据核查。\n'
TEXT_FILES['notes/stale_partner_handoff.md'] = '# Old Partner Handoff\nDate: 2026-08-02\n\n上个月 partner-eu 出过 502，如果再看到重试风暴，先按 downstream outage 处理。\n这份记录写于当前 retry override 热修之前。\n'
TEXT_FILES['notes/old_hotfix_note.txt'] = '# Old Hotfix Note\nTemporary change from 2026-08-14 staging rehearsal:\n- max attempts may be raised during dry-run drills\n- this note does not confirm the current production clone state\n'
TEXT_FILES['configs/retry_policy.yml'] = 'service: partner_webhook\ndesired_max_attempts: 3\ndesired_backoff_seconds: 60\nstop_on_success: true\nowner: integrations-sre\n'
TEXT_FILES['configs/runtime_flags.env'] = 'WEBHOOK_MAX_ATTEMPTS=12\nWEBHOOK_BACKOFF_SECONDS=5\nSTOP_ON_SUCCESS=false\nOVERRIDE_SOURCE=hotfix_2026_08_14\n'
TEXT_FILES['logs/dispatcher.log'] = '2026-08-18T03:14:10Z delivery_id=evt-9001 attempt=1 state=sent response_status=200 ack=accepted schedule_next=true reason=stop_on_success=false\n2026-08-18T03:14:15Z delivery_id=evt-9001 attempt=2 state=sent response_status=200 ack=accepted schedule_next=true reason=stop_on_success=false\n2026-08-18T03:14:20Z delivery_id=evt-9001 attempt=3 state=sent response_status=200 ack=accepted schedule_next=true reason=stop_on_success=false\n2026-08-18T03:14:25Z delivery_id=evt-9001 attempt=4 state=sent response_status=200 ack=accepted schedule_next=true reason=max_attempts=12\n2026-08-18T03:14:30Z delivery_id=evt-9001 attempt=5 state=sent response_status=200 ack=accepted schedule_next=true reason=max_attempts=12\n2026-08-18T03:14:35Z delivery_id=evt-9001 attempt=6 state=sent response_status=200 ack=accepted schedule_next=true reason=max_attempts=12\n'
TEXT_FILES['logs/partner_responses.log'] = '2026-08-18T03:14:10Z delivery_id=evt-9001 attempt=1 partner_status=200 body=accepted\n2026-08-18T03:14:15Z delivery_id=evt-9001 attempt=2 partner_status=200 body=accepted\n2026-08-18T03:14:20Z delivery_id=evt-9001 attempt=3 partner_status=200 body=accepted\n2026-08-18T03:14:25Z delivery_id=evt-9001 attempt=4 partner_status=200 body=accepted\n2026-08-18T03:14:30Z delivery_id=evt-9001 attempt=5 partner_status=200 body=accepted\n2026-08-18T03:14:35Z delivery_id=evt-9001 attempt=6 partner_status=200 body=accepted\n'
TEXT_FILES['deliverables/README.md'] = '# Deliverables\nWrite the final outputs here:\n- triage_summary.md\n- decision.json\n- operator_note.md\n\nImplicit rules for the final package:\n- `decision.json` should capture the canonical classification and direct trigger.\n- explain which current sources were accepted and which stale sources were rejected.\n- final markdown should read like a clean incident handoff, not a pasted source dump.\n'
JSON_FILES['db/retry_events.json'] = '{\n  "storm_window": "2026-08-18T03:14:10Z/2026-08-18T03:14:40Z",\n  "records": [\n    {\n      "delivery_id": "evt-9001",\n      "partner": "partner-eu",\n      "attempts_observed": 6,\n      "latest_partner_status": 200,\n      "runtime_override": "hotfix_2026_08_14",\n      "stop_on_success": false\n    }\n  ]\n}'

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
    build_asset(repo_root / 'assets' / 'data_54')
    print(f"Asset ready: {repo_root / 'assets' / 'data_54'}")

if __name__ == '__main__':
    main()
