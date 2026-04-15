from __future__ import annotations
import json
from pathlib import Path

TEXT_FILES = {'README.txt': '当前目录是一次预算超支归因复核快照。\n'
               '\n'
               '工作规则：\n'
               '1. 不要修改原始证据文件；\n'
               '2. 旧 baseline 快照只能当线索，不能覆盖当前批准版本；\n'
               '3. 结论必须建立在当前 baseline、实际支出和批准备注的交叉印证上；\n'
               '4. 最终交付统一写入 /deliverables/；\n'
               '5. 最终说明里需要交代哪些来源被接受、哪些被拒绝。\n',
 'MEMORY.md': '# Memory\n'
              '- Program: family-day operations\n'
              '- Finance wants one agreed overrun explanation\n',
 'active_task.md': '# Active Task\n'
                   'Audit the budget overrun narrative and prepare the final attribution '
                   'package.\n',
 'notes/triage_rules.md': '# Triage Rules\n'
                          '- 先对齐当前 baseline，再看实际支出。\n'
                          '- 如果 dashboard 仍指向旧 baseline，不能直接拿旧差额当责任结论。\n'
                          '- 已批准的供应商切换要和未批准的失控支出区分开。\n',
 'notes/stale_baseline_snapshot.csv': 'category,amount_cny,version\n'
                                      'venue,52000,v1\n'
                                      'catering,39000,v1\n'
                                      'activity_materials,19000,v1\n'
                                      'av_vendor,15000,v1\n'
                                      'staffing,8000,v1\n',
 'notes/vendor_switch_approval.md': '# Vendor Switch Approval\n'
                                    '审批日期：2026-08-18\n'
                                    '\n'
                                    '因为场地新增安全布线要求，AV 供应商从 LightBox 改为 SafeStage。\n'
                                    '批准追加金额：3000 元。\n'
                                    '该追加已经包含在当前 baseline 评审后的执行口径里。\n',
 'finance/current_baseline.csv': 'category,amount_cny,version\n'
                                 'venue,54000,v2\n'
                                 'catering,42000,v2\n'
                                 'activity_materials,21000,v2\n'
                                 'av_vendor,18000,v2\n'
                                 'staffing,13000,v2\n',
 'finance/actuals_august.csv': 'category,amount_cny\n'
                               'venue,54000\n'
                               'catering,42000\n'
                               'activity_materials,21000\n'
                               'av_vendor,21000\n'
                               'staffing,13000\n',
 'logs/budget_sync.log': '2026-08-20T08:12:00Z dashboard=family_day_budget note=cache still '
                         'serving baseline_v1\n'
                         '2026-08-20T08:12:11Z baseline_v2_total=148000 actual_snapshot=151000\n'
                         '2026-08-20T08:12:44Z warning=owner view still labels variance against '
                         'stale 133000 snapshot\n',
 'deliverables/README.md': '# Deliverables\n'
                           '请在这里写最终输出：\n'
                           '- budget_attribution.md\n'
                           '- decision.json\n'
                           '- manager_note.md\n'
                           '\n'
                           '隐含要求：\n'
                           '- `decision.json` 需要使用规范决策枚举，并记录 accepted_sources 与 rejected_sources\n'
                           '- 最终结论要给出当前 baseline、最终实际支出和真实差额解释\n'
                           '- 交付内容要像给负责人复盘用的成品\n'}
JSON_FILES = {}


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
    build_asset(repo_root / "assets" / "data_65")
    print(f"Asset ready: {repo_root / 'assets' / 'data_65'}")


if __name__ == "__main__":
    main()
