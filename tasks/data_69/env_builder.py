from __future__ import annotations
import json
from pathlib import Path

TEXT_FILES = {'README.txt': '当前目录是一次达人 brief 合规复核快照。\n\n工作规则：\n1. 不要修改任何带有 DO_NOT_EDIT 标记的文件；\n2. 旧品牌手册只能作为背景，不是当前口径；\n3. 当前合规更新、产品事实表、待发 brief 三者交叉后再下结论；\n4. 最终交付统一写入 /deliverables/；\n5. 最终交付里需要说明哪些来源被接受、哪些被拒绝。\n', 'MEMORY.md': '# Memory\n- Brand: Nera Skin\n- Review type: creator brief correction\n', 'active_task.md': '# Active Task\nCheck whether the creator brief needs corrections before sending.\n', 'notes/triage_rules.md': '# Triage Rules\n- 当前合规更新优先于旧品牌手册。\n- 如果 brief 中出现已经下线或被限制的表述，需要明确指出并给出替代表述。\n- 不要把旧 slogan 当成当前可对外发送的话术。\n', 'notes/compliance_update_2026-07-02.md': '# Compliance Update\n日期：2026-07-02\n\n从本轮达人合作起：\n- 禁止再使用『医用级修护』这类医疗暗示表述\n- 赠礼信息必须写成『满199加赠旅行装』，不能写成『全店无门槛赠礼』\n- 防晒喷雾只能写『户外补喷方便』，不能写成『全天候不用补』\n', 'notes/brand_guideline_2025.md': '# Brand Guideline 2025\n- 核心感知：医用级修护体验\n- 活动词：全店无门槛赠礼\n- 旧 campaign 曾写过『全天候安心不补喷』\n\n备注：这是旧版品牌手册摘录，编写时间早于 2026 合规整改。\n', 'briefs/current_creator_brief.md': '# Creator Brief Draft\n1. 请突出『医用级修护喷雾』\n2. 可带一句『全店无门槛赠礼』\n3. 使用场景可以写『全天候安心不补喷』\n4. 主线还是围绕通勤补喷和妆后使用\n', 'deliverables/README.md': '# Deliverables\n请在这里写最终输出：\n- brief_review.md\n- decision.json\n- creator_reply.md\n\n隐含要求：\n- `decision.json` 需要使用规范决策枚举，并记录 accepted_sources 与 rejected_sources\n- 交付里要明确指出需要替换的旧表述\n- 沟通文案要像真实发给达人的说明，不要直接抄原始材料\n'}
JSON_FILES = {'product/claim_facts.json': {'product': 'Nera Skin UV Mist', 'allowed_claims': ['户外补喷方便', '妆后可补喷', '满199加赠旅行装'], 'blocked_claims': ['医用级修护', '全店无门槛赠礼', '全天候不用补喷']}}


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
    build_asset(repo_root / "assets" / "data_69")
    print(f"Asset ready: {repo_root / 'assets' / 'data_69'}")


if __name__ == "__main__":
    main()
