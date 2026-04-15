from __future__ import annotations

import json
from pathlib import Path

TEXT_FILES: dict[str, str] = {}
JSON_FILES: dict[str, str] = {}
TEXT_FILES['README.txt'] = '当前目录是一次合同 amendment 适用性核对任务的本地资料快照。\n\n工作规则：\n1. 不要修改任何带有 DO_NOT_EDIT 标记的源材料；\n2. 未签 draft 和旧摘要不能直接覆盖已签文件；\n3. 最终结论必须由主协议、已签 amendment 和当前续约材料交叉印证；\n4. 最终交付统一写入 /deliverables/；\n5. 交付中需要说明哪些来源被接受、哪些来源被拒绝。\n'
TEXT_FILES['MEMORY.md'] = '# Memory\n- Task under review: contract amendment applicability\n'
TEXT_FILES['active_task.md'] = '# Active Task\nDetermine whether the signed amendment applies to the renewal case.\n'
TEXT_FILES['notes/triage_rules.md'] = '# Triage Rules\n- 已签 amendment 在生效日期和适用范围命中当前 case 时，应优先于旧摘要和旧口头结论。\n- 未签 draft 不能单独产生约束力。\n- 必须同时确认签署状态、覆盖范围和当前 renewal case 的时间/产品匹配。\n'
TEXT_FILES['notes/old_summary.md'] = '# Old Summary\nRenewal cap stays at 8% under section 4 of the master agreement.\nThis summary was drafted before Amendment 02 was fully executed.\n'
TEXT_FILES['contracts/master_agreement.md'] = '# Master Agreement\nSection 4. Renewal Pricing\n- Default annual renewal cap: 8%\n- Unless superseded by a later fully executed amendment.\n'
TEXT_FILES['contracts/amendments/amendment_02_signed.md'] = '# Amendment 02 (Signed)\nExecution date: 2026-02-03\nSigned by both parties: yes\n\nEffective for enterprise support renewals on or after 2026-03-01.\nSection 4 renewal cap is replaced with 3% for covered renewals.\n'
TEXT_FILES['contracts/amendments/amendment_02_draft.md'] = '# Amendment 02 Draft\nStatus: draft only\nProposed 3% cap for enterprise support renewals.\nThis draft predates signature collection.\n'
TEXT_FILES['contracts/order_form.md'] = '# Current Order Form\nCustomer: BlueHarbor\nProduct: enterprise support\nRenewal term start: 2026-08-01\n'
TEXT_FILES['deliverables/README.md'] = '# Deliverables\nWrite the final outputs here:\n- applicability_summary.md\n- applicability_decision.json\n- counsel_note.md\n\nImplicit rules for the final package:\n- `applicability_decision.json` should capture whether the signed amendment applies and why stale sources were rejected.\n- explain which current sources were accepted and which stale sources were rejected.\n- final markdown should read like a clean legal handoff, not a pasted source dump.\n'
JSON_FILES['intake/renewal_case.json'] = '{\n  "customer": "BlueHarbor",\n  "product": "enterprise support",\n  "renewal_date": "2026-08-01",\n  "question": "Does Amendment 02 control this renewal?"\n}'

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
    build_asset(repo_root / 'assets' / 'data_59')
    print(f"Asset ready: {repo_root / 'assets' / 'data_59'}")

if __name__ == '__main__':
    main()
