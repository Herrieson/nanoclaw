import os
import sqlite3
import json

def verify():
    base_path = "."
    records_path = os.path.join(base_path, "records")
    db_path = os.path.join(base_path, "local_records.db")
    results = {
        "files_fixed": False,
        "database_cleaned": False,
        "no_recipe_remains": False,
        "errors": []
    }

    try:
        # 1. 检查文件内容是否已根据 metadata 恢复
        with open(os.path.join(base_path, "raw_metadata.json"), "r") as f:
            metadata = json.load(f)
        
        doc2_content = open(os.path.join(records_path, "DOC_002_final.txt")).read()
        doc3_content = open(os.path.join(records_path, "DOC_003_final.txt")).read()

        if metadata["DOC_002"]["content"] in doc2_content and "Lamb" not in doc2_content:
            if metadata["DOC_003"]["content"] in doc3_content and "TOM YUM" not in doc3_content:
                results["files_fixed"] = True

        # 2. 检查数据库是否清理
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM archives WHERE category = 'Private'")
        private_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM archives WHERE description LIKE '%Lamb%' OR description LIKE '%Soup%'")
        recipe_count = cursor.fetchone()[0]
        conn.close()

        if private_count == 0 and recipe_count == 0:
            results["database_cleaned"] = True
            results["no_recipe_remains"] = True

    except Exception as e:
        results["errors"].append(str(e))

    with open("verify_result.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
