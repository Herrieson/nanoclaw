from __future__ import annotations
import json
from pathlib import Path

TEXT_FILES = {'README.txt': '当前目录是一次内容选题核对快照。\n\n工作规则：\n1. 不要修改任何带有 DO_NOT_EDIT 标记的文件；\n2. 旧关键词备忘只能作为线索，不能直接当最终依据；\n3. 本周评论聚类、最近内容表现、当前商品窗口优先级更高；\n4. 最终交付统一写入 /deliverables/；\n5. 最终交付里需要说明哪些来源被接受、哪些被拒绝。\n', 'MEMORY.md': '# Memory\n- Team: lifestyle content ops\n- Current planning window: next Tuesday topic slot\n', 'active_task.md': '# Active Task\nAudit the conflicting topic signals and prepare the final recommendation package.\n', 'notes/triage_rules.md': '# Triage Rules\n- 优先看最近七天的评论聚类和内容表现，不要让更早的关键词备忘压过当前反馈。\n- 如果当前商品窗口已经变化，旧 memo 只能当背景。\n- 结论必须能解释为什么接受当前证据、为什么拒绝旧线索。\n', 'notes/stale_keyword_memo.md': '# Keyword Memo\n更新时间：2026-07-01\n\n上月复盘时，大家觉得『春季胶囊衣橱』这个词有希望继续带搜索，所以先记着。\n这份 memo 写在夏季防晒系列上线之前，也没有纳入最近一周评论区追问。\n', 'notes/current_merch_window.md': '# Current Merch Window\n- 本周主推组合：通勤防晒衬衫 + 轻薄叠穿外套\n- 运营备注：春季胶囊衣橱相关 SKU 已下到次级入口，不适合再做主推标题\n- 下周要配合门店直播，优先放大『通勤防晒怎么穿不闷』\n', 'research/post_performance.csv': 'post_id,title,publish_date,views,saves,shares,topic_tag\n118,通勤防晒衬衫怎么搭不显臃肿,2026-07-08,18200,1340,220,uv_commute_layers\n119,春季胶囊衣橱5件循环穿,2026-07-06,9100,410,88,spring_capsule\n120,办公室空调房防晒外套挑选,2026-07-09,16500,1185,204,uv_commute_layers\n121,夏天通勤想显瘦先看版型,2026-07-10,14900,960,171,uv_commute_layers\n', 'deliverables/README.md': '# Deliverables\n请在这里写最终输出：\n- topic_recommendation.md\n- decision.json\n- editor_note.md\n\n隐含要求：\n- `decision.json` 需要使用规范决策枚举，并记录 accepted_sources 与 rejected_sources\n- 最终说明要解释为什么当前证据覆盖旧 memo\n- 交付文档要像干净成品，不能直接复制原始材料\n'}
JSON_FILES = {'research/comment_clusters.json': {'window': '2026-07-04/2026-07-10', 'clusters': [{'topic': 'uv_commute_layers', 'comment_count': 46, 'signals': ['求通勤防晒穿法', '空调房叠穿不闷', '想看显瘦外套']}, {'topic': 'spring_capsule', 'comment_count': 9, 'signals': ['去年收藏翻出来了', '适合春天参考']}, {'topic': 'linen_vacation', 'comment_count': 7, 'signals': ['周末旅行穿搭']}]}}


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
    build_asset(repo_root / "assets" / "data_68")
    print(f"Asset ready: {repo_root / 'assets' / 'data_68'}")


if __name__ == "__main__":
    main()
