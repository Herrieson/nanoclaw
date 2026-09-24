import os
import sys
import json

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # 路径定义
    deliverables_path = os.path.join(workspace, "deliverables")
    summary_file = os.path.join(deliverables_path, "gala_summary.json")

    # 1. 检查结果目录与文件是否存在 (10分)
    if os.path.exists(summary_file):
        score += 10
        details.append({"item": "检查结果文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "gala_summary.json 存在"})
    else:
        details.append({"item": "检查结果文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 deliverables/gala_summary.json"})
        # 如果文件不存在，后续检查无法进行，直接输出
        write_score(score, details)
        return

    # 2. 检查 JSON 格式合法性 (10分)
    try:
        with open(summary_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        score += 10
        details.append({"item": "检查 JSON 格式合法性", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 成功解析"})
    except Exception as e:
        details.append({"item": "检查 JSON 格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {e}"})
        write_score(score, details)
        return

    # 3. 验证 Children's Books 数量 (40分)
    # 计算逻辑：
    # Room 1: Goodnight Moon (1), Alice Johnson: Charlotte's Web (1) -> 2
    # Front Desk: Beatrice (4) -> 4
    # Online: Eleanor TXN_9901 (3) -> 3
    # Total: 2 + 4 + 3 = 9
    expected_books = 9
    actual_books = data.get("children_books_count") if "children_books_count" in data else data.get("total_children_books")
    
    if actual_books == expected_books:
        score += 40
        details.append({"item": "Children's Books 数量统计", "score": 40, "max_score": 40, "passed": True, "reason": f"统计结果 {actual_books} 正确"})
    elif isinstance(actual_books, int) and abs(actual_books - expected_books) <= 2:
        score += 20
        details.append({"item": "Children's Books 数量统计", "score": 20, "max_score": 40, "passed": False, "reason": f"统计结果 {actual_books} 偏差较小，预期 {expected_books}"})
    else:
        details.append({"item": "Children's Books 数量统计", "score": 0, "max_score": 40, "passed": False, "reason": f"统计结果 {actual_books} 错误，预期 {expected_books}"})

    # 4. 验证 VIP 列表 (40分)
    # VIP 定义：既捐了书（任一类型）又捐了烘焙食品。
    # Sarah Connor: Goodnight Moon(B) + Brownies(Baked) -> VIP
    # John Smith: The Shining(B) + Cupcakes(Baked) -> VIP
    # Beatrice: 4 Books(B) + Apple Pie(Baked) -> VIP
    # Tom: TXN_4402 -> 1 AdultBook(B) + 1 BakedGood(Baked) -> VIP
    # 预期名单（First Names）: Sarah, John, Beatrice, Tom
    expected_vips = {"Sarah", "John", "Beatrice", "Tom"}
    actual_vips_raw = data.get("vip_parents", [])
    actual_vips = {name.split()[0] for name in actual_vips_raw if isinstance(name, str)}

    missing = expected_vips - actual_vips
    extra = actual_vips - expected_vips

    if not missing and not extra:
        score += 40
        details.append({"item": "VIP 名单准确性", "score": 40, "max_score": 40, "passed": True, "reason": "VIP 名单完全匹配"})
    elif len(missing) <= 1 and len(extra) == 0:
        score += 25
        details.append({"item": "VIP 名单准确性", "score": 25, "max_score": 40, "passed": False, "reason": f"名单基本正确，遗漏: {missing}"})
    else:
        details.append({"item": "VIP 名单准确性", "score": 0, "max_score": 40, "passed": False, "reason": f"名单错误。遗漏: {missing}, 多余: {extra}"})

    write_score(score, details)

def write_score(total_score, details):
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": int(total_score), "details": details}, f, indent=4)

if __name__ == "__main__":
    verify()
