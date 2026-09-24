import os
import json

def verify():
    state = {
        "exhibition_folder_exists": False,
        "inventory_file_exists": False,
        "correct_paintings_included": False,
        "skill_used_for_ocr": False,
        "skill_used_for_insurance": False,
        "total_value_correct": False
    }

    if os.path.isdir("exhibition"):
        state["exhibition_folder_exists"] = True

    file_path = "exhibition/gallery_inventory.md"
    if os.path.exists(file_path):
        state["inventory_file_exists"] = True
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().lower()
            
            # 基础画作 (来自 CSV)
            csv_paintings = ["sunflowers", "spring morning", "morning dew"]
            # 核心画作 (必须通过 OCR 获取)
            ocr_paintings = ["abstract 1", "neon dreams"]
            
            if all(p in content for p in csv_paintings + ocr_paintings):
                state["correct_paintings_included"] = True
            
            # 校验保险估值逻辑 (Base Price * 1.15 + 50) -> 这是 Skill 内部逻辑的 Mock 结果
            # CSV Items: 
            # Sunflowers: 500 -> 625
            # Spring Morning: 250 -> 337.5
            # Morning Dew: 200 -> 280
            # OCR Items (预设):
            # Abstract 1: 600 -> 740
            # Neon Dreams: 800 -> 970
            # Total: 625 + 337.5 + 280 + 740 + 970 = 2952.5
            if "2952.5" in content or "2,952.5" in content:
                state["total_value_correct"] = True

    # 轨迹检查（由 verify_prompt 进一步确认，此处做初步状态记录）
    # 在实际系统中，这通常由裁判模型读取 trace.jsonl 判定
    
    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
