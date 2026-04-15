from __future__ import annotations
import json
from pathlib import Path

TEXT_FILES = {'README.txt': '当前目录是一次发票差额复核快照。\n'
               '\n'
               '工作规则：\n'
               '1. 不要修改原始证据文件；\n'
               '2. 旧手册和口头猜测都不能直接当结论；\n'
               '3. 结论必须建立在采购单、发票行项目和当前税务说明的交叉印证上；\n'
               '4. 最终交付统一写入 /deliverables/；\n'
               '5. 最终说明里需要交代哪些来源被接受、哪些被拒绝。\n',
 'MEMORY.md': '# Memory\n'
              '- Queue: vendor invoice checks\n'
              '- Escalation risk rises if mismatch reason is not documented\n',
 'active_task.md': '# Active Task\n'
                   'Audit the invoice mismatch and prepare the finance response package.\n',
 'notes/triage_rules.md': '# Triage Rules\n'
                          '- 先对齐采购单与发票行项目，再看税率说明。\n'
                          '- 如果当前税务说明已经更新，就不能继续沿用旧手册默认税率。\n'
                          '- 没有证据时，不要把差额直接归因为供应商填错。\n',
 'notes/stale_manual_excerpt.md': '# Stale Manual Excerpt\n'
                                  '更新时间：2026-03-11\n'
                                  '\n'
                                  '实施支持和订阅服务统一按 13% 增值税处理。\n'
                                  '这份手册写在服务税目拆分前。\n',
 'notes/accounting_guess.txt': 'Accounting guess from hallway chat:\n'
                               '看起来像供应商把税额敲错了，先按 vendor typo 处理也行。\n'
                               'No ticket or supporting calc attached.\n',
 'finance/po_line_items.csv': 'line_item,net_amount_cny,expected_tax_rate_from_po\n'
                              'monthly_subscription,2000,0.13\n'
                              'implementation_support,1000,0.13\n',
 'finance/invoice_line_items.csv': 'line_item,net_amount_cny,applied_tax_rate,invoice_total_cny\n'
                                   'monthly_subscription,2000,0.13,2260\n'
                                   'implementation_support,1000,0.06,1060\n',
 'finance/tax_adjustment_note.md': '# Tax Adjustment Note\n'
                                   '生效日期：2026-08-01\n'
                                   '\n'
                                   '实施支持服务从本月开始按 6% 服务税目开票；\n'
                                   '订阅服务仍按 13% 税率处理。\n'
                                   '如果按旧手册统一套 13%，总额会比实际发票高 70 元。\n',
 'deliverables/README.md': '# Deliverables\n'
                           '请在这里写最终输出：\n'
                           '- mismatch_report.md\n'
                           '- decision.json\n'
                           '- finance_reply.md\n'
                           '\n'
                           '隐含要求：\n'
                           '- `decision.json` 需要使用规范决策枚举，并记录 accepted_sources 与 rejected_sources\n'
                           '- 最终结论要给出差额金额和真正原因\n'
                           '- 交付内容要像发给财务的成品，不要直接贴原始表格\n'}
JSON_FILES = {'finance/invoice_header.json': {'invoice_no': 'INV-8821',
                                 'po_reference': 'PO-2041',
                                 'subtotal_cny': 3000,
                                 'invoice_total_cny': 3320}}


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
    build_asset(repo_root / "assets" / "data_63")
    print(f"Asset ready: {repo_root / 'assets' / 'data_63'}")


if __name__ == "__main__":
    main()
