import os
import json
import sys
import base64

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    state = {
        "finished_poems_count": 0,
        "catalog_exists": False,
        "err_tag_removed": True,
        "ocr_used": False,
        "binary_parsed": False,
        "catalog_content_correct": False
    }

    finished_dir = os.path.join(workspace, "finished_poems")
    catalog_path = os.path.join(workspace, "summary", "catalog.json")

    # 1. 检查文件生成情况
    if os.path.exists(finished_dir):
        files = [f for f in os.listdir(finished_dir) if f.endswith(".txt")]
        state["finished_poems_count"] = len(files)
        
        for f in files:
            with open(os.path.join(finished_dir, f), 'r', encoding='utf-8') as file:
                content = file.read()
                if "<<<ERR>>>" in content:
                    state["err_tag_removed"] = False
                # 检查是否成功解析了二进制和图片内容
                if "Words flow like slow honey" in content:
                    state["binary_parsed"] = True
                if "bloom in the desert" in content: # 这是 OCR 应该返回的内容
                    state["ocr_used"] = True

    # 2. 检查 Catalog
    if os.path.exists(catalog_path):
        state["catalog_exists"] = True
        try:
            with open(catalog_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 预期由 Skill 返回的标准化标题
                expected = {
                    "Ocean Whispers": 3,
                    "Midnight Ink": 4,
                    "Cactus Flower": 4
                }
                found_count = 0
                if isinstance(data, list):
                    for entry in data:
                        t = entry.get("title")
                        l = entry.get("lines")
                        if t in expected and expected[t] == l:
                            found_count += 1
                
                if found_count == 3:
                    state["catalog_content_correct"] = True
        except:
            pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
