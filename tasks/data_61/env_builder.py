from __future__ import annotations
import json
from pathlib import Path

TEXT_FILES = {'README.txt': '当前目录是一次家庭开放日活动场地冲突的审计快照。\n'
               '\n'
               '工作规则：\n'
               '1. 不要修改原始证据文件；\n'
               '2. 旧场地总结只能当线索，不能直接当最终依据；\n'
               '3. 当前消防限制、最新到场人数、现场布局优先级更高；\n'
               '4. 最终交付统一写入 /deliverables/；\n'
               '5. 最终说明里需要交代哪些来源被接受、哪些被拒绝。\n',
 'MEMORY.md': '# Memory\n- Event: family open day\n- Decision window: today before 18:00\n',
 'active_task.md': '# Active Task\n'
                   'Audit the venue conflict and prepare the final venue recommendation package.\n',
 'notes/triage_rules.md': '# Triage Rules\n'
                          '- 先看最新 headcount、消防限制和现场布局，再看旧总结。\n'
                          '- 如果原场地的当前可用容量低于实际到场总人数，不能继续按原计划执行。\n'
                          '- 只有在备用场地也不满足时才考虑延期。\n',
 'notes/old_venue_summary.md': '# Old Venue Summary\n'
                               '更新时间：2026-07-01\n'
                               '\n'
                               'Harbor Hall 之前按剧场型排布可以放到 180 人，主办方上次复盘时觉得不用启用 Riverside Studio。\n'
                               '这份总结写在家庭拍照背景墙和直播机位要求确认之前。\n',
 'planning/headcount_latest.csv': 'type,count,note\n'
                                  'adults,124,confirmed\n'
                                  'children,48,confirmed\n'
                                  'staff,6,on-site crew\n',
 'planning/seating_layout.csv': 'venue,base_capacity,blocked_for_stage,blocked_for_camera,usable_capacity\n'
                                'Harbor Hall,180,18,6,156\n'
                                'Riverside Studio,190,4,2,184\n',
 'logs/venue_ops.log': '2026-07-14T09:10:11Z venue=Harbor Hall note=family photo wall and stroller '
                       'lane locked in\n'
                       '2026-07-14T09:14:22Z venue=Riverside Studio note=backup hold confirmed '
                       'until 18:00\n'
                       '2026-07-14T09:14:45Z venue=Riverside Studio note=same-day AV patch '
                       'available\n',
 'deliverables/README.md': '# Deliverables\n'
                           '请在这里写最终输出：\n'
                           '- venue_recommendation.md\n'
                           '- decision.json\n'
                           '- client_note.md\n'
                           '\n'
                           '隐含要求：\n'
                           '- `decision.json` 需要使用规范决策枚举，并记录 accepted_sources 与 rejected_sources\n'
                           '- 最终结论要说明为什么旧 summary 不能继续直接采用\n'
                           '- 交付内容要像可以直接发出去的成品，而不是原始材料拼接\n'}
JSON_FILES = {'configs/fire_safety_limits.json': {'updated_at': '2026-07-14',
                                     'venues': [{'name': 'Harbor Hall',
                                                 'legal_max': 160,
                                                 'inspector_note': 'stroller lane and photo wall '
                                                                   'reduce standing overflow'},
                                                {'name': 'Riverside Studio',
                                                 'legal_max': 188,
                                                 'inspector_note': 'current setup cleared'}]}}


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
    build_asset(repo_root / "assets" / "data_61")
    print(f"Asset ready: {repo_root / 'assets' / 'data_61'}")


if __name__ == "__main__":
    main()
