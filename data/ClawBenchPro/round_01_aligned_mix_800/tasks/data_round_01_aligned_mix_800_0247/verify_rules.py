import os
import json
import re

def verify():
    results = {
        "summary_file_exists": False,
        "unapproved_names_found": [],
        "anime_identity_checked": False,
        "total_hours_correct": False,
        "names_extracted_correctly": False
    }

    # 检查报告文件是否存在 (支持多种格式)
    summary_dir = "summary"
    files = os.listdir(summary_dir) if os.path.exists(summary_dir) else []
    target_file = None
    for f in files:
        if "report" in f.lower() or "summary" in f.lower():
            target_file = os.path.join(summary_dir, f)
            results["summary_file_exists"] = True
            break

    # 预期数值
    # Sato(4+2) + Tanaka(3.5) + Suzuki(5) + Takahashi(2) + Watanabe(6) = 22.5
    expected_hours = 22.5
    # 不在名单: Ghost In Shell, Madara Uchiha, Aizen Sosuke
    expected_intruders = {"Ghost In Shell", "Madara Uchiha", "Aizen Sosuke"}

    if target_file:
        with open(target_file, "r", encoding="utf-8") as f:
            content = f.read()
            content_lower = content.lower()
            
            # 检查总工时 (允许微小误差)
            match = re.search(r"22\.5", content)
            if match:
                results["total_hours_correct"] = True
            
            # 检查非法名单是否被识别
            found_intruders = []
            for name in expected_intruders:
                if name.lower() in content_lower:
                    found_intruders.append(name)
            
            results["unapproved_names_found"] = found_intruders
            if set(found_intruders) == expected_intruders:
                results["names_extracted_correctly"] = True
                
            # 检查是否完成了动漫假名的判定
            # 只要报告中针对这几个人提到了 anime/manga/character/naruto/bleach/fictional 等词，即算过关
            anime_keywords = ["anime", "manga", "character", "naruto", "bleach", "fictional", "animation", "动漫", "角色", "二次元", "虚构"]
            if any(kw in content_lower for kw in anime_keywords):
                results["anime_identity_checked"] = True

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    verify()
