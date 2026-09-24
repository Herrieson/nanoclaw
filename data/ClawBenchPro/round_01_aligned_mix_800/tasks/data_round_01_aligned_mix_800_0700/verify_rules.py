import os
import json
import sys

def verify():
    # 获取工作目录
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    state = {
        "finished_poems_count": 0,
        "catalog_exists": False,
        "err_tag_removed": True,
        "catalog_content_correct": False,
        "file_format_standardized": True
    }

    finished_dir = os.path.join(workspace, "finished_poems")
    catalog_path = os.path.join(workspace, "summary", "catalog.json")

    # 1. 检查整理后的文件
    if os.path.exists(finished_dir):
        files = [f for f in os.listdir(finished_dir) if f.endswith(".txt")]
        state["finished_poems_count"] = len(files)
        
        # 检查是否还有 ERR 标记
        for f in files:
            with open(os.path.join(finished_dir, f), 'r', encoding='utf-8') as file:
                content = file.read()
                if "<<<ERR>>>" in content:
                    state["err_tag_removed"] = False

    # 2. 检查 Catalog
    if os.path.exists(catalog_path):
        state["catalog_exists"] = True
        try:
            with open(catalog_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 预期的诗歌标题
                expected_titles = ["Ocean Whispers", "Midnight Ink", "Cactus Flower"]
                # 检查逻辑：是否包含这三个标题，且行数匹配
                # Ocean(3), Midnight(4), Cactus(4)
                titles_found = []
                if isinstance(data, list):
                    for entry in data:
                        t = entry.get("title")
                        l = entry.get("lines")
                        if t == "Ocean Whispers" and l == 3: titles_found.append(t)
                        if t == "Midnight Ink" and l == 4: titles_found.append(t)
                        if t == "Cactus Flower" and l == 4: titles_found.append(t)
                
                if len(set(titles_found)) == 3:
                    state["catalog_content_correct"] = True
        except:
            state["catalog_content_correct"] = False

    # 写入 state.json
    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
