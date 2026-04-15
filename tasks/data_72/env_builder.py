from __future__ import annotations
import json
from pathlib import Path

TEXT_FILES = {'README.txt': '当前目录是一次定时任务漂移排查快照。\n\n工作规则：\n1. 不要修改任何带有 DO_NOT_EDIT 标记的文件；\n2. 旧猜测只能当线索，不能直接当结论；\n3. 当前 cron 表达式、运行时间日志、时钟状态三者必须交叉验证；\n4. 最终交付统一写入 /deliverables/；\n5. 最终交付里需要说明哪些来源被接受、哪些被拒绝。\n', 'MEMORY.md': '# Memory\n- Service: feed-sync\n- Review type: scheduler drift investigation\n', 'active_task.md': '# Active Task\nInvestigate the observed scheduler drift and prepare the fix note.\n', 'notes/triage_rules.md': '# Triage Rules\n- 先确认时钟状态是否健康，再判断是不是系统时间漂移。\n- 如果运行时间呈现稳定的固定间隔，优先检查 cron 表达式本身。\n- 结论里要说明为什么接受当前调度证据、为什么拒绝旧猜测。\n', 'notes/clock_drift_guess.md': '# Guess\n有人说任务不是整点跑，可能是机器时钟慢慢飘了。\n这条猜测没有附上 NTP 状态，也没有核对实际 cron 配置。\n', 'notes/expected_schedule.md': '# Expected Schedule\n这个同步任务应该每 15 分钟跑一次，也就是 00、15、30、45 分。\n', 'configs/cron_jobs.txt': '# cron snapshot\n*/17 * * * * /opt/feed-sync/run_sync.sh\n10 3 * * * /opt/feed-sync/cleanup.sh\n', 'logs/job_runs.log': '2026-07-15T09:03:00Z run_sync start\n2026-07-15T09:20:00Z run_sync start\n2026-07-15T09:37:00Z run_sync start\n2026-07-15T09:54:00Z run_sync start\n', 'system/clock_status.txt': 'NTP service: active\nLast sync: 2026-07-15T08:59:58Z\nClock offset: 0.014s\nClock state: synchronized\n', 'deliverables/README.md': '# Deliverables\n请在这里写最终输出：\n- drift_audit.md\n- decision.json\n- fix_note.md\n\n隐含要求：\n- `decision.json` 需要使用规范决策枚举，并记录 accepted_sources 与 rejected_sources\n- 需要把错误表达式和建议表达式写清楚\n- 最终说明要解释为什么时钟漂移猜测不成立\n'}
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
    build_asset(repo_root / "assets" / "data_72")
    print(f"Asset ready: {repo_root / 'assets' / 'data_72'}")


if __name__ == "__main__":
    main()
