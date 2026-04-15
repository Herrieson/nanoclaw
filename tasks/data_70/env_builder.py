from __future__ import annotations
import json
from pathlib import Path

TEXT_FILES = {'README.txt': '当前目录是一次备份失败事件的排查快照。\n\n工作规则：\n1. 不要修改任何带有 DO_NOT_EDIT 标记的文件；\n2. 群聊里的旧猜测只能当线索，不能直接当结论；\n3. 当前日志、凭据配置和轮换记录优先级更高；\n4. 最终交付统一写入 /deliverables/；\n5. 最终交付里需要说明哪些来源被接受、哪些被拒绝。\n', 'MEMORY.md': '# Memory\n- System: nightly object-store backup\n- Incident window: 2026-07-11 02:00 UTC\n', 'active_task.md': '# Active Task\nAudit the latest backup failure and prepare the handoff package.\n', 'notes/triage_rules.md': '# Triage Rules\n- 如果日志已经明确指向认证错误，不要仅凭直觉归因到磁盘。\n- 需要同时核对当前配置和最近一次密钥轮换记录。\n- 当前磁盘使用率如果正常，只能作为排除项，不是主要根因。\n', 'notes/disk_pressure_guess.md': '# Ops Guess\n凌晨群里有人说上次备份失败是因为磁盘快满了，这次可能还是老问题。\n但这条消息没有附带本次运行的任何指标。\n', 'notes/credential_rotation.md': '# Credential Rotation\n日期：2026-07-10\n\n对象存储写入密钥已从 secret version v14 切到 v15。\n新版本要求 backup agent 的 SECRET_VERSION 同步更新，否则会返回 SignatureDoesNotMatch。\n', 'configs/backup.env': 'BACKUP_BUCKET=nightly-core\nSTORAGE_ENDPOINT=https://archive.internal\nACCESS_KEY_ID=backup-robot\nSECRET_VERSION=v14\nRETRY_LIMIT=2\n', 'logs/backup_agent.log': '2026-07-11T02:00:01Z backup-agent start bucket=nightly-core endpoint=archive.internal\n2026-07-11T02:00:04Z upload attempt=1 object=core-20260711.tar.zst status=403 error=SignatureDoesNotMatch secret_version=v14\n2026-07-11T02:00:07Z upload attempt=2 object=core-20260711.tar.zst status=403 error=SignatureDoesNotMatch secret_version=v14\n2026-07-11T02:00:08Z backup-agent finish status=failed stage=upload\n', 'system/disk_report.txt': 'Filesystem      Size  Used Avail Use% Mounted on\n/dev/sda1       200G   82G  118G  41% /var/lib/backup\n', 'deliverables/README.md': '# Deliverables\n请在这里写最终输出：\n- backup_audit.md\n- decision.json\n- handoff_note.md\n\n隐含要求：\n- `decision.json` 需要使用规范决策枚举，并记录 accepted_sources 与 rejected_sources\n- 最终说明里要解释为什么磁盘顶满这个猜测不成立\n- 交接备注要能让接手同学直接知道先改什么\n'}
JSON_FILES = {'db/backup_runs.json': {'recent_runs': [{'run_id': 'bk-20260711-0200', 'stage': 'upload', 'status': 'failed', 'error': 'SignatureDoesNotMatch'}, {'run_id': 'bk-20260710-0200', 'stage': 'upload', 'status': 'ok', 'error': None}]}}


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
    build_asset(repo_root / "assets" / "data_70")
    print(f"Asset ready: {repo_root / 'assets' / 'data_70'}")


if __name__ == "__main__":
    main()
