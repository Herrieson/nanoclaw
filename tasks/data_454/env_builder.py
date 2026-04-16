import os
import json
import sqlite3

def build():
    base_path = "assets/data_454"
    os.makedirs(base_path, exist_ok=True)
    
    # 模拟混乱的文件系统
    subfolders = ["Downloads/Old_Exports", "Documents/Yoga_Schedule", ".hidden_configs/temp", "Desktop/New_Folder_2"]
    for folder in subfolders:
        os.makedirs(os.path.join(base_path, folder), exist_ok=True)

    # 1. 碎片的笔记 - 包含关键线索
    with open(os.path.join(base_path, "Documents/Yoga_Schedule/notes_from_last_night.txt"), "w") as f:
        f.write("Need to finish the project! API key for the local conservation mock service is 'ECO-2024-OHIO'.\n")
        f.write("The service runs on localhost:5050/api/species_data\n")
        f.write("Check the .hidden_configs/temp folder for the partial list I started.")

    # 2. 隐藏的错误数据
    partial_data = [
        {"common_name": "Indiana Bat", "scientific_name": "Myotis sodalis", "risk_level": "Endangered"},
        {"common_name": "Ohio Blue Salamander", "scientific_name": "Error_Unknown_Species", "risk_level": "Vulnerable"}
    ]
    with open(os.path.join(base_path, ".hidden_configs/temp/partial_list.json"), "w") as f:
        json.dump(partial_data, f)

    # 3. 散落的 CSV
    csv_content = "common_name,scientific_name,risk_level\n" \
                  "Karner Blue Butterfly,Lycaeides melissa samuelis,Endangered\n" \
                  "Lakeside Daisy,Tetraneuris herbacea,Threatened\n"
    with open(os.path.join(base_path, "Downloads/Old_Exports/legacy_data.csv"), "w") as f:
        f.write(csv_content)

    # 4. 模拟一个简单的本地 API 服务文件 (Agent 需要发现并读取它，模拟 API 调用结果)
    # 我们直接在本地放一个数据库，Agent 需要通过脚本去读取它来模拟 API 响应
    db_path = os.path.join(base_path, "conservation_server.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE species (common_name TEXT, scientific_name TEXT, risk_level TEXT)")
    cursor.execute("INSERT INTO species VALUES ('Eastern Massasauga', 'Sistrurus catenatus', 'Threatened')")
    cursor.execute("INSERT INTO species VALUES ('Northern Long-eared Bat', 'Myotis septentrionalis', 'Endangered')")
    conn.commit()
    conn.close()

    print(f"Environment built successfully in {base_path}")

if __name__ == "__main__":
    build()
