from __future__ import annotations

import json
from pathlib import Path

TEXT_FILES: dict[str, str] = {}
JSON_FILES: dict[str, str] = {}
TEXT_FILES['README.txt'] = '当前目录是一次重复工单洪峰事件的本地取证快照。\n\n工作规则：\n1. 不要修改任何带有 DO_NOT_EDIT 标记的源材料；\n2. 旧前端经验和旧 war-room 结论不能直接当最终事实；\n3. 最终结论必须由表单日志、队列事件、消费端日志和幂等配置交叉印证；\n4. 最终交付统一写入 /deliverables/；\n5. 交付中需要说明哪些来源被接受、哪些来源被拒绝。\n'
TEXT_FILES['MEMORY.md'] = '# Memory\n- Incident class under review: duplicate ticket flood\n'
TEXT_FILES['active_task.md'] = '# Active Task\nInvestigate the duplicate ticket flood and produce the final root-cause package.\n'
TEXT_FILES['notes/triage_rules.md'] = '# Triage Rules\n- 如果当前表单日志显示同一表单 token 被用户重复提交，并生成不同 request_id，才能定性为 user double submit。\n- 如果表单侧只有一次提交，但 sync consumer 重复处理同一 message_id，且幂等配置未真正拦截重复消费，应定性为 sync consumer idempotency bug。\n- 旧经验和 war-room 初判只能辅助搜索，不能代替当前证据。\n'
TEXT_FILES['notes/old_frontend_note.md'] = '# Old Frontend Note\n用户双击提交表单以前发生过，看到重复票时可以先按 double submit 处理。\n这份说明写于当前 support sync 重构之前。\n'
TEXT_FILES['notes/stale_war_room.txt'] = 'War-room first guess:\n"Probably user kept clicking submit."\n'
TEXT_FILES['configs/idempotency.yml'] = 'consumer: support_sync\nmode: observe_only\nttl_seconds: 0\nowner: support-platform\n'
TEXT_FILES['logs/web_form.log'] = '2026-09-12T08:40:01Z POST /support/submit request_id=req-701 form_token=ft-884 customer=BlueHarbor issue=refund_blocked status=202\n2026-09-12T08:40:02Z POST /support/submit request_id=req-701 form_token=ft-884 customer=BlueHarbor issue=refund_blocked status=202 note=client_reused_connection\n'
TEXT_FILES['logs/sync_consumer.log'] = '2026-09-12T08:40:03Z consumer=support_sync message_id=msg-912 action=create_ticket ticket_id=T-4401 dedupe=miss mode=observe_only\n2026-09-12T08:40:05Z consumer=support_sync message_id=msg-912 action=create_ticket ticket_id=T-4402 dedupe=observed_only mode=observe_only retry_reason=ack_timeout\n2026-09-12T08:40:06Z consumer=support_sync message_id=msg-912 action=finish duplicates=2\n'
TEXT_FILES['queues/support_events.jsonl'] = '{"message_id":"msg-912","request_id":"req-701","form_token":"ft-884","customer":"BlueHarbor","attempt":1}\n{"message_id":"msg-912","request_id":"req-701","form_token":"ft-884","customer":"BlueHarbor","attempt":2}\n'
TEXT_FILES['deliverables/README.md'] = '# Deliverables\nWrite the final outputs here:\n- root_cause_summary.md\n- decision.json\n- ops_note.md\n\nImplicit rules for the final package:\n- `decision.json` should capture the canonical classification and direct trigger.\n- explain which current sources were accepted and which stale sources were rejected.\n- final markdown should read like a clean support incident handoff, not a pasted source dump.\n'
JSON_FILES['db/submission_events.json'] = '{\n  "window": "2026-09-12T08:40:00Z/2026-09-12T08:40:10Z",\n  "submissions": [\n    {\n      "request_id": "req-701",\n      "form_token": "ft-884",\n      "customer": "BlueHarbor",\n      "user_submit_count": 1,\n      "message_id": "msg-912"\n    }\n  ]\n}'

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
    build_asset(repo_root / 'assets' / 'data_57')
    print(f"Asset ready: {repo_root / 'assets' / 'data_57'}")

if __name__ == '__main__':
    main()
