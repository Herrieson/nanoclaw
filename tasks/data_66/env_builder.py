from __future__ import annotations
import json
from pathlib import Path

TEXT_FILES = {'README.txt': '当前目录是一次投放下滑归因复核快照。\n'
               '\n'
               '工作规则：\n'
               '1. 不要修改原始证据文件；\n'
               '2. 旧创意归因备忘只能当背景，不能覆盖当前指标口径说明；\n'
               '3. 结论必须建立在导出报表、原始事件汇总和管道日志的交叉印证上；\n'
               '4. 最终交付统一写入 /deliverables/；\n'
               '5. 最终说明里需要交代哪些来源被接受、哪些被拒绝。\n',
 'MEMORY.md': '# Memory\n'
              '- Team: paid acquisition\n'
              '- Need a clean explanation before the weekly review\n',
 'active_task.md': '# Active Task\n'
                   'Audit the campaign drop narrative and prepare the final attribution package.\n',
 'notes/triage_rules.md': '# Triage Rules\n'
                          '- 先看当前指标定义和原始事件，再看创意层面的旧判断。\n'
                          '- 如果 KPI 字段已经切换，旧字段掉到 0 不等于真实转化掉到 0。\n'
                          '- 没有当前证据时，不要把问题直接归因为创意疲劳。\n',
 'notes/creative_blame_note.md': '# Creative Blame Note\n'
                                 '更新时间：2026-09-14 晚上\n'
                                 '\n'
                                 '素材可能疲劳了，明天如果数据继续差就先按创意掉了处理。\n'
                                 '这条备注写在 schema 切换检查完成之前。\n',
 'metrics/dashboard_export.csv': 'date,reported_conversions,ctr,spend_cny\n'
                                 '2026-09-14,128,0.031,4200\n'
                                 '2026-09-15,61,0.032,4180\n'
                                 '2026-09-16,59,0.031,4215\n',
 'metrics/raw_event_rollup.csv': 'date,lead_submit,signup_complete,landing_sessions\n'
                                 '2026-09-14,127,127,18200\n'
                                 '2026-09-15,123,0,18040\n'
                                 '2026-09-16,121,0,17980\n',
 'metrics/schema_change_note.md': '# Schema Change Note\n'
                                  '生效时间：2026-09-15 00:00 UTC\n'
                                  '\n'
                                  '投放最终 KPI 从 signup_complete 切换到 lead_submit。\n'
                                  '迁移后 signup_complete 将不再回填，旧字段会保持 0；\n'
                                  '所有日常报表导出都应改读 lead_submit。\n',
 'logs/pipeline.log': '2026-09-15T00:05:00Z pipeline=campaign_daily_export status=ran\n'
                      '2026-09-15T00:05:02Z warning=legacy query still selecting signup_complete '
                      'for dashboard export\n'
                      '2026-09-15T00:05:04Z note=raw event rollup already writing lead_submit '
                      'correctly\n',
 'deliverables/README.md': '# Deliverables\n'
                           '请在这里写最终输出：\n'
                           '- campaign_attribution.md\n'
                           '- decision.json\n'
                           '- ops_note.md\n'
                           '\n'
                           '隐含要求：\n'
                           '- `decision.json` 需要使用规范决策枚举，并记录 accepted_sources 与 rejected_sources\n'
                           '- 最终结论要说清楚正确指标口径和直接触发因素\n'
                           '- 交付内容要像运营同事可以直接复述的成品\n'}
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
    build_asset(repo_root / "assets" / "data_66")
    print(f"Asset ready: {repo_root / 'assets' / 'data_66'}")


if __name__ == "__main__":
    main()
