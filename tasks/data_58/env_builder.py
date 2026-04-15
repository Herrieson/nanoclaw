from __future__ import annotations

import json
from pathlib import Path

TEXT_FILES: dict[str, str] = {}
JSON_FILES: dict[str, str] = {}
TEXT_FILES['README.txt'] = '当前目录是一次供应商联络路由核对任务的本地资料快照。\n\n工作规则：\n1. 不要修改任何带有 DO_NOT_EDIT 标记的源材料；\n2. 联系人签名和旧组织说明只能作为线索，不能直接覆盖当前 owner 记录；\n3. 最终结论必须由当前 ownership 记录、handover 和供应商档案交叉印证；\n4. 最终交付统一写入 /deliverables/；\n5. 交付中需要说明哪些来源被接受、哪些来源被拒绝。\n'
TEXT_FILES['MEMORY.md'] = '# Memory\n- Task under review: vendor contact routing audit\n'
TEXT_FILES['active_task.md'] = '# Active Task\nDetermine the current vendor owner and prepare the final routing package.\n'
TEXT_FILES['notes/triage_rules.md'] = '# Triage Rules\n- 当前 owner 应由 active ownership matrix、vendor record 和 current handover 共同确认。\n- 邮件签名、旧 org note、历史抄送习惯只能作为线索，不能直接决定最终收件人。\n- 如果当前资料一致指向新的 owner，应拒绝沿用旧联系人。\n'
TEXT_FILES['notes/old_org_note.md'] = '# Old Org Note\nIris Shen used to handle Northstar Systems when the vendor sat under legacy sourcing.\nThis note predates the 2026-07-01 ownership transfer.\n'
TEXT_FILES['mail/stale_signature.txt'] = 'From an old thread:\nIris Shen | Vendor Operations\niris.shen@acme.example\n"If Northstar needs anything, send it to me directly."\n'
TEXT_FILES['mail/current_handover.md'] = '# Current Handover\nEffective date: 2026-07-01\n\nNorthstar Systems moved from Iris Shen to Lin Qiao.\nNew owner email: lin.qiao@acme.example\nReason: supplier portfolio realignment.\n'
TEXT_FILES['ops/ownership_matrix.csv'] = 'vendor,portfolio,owner_name,owner_email,status,effective_date\nNorthstar Systems,core-platform,Lin Qiao,lin.qiao@acme.example,active,2026-07-01\nEastJet Printing,field-ops,Wen Yu,wen.yu@acme.example,active,2026-05-20\n'
TEXT_FILES['contacts/vendor_directory.csv'] = 'vendor,primary_alias,region,last_refresh\nNorthstar Systems,northstar-ops@vendor.example,APAC,2026-08-10\nEastJet Printing,eastjet@vendor.example,APAC,2026-08-08\n'
TEXT_FILES['deliverables/README.md'] = '# Deliverables\nWrite the final outputs here:\n- routing_summary.md\n- routing_decision.json\n- vendor_message.md\n\nImplicit rules for the final package:\n- `routing_decision.json` should capture the chosen owner and why stale sources were rejected.\n- explain which current sources were accepted and which stale sources were rejected.\n- final markdown should read like a clean routing handoff, not a pasted source dump.\n'
JSON_FILES['db/vendor_record.json'] = '{\n  "vendor": "Northstar Systems",\n  "portfolio": "core-platform",\n  "current_contact_owner": "Lin Qiao",\n  "current_contact_email": "lin.qiao@acme.example",\n  "last_transition": "2026-07-01"\n}'

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
    build_asset(repo_root / 'assets' / 'data_58')
    print(f"Asset ready: {repo_root / 'assets' / 'data_58'}")

if __name__ == '__main__':
    main()
