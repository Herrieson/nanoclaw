from __future__ import annotations
import json
from pathlib import Path

TEXT_FILES = {'README.txt': '当前目录是一次订阅拒付分类复核快照。\n'
               '\n'
               '工作规则：\n'
               '1. 不要修改原始证据文件；\n'
               '2. 旧流失手册只能当背景，不能覆盖当前计费配置和事件记录；\n'
               '3. 结论必须建立在配置、发布日志和扣费事件的交叉印证上；\n'
               '4. 最终交付统一写入 /deliverables/；\n'
               '5. 最终说明里需要交代哪些来源被接受、哪些被拒绝。\n',
 'MEMORY.md': '# Memory\n'
              '- Queue: renewal chargeback review\n'
              '- Refund ops asked for clearer classification this week\n',
 'active_task.md': '# Active Task\n'
                   'Audit the chargeback cluster and prepare the final classification package.\n',
 'notes/triage_rules.md': '# Triage Rules\n'
                          '- 先看当前计费配置和重复扣费事件，再看旧流失经验。\n'
                          '- 如果同一续费窗口里出现重复扣费并触发拒付，优先考虑系统回归。\n'
                          '- 没有取消或自助流失证据时，不要直接归为正常 churn。\n',
 'notes/old_churn_playbook.md': '# Old Churn Playbook\n'
                                '更新时间：2026-06-08\n'
                                '\n'
                                '续费后 14 天内的拒付，多数可以按正常流失归档。\n'
                                '这份手册写在 retry guard 改版之前，也没有覆盖重复扣费场景。\n',
 'data/chargebacks.csv': 'account_id,renewal_id,first_charge_ts,second_charge_ts,chargeback_reason,status\n'
                         'acct_401,RN-401,2026-09-03T02:00:01Z,2026-09-03T02:02:13Z,duplicate '
                         'charge,open\n'
                         'acct_402,RN-402,2026-09-03T02:05:09Z,2026-09-03T02:06:41Z,duplicate '
                         'charge,open\n'
                         'acct_403,RN-403,2026-09-03T02:09:55Z,2026-09-03T02:12:02Z,duplicate '
                         'charge,open\n'
                         'acct_404,RN-404,2026-09-03T02:14:18Z,2026-09-03T02:16:11Z,duplicate '
                         'charge,open\n',
 'logs/release_changes.log': '2026-09-03T01:40:00Z release=billing-2026.09.03 status=deployed\n'
                             '2026-09-03T01:41:12Z note=retry_guard_minutes default accidentally '
                             'set to 0 in production override\n'
                             '2026-09-03T01:42:03Z note=idempotency warning suppressed for '
                             'catch-up renewals\n',
 'deliverables/README.md': '# Deliverables\n'
                           '请在这里写最终输出：\n'
                           '- chargeback_audit.md\n'
                           '- decision.json\n'
                           '- refund_ops_note.md\n'
                           '\n'
                           '隐含要求：\n'
                           '- `decision.json` 需要使用规范决策枚举，并记录 accepted_sources 与 rejected_sources\n'
                           '- 最终结论要说明为什么这不是正常 churn\n'
                           '- 交付内容要像退款运营可以直接参考的成品\n'}
JSON_FILES = {'configs/billing_retry_rules.json': {'release': '2026.09.03',
                                      'retry_guard_minutes': 0,
                                      'intended_retry_guard_minutes': 1440,
                                      'catch_up_mode': 'enabled',
                                      'idempotency_override': 'suppressed'},
 'data/subscription_events.json': {'window': '2026-09-03T02:00:00Z/2026-09-03T02:20:00Z',
                                   'accounts': [{'account_id': 'acct_401',
                                                 'cancelled': False,
                                                 'renewal_attempts': 2},
                                                {'account_id': 'acct_402',
                                                 'cancelled': False,
                                                 'renewal_attempts': 2},
                                                {'account_id': 'acct_403',
                                                 'cancelled': False,
                                                 'renewal_attempts': 2},
                                                {'account_id': 'acct_404',
                                                 'cancelled': False,
                                                 'renewal_attempts': 2}]}}


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
    build_asset(repo_root / "assets" / "data_64")
    print(f"Asset ready: {repo_root / 'assets' / 'data_64'}")


if __name__ == "__main__":
    main()
