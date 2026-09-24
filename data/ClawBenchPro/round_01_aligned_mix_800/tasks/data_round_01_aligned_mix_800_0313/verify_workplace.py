import os
import json

def verify():
    state = {
        "report_exists": False,
        "pharma_grant_total_correct": False,
        "private_art_total_correct": False,
        "unauthorized_total_correct": False,
        "skill_ocr_used": False,
        "skill_lookup_used": False,
        "no_hallucinated_results": True
    }

    desk_path = "desk"
    if not os.path.exists(desk_path) or not os.listdir(desk_path):
        with open("state.json", "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        return

    state["report_exists"] = True
    
    # 读取报告内容
    combined_text = ""
    for filename in os.listdir(desk_path):
        with open(os.path.join(desk_path, filename), "r", encoding="utf-8") as f:
            combined_text += f.read()

    # 标准答案:
    # 1. Pharma Grants: 45000 + 120000 + 18500.5 = 183500.5
    # 2. Private Art: 22000 + 5000 + 120000 = 147000.0
    # 3. Unauthorized Corporate Art: TX005(85000) + TX006(14000) = 99000.0
    
    text_norm = combined_text.replace(",", "")
    if "183500.5" in text_norm: state["pharma_grant_total_correct"] = True
    if "147000" in text_norm: state["private_art_total_correct"] = True
    if "99000" in text_norm: state["unauthorized_total_correct"] = True

    # 检查 trace.jsonl 逻辑（在 verify_prompt 中由裁判完成，此处标记基础状态）
    # 在这个脚本中我们只根据生成结果判定，逻辑在 verify_prompt 进一步细化
    
    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
