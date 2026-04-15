from __future__ import annotations
import json
from pathlib import Path

TEXT_FILES = {'README.txt': '当前目录是一次配置回滚评估快照。\n\n工作规则：\n1. 不要修改任何带有 DO_NOT_EDIT 标记的文件；\n2. 旧的全量回滚建议只能作为背景，不能直接当最终结论；\n3. 当前配置、日志和发布差异优先级更高；\n4. 最终交付统一写入 /deliverables/；\n5. 最终交付里需要说明哪些来源被接受、哪些被拒绝。\n', 'MEMORY.md': '# Memory\n- Service: notifier\n- Review type: rollback necessity check\n', 'active_task.md': '# Active Task\nDecide whether the new config needs a full rollback or only a targeted patch.\n', 'notes/triage_rules.md': '# Triage Rules\n- 如果问题能被单一 flag 明确解释，并且其他变更没有异常证据，优先给 targeted patch。\n- 不要因为旧 memo 习惯性建议回滚，就忽略当前差异和日志。\n- 结论里要写清楚为什么 single-flag patch 足够。\n', 'notes/full_rollback_memo.md': '# Rollback Memo\n去年值班手册里写过：发布后出现告警就先整包回滚。\n这份 memo 没有覆盖当前 notifier 的细粒度 feature flag 流程。\n', 'notes/hotfix_window.md': '# Hotfix Window\n- 允许在不重启整套服务的情况下修改 notifier feature flag\n- 如果只涉及 `enable_delta_cache`，可走单点配置修正，不需要整包回滚\n- 本次值班窗口允许 10 分钟内完成热修\n', 'configs/service_flags.toml': '[features]\nenable_delta_cache = true\nenable_digest_queue = true\nenable_priority_fanout = true\n', 'logs/notification_worker.log': '2026-07-18T12:03:11Z notifier send batch=182 mode=delta-cache result=duplicate_push_detected\n2026-07-18T12:03:12Z notifier fallback queue=digest status=ok\n2026-07-18T12:03:13Z alert duplicate notifications spike after enable_delta_cache=true\n', 'reports/release_diff.txt': 'Release 2026-07-18 config diff\n- enable_delta_cache: false -> true\n- other notifier flags unchanged\n', 'deliverables/README.md': '# Deliverables\n请在这里写最终输出：\n- rollback_decision.md\n- decision.json\n- patch_note.md\n\n隐含要求：\n- `decision.json` 需要使用规范决策枚举，并记录 accepted_sources 与 rejected_sources\n- 需要写清楚 target_file、target_flag、target_value\n- 最终说明要解释为什么不用整包回滚\n'}
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
    build_asset(repo_root / "assets" / "data_73")
    print(f"Asset ready: {repo_root / 'assets' / 'data_73'}")


if __name__ == "__main__":
    main()
