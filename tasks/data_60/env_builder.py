from __future__ import annotations

import json
from pathlib import Path

TEXT_FILES: dict[str, str] = {}
JSON_FILES: dict[str, str] = {}
TEXT_FILES['README.txt'] = '当前目录是一次 shipment escalation 收件人核对任务的本地资料快照。\n\n工作规则：\n1. 不要修改任何带有 DO_NOT_EDIT 标记的源材料；\n2. 旧组织图和旧签名只能作为线索，不能直接当最终收件人依据；\n3. 最终结论必须由当前区域映射、current roster、handover 和 case 信息交叉印证；\n4. 最终交付统一写入 /deliverables/；\n5. 交付中需要说明哪些来源被接受、哪些来源被拒绝。\n'
TEXT_FILES['MEMORY.md'] = '# Memory\n- Task under review: shipment escalation recipient check\n'
TEXT_FILES['active_task.md'] = '# Active Task\nDetermine the correct shipment escalation recipient and prepare the final handoff package.\n'
TEXT_FILES['notes/triage_rules.md'] = '# Triage Rules\n- 最终升级收件人应由 shipment case 对应的 region mapping 和 current region roster 共同决定。\n- coverage rotation 和 current handover 可以辅助确认当前责任人，但旧组织图和旧签名不能覆盖当前 roster。\n- 如果当前资料一致指向新的区域 owner，应拒绝沿用旧联系人。\n'
TEXT_FILES['notes/coverage_rotation.md'] = '# Coverage Rotation\nWeek of 2026-09-14\n- southeast_asia primary owner: Mei Sun\n- southeast_asia backup: Arun Das\n- use primary owner for standard escalation routing\n'
TEXT_FILES['notes/stale_org_chart.md'] = '# Stale Org Chart Note\nKelvin Tan was listed as Southeast Asia escalation owner in the 2025 org chart.\nThis note predates the 2026 regional consolidation.\n'
TEXT_FILES['mail/old_signature.txt'] = 'Kelvin Tan\nRegional Escalations\nkelvin.tan@logix.example\n"Send SEA urgent issues straight to me."\n'
TEXT_FILES['mail/current_handover.md'] = '# Current Handover\nEffective 2026-08-01, Southeast Asia escalations moved to Mei Sun.\nOwner email: mei.sun@logix.example\nKelvin Tan remains archived in older org references only.\n'
TEXT_FILES['configs/region_map.yml'] = 'region_codes:\n  SEA-SG: southeast_asia\n  SEA-ID: southeast_asia\n  APAC-JP: japan\n'
TEXT_FILES['ops/current_region_roster.csv'] = 'region,owner_name,owner_email,status,effective_date\nsoutheast_asia,Mei Sun,mei.sun@logix.example,active,2026-08-01\njapan,Ren Ito,ren.ito@logix.example,active,2026-06-01\n'
TEXT_FILES['deliverables/README.md'] = '# Deliverables\nWrite the final outputs here:\n- recipient_summary.md\n- recipient_decision.json\n- escalation_message.md\n\nImplicit rules for the final package:\n- `recipient_decision.json` should capture the chosen regional owner and why stale sources were rejected.\n- explain which current sources were accepted and which stale sources were rejected.\n- final markdown should read like a clean escalation handoff, not a pasted source dump.\n'
JSON_FILES['cases/shipment_case.json'] = '{\n  "shipment_id": "SHP-22018",\n  "region_code": "SEA-SG",\n  "lane": "SGP-JKT",\n  "priority": "high",\n  "issue": "customs hold exceeded SLA"\n}'

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
    build_asset(repo_root / 'assets' / 'data_60')
    print(f"Asset ready: {repo_root / 'assets' / 'data_60'}")

if __name__ == '__main__':
    main()
