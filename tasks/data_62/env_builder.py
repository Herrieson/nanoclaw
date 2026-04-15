from __future__ import annotations
import json
from pathlib import Path

TEXT_FILES = {'README.txt': '当前目录是一次报销争议复核快照。\n'
               '\n'
               '工作规则：\n'
               '1. 不要修改原始证据文件；\n'
               '2. 旧 FAQ 捷径只能当背景，不能直接替代现行政策；\n'
               '3. 结论必须建立在现行政策、报销明细和审批记录的交叉印证上；\n'
               '4. 最终交付统一写入 /deliverables/；\n'
               '5. 最终说明里需要交代哪些来源被接受、哪些被拒绝。\n',
 'MEMORY.md': '# Memory\n'
              '- Queue: travel reimbursement disputes\n'
              '- Reviewer macro complaints increased this week\n',
 'active_task.md': '# Active Task\n'
                   'Audit the reimbursement dispute and produce the final resolution package.\n',
 'notes/triage_rules.md': '# Triage Rules\n'
                          '- 先用现行政策判断每个明细，再看旧 FAQ 是否已经过期。\n'
                          '- 混合票据不等于整单否决；要区分可报和不可报部分。\n'
                          '- 审核日志可以帮助定位争议是政策问题还是执行 shortcut 问题。\n',
 'notes/old_faq_shortcut.md': '# Old FAQ Shortcut\n'
                              '更新时间：2026-05-20\n'
                              '\n'
                              '如果一张票据同时出现酒精或电子配件，审核模板可以直接把整单打回，避免拆分计算。\n'
                              '这条 FAQ 写在 demo 配件补贴政策上线之前。\n',
 'policies/current_reimbursement_policy.md': '# Current Reimbursement Policy\n'
                                             '1. 与出差行程相关的交通费用，在有行程单和票据时可报。\n'
                                             '2. 客户餐叙中的餐食部分可报，酒精部分不可报。\n'
                                             '3. 用于现场演示的低值转接器或配件，单项不超过 100 元且有出差审批时可报。\n'
                                             '4. 不要因为一项不可报就整单否决；需要拆分明细后处理。\n',
 'approvals/travel_approval.txt': 'Trip code: FD-204\n'
                                  'Approved traveler: lin.shu\n'
                                  'Purpose: family-day partner demo and venue walk-through\n'
                                  'Approved extras: demo adapter under 100 CNY\n',
 'logs/reviewer_bot.log': '2026-08-02T10:11:02Z claim=RB-204 parser=ok items=4\n'
                          '2026-08-02T10:11:03Z claim=RB-204 macro=faq_shortcut_v1 reason=mixed '
                          'receipt contains alcohol and electronics\n'
                          '2026-08-02T10:11:03Z claim=RB-204 action=deny_full_claim\n',
 'deliverables/README.md': '# Deliverables\n'
                           '请在这里写最终输出：\n'
                           '- reimbursement_audit.md\n'
                           '- decision.json\n'
                           '- reviewer_note.md\n'
                           '\n'
                           '隐含要求：\n'
                           '- `decision.json` 需要使用规范决策枚举，并记录 accepted_sources 与 rejected_sources\n'
                           '- 最终结论要明确给出可报金额和争议来源\n'
                           '- 交付内容要像复核结果，不要直接复制政策全文\n'}
JSON_FILES = {'claims/reimbursement_claim.json': {'claim_id': 'RB-204',
                                     'employee': 'lin.shu',
                                     'trip_code': 'FD-204',
                                     'total_claimed_cny': 302,
                                     'items': [{'item': 'airport_taxi',
                                                'amount_cny': 86,
                                                'policy_tag': 'transit',
                                                'receipt_id': 'R-101'},
                                               {'item': 'client_dinner_food',
                                                'amount_cny': 132,
                                                'policy_tag': 'client_meal_food',
                                                'receipt_id': 'R-102'},
                                               {'item': 'client_dinner_wine',
                                                'amount_cny': 36,
                                                'policy_tag': 'alcohol',
                                                'receipt_id': 'R-102'},
                                               {'item': 'hdmi_adapter',
                                                'amount_cny': 48,
                                                'policy_tag': 'demo_accessory',
                                                'receipt_id': 'R-103'}]}}


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_asset(asset_root: Path) -> None:
    for relative_path, content in TEXT_FILES.items():
        write_text(asset_root / relative_path, content)
    for relative_path, payload in JSON_FILES.items():
        write_json(asset_root / relative_path, payload)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    build_asset(repo_root / "assets" / "data_62")
    print(f"Asset ready: {repo_root / 'assets' / 'data_62'}")


if __name__ == "__main__":
    main()
