from __future__ import annotations
import json
from pathlib import Path

TEXT_FILES = {'README.txt': '当前目录是一次发帖排期冲突的审计快照。\n'
               '\n'
               '工作规则：\n'
               '1. 不要修改原始证据文件；\n'
               '2. 最终批准日历优先级高于旧导出和草稿备注；\n'
               '3. 结论必须建立在最终批准版本、排期规则和导入日志的交叉印证上；\n'
               '4. 最终交付统一写入 /deliverables/；\n'
               '5. 最终说明里需要交代哪些来源被接受、哪些被拒绝。\n',
 'MEMORY.md': '# Memory\n'
              '- Channel: community posts\n'
              '- Scheduler conflict needs one clean source of truth\n',
 'active_task.md': '# Active Task\n'
                   'Audit the scheduling conflict and prepare the final publishing package.\n',
 'notes/triage_rules.md': '# Triage Rules\n'
                          '- 最终批准日历是最高优先级。\n'
                          '- 旧导出只能说明系统当时导入了什么，不能覆盖最终批准版。\n'
                          '- 草稿如果没有批准记录，不能直接进入正式排期。\n',
 'notes/outdated_export.csv': 'slot,post_slug,owner,exported_from\n'
                              '2026-10-07 09:00,brand_collab_teaser,mei,scheduler_cache_v1\n'
                              '2026-10-07 09:00,family_story_roundup,jun,scheduler_cache_v1\n'
                              '2026-10-08 12:30,holiday_return_packing,lin,scheduler_cache_v1\n',
 'notes/draft_calendar.md': '# Draft Calendar\n'
                            '- family_story_roundup once floated for 2026-10-07 09:00, but that '
                            'was before the final review.\n'
                            '- holiday_return_packing was discussed for 2026-10-08 12:30 in draft '
                            'comments only.\n'
                            '- This note was never marked approved.\n',
 'calendar/final_approved_calendar.csv': 'slot,post_slug,owner,status\n'
                                         '2026-10-07 09:00,brand_collab_teaser,mei,approved\n'
                                         '2026-10-08 12:30,family_story_roundup,jun,approved\n'
                                         '2026-10-10 18:00,holiday_return_packing,lin,approved\n',
 'rules/post_slot_rules.md': '# Post Slot Rules\n'
                             '1. 最终批准日历是唯一正式排期来源。\n'
                             '2. 同一频道同一时段不能有两个帖子。\n'
                             '3. 旧导出和草稿只用于追查冲突来源，不能直接覆盖 approved 版本。\n',
 'logs/publish_ops.log': '2026-10-06T21:04:01Z scheduler import_source=notes/outdated_export.csv\n'
                         '2026-10-06T21:04:02Z warning=duplicate slot detected at 2026-10-07 '
                         '09:00\n'
                         '2026-10-06T21:04:09Z note=final approved calendar had not been '
                         're-imported after cache restore\n',
 'deliverables/README.md': '# Deliverables\n'
                           '请在这里写最终输出：\n'
                           '- schedule_audit.md\n'
                           '- decision.json\n'
                           '- publisher_note.md\n'
                           '\n'
                           '隐含要求：\n'
                           '- `decision.json` 需要使用规范决策枚举，并记录 accepted_sources 与 rejected_sources\n'
                           '- 最终结论要明确哪个版本是执行依据，以及冲突怎么来的\n'
                           '- 交付内容要像排期同事可以直接执行的成品\n'}
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
    build_asset(repo_root / "assets" / "data_67")
    print(f"Asset ready: {repo_root / 'assets' / 'data_67'}")


if __name__ == "__main__":
    main()
