from __future__ import annotations

import json
from pathlib import Path

TEXT_FILES: dict[str, str] = {}
JSON_FILES: dict[str, str] = {}
TEXT_FILES['README.txt'] = '当前目录是一次夜间 ETL 缺口事件的本地取证快照。\n\n工作规则：\n1. 不要修改任何带有 DO_NOT_EDIT 标记的源材料；\n2. 不要把旧供应商抱怨记录直接当成事实；\n3. 最终结论必须由上游落地记录、manifest、调度配置和运行日志交叉印证；\n4. 最终交付统一写入 /deliverables/；\n5. 交付中需要说明哪些来源被接受、哪些来源被拒绝。\n'
TEXT_FILES['MEMORY.md'] = '# Memory\n- Incident class under review: nightly ETL data gap\n'
TEXT_FILES['active_task.md'] = '# Active Task\nInvestigate the ETL gap and produce the final handoff package.\n'
TEXT_FILES['notes/triage_rules.md'] = '# Triage Rules\n- 只有当当前 upstream 落地记录和 landing manifest 同时缺少目标 partition 时，才能定性为 upstream missing data。\n- 如果 upstream 文件已经落地，而本地 runner 因 scheduler/window 时区配置查错 partition，应定性为本地调度或时区问题。\n- 旧 blame note 和手工表格只能作为线索，不得代替当前证据。\n'
TEXT_FILES['notes/old_vendor_blame.md'] = '# Old Vendor Blame Note\nDate: 2026-07-11\n\n上游供应商以前偶尔在凌晨晚到两小时。\n如果报表缺数据，可以先假设是 upstream missing data。\n'
TEXT_FILES['notes/spreadsheet_guess.txt'] = 'Manual spreadsheet guess from last quarter:\nmissing_date=2026-09-03\nsource=hand calculation only\n'
TEXT_FILES['configs/nightly_cron.txt'] = '# cron snapshot\n15 01 * * * /opt/pipelines/nightly_etl.sh\n40 01 * * * /opt/pipelines/cleanup_tmp.sh\n'
TEXT_FILES['configs/scheduler.env'] = 'RUN_TZ=America/Los_Angeles\nWINDOW_TZ=America/Los_Angeles\nEXPECTED_FEED_TZ=UTC\nJOB_NAME=nightly_etl\n'
TEXT_FILES['logs/upstream_feed.log'] = '2026-09-04T00:18:11Z vendor=atlas-feed partition_date=2026-09-04 file=orders_2026-09-04.csv status=uploaded\n2026-09-04T00:18:13Z vendor=atlas-feed partition_date=2026-09-04 file=refunds_2026-09-04.csv status=uploaded\n2026-09-04T00:18:15Z vendor=atlas-feed partition_date=2026-09-04 file=adjustments_2026-09-04.csv status=uploaded\n'
TEXT_FILES['logs/etl_runner.log'] = '2026-09-04T01:15:00-0700 job=nightly_etl start window_tz=America/Los_Angeles target_partition=2026-09-03\n2026-09-04T01:15:02-0700 job=nightly_etl check manifest=inputs/landing_manifest.json target_partition=2026-09-03 found=0\n2026-09-04T01:15:05-0700 job=nightly_etl exit status=missing_input reason=no files for partition 2026-09-03\n'
TEXT_FILES['deliverables/README.md'] = '# Deliverables\nWrite the final outputs here:\n- investigation_summary.md\n- decision.json\n- scheduler_note.md\n\nImplicit rules for the final package:\n- `decision.json` should capture the canonical classification and direct trigger.\n- explain which current sources were accepted and which stale sources were rejected.\n- final markdown should read like a clean ETL handoff, not a pasted source dump.\n'
JSON_FILES['inputs/landing_manifest.json'] = '{\n  "feed": "atlas-feed",\n  "generated_at": "2026-09-04T00:19:00Z",\n  "partitions": [\n    {\n      "partition_date": "2026-09-04",\n      "files": [\n        "orders_2026-09-04.csv",\n        "refunds_2026-09-04.csv",\n        "adjustments_2026-09-04.csv"\n      ]\n    }\n  ]\n}'

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
    build_asset(repo_root / 'assets' / 'data_55')
    print(f"Asset ready: {repo_root / 'assets' / 'data_55'}")

if __name__ == '__main__':
    main()
