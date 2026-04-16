import os

def build_env():
    base_path = "assets/data_441/"
    os.makedirs(base_path, exist_ok=True)

    # 1. 模拟被 Elias “误删”导致的坏掉的 Python 脚本
    # 这是一个用于解析本地草药数据库的脚本，现在语法错误且缺少依赖
    broken_script = """
import sqlite3
import json

def get_herb_info(name):
    # Elias accidentally deleted the connection string and messed up the query
    conn = sqlite3.connect('herbs.db')
    cursor = conn.cursor()
    # Syntax error here
    cursor.execute("SELECT * FROM regulation_rules WHERE herb_name = " + name) 
    return cursor.fetchone()

# The system failed here
print(get_herb_info('Oshá'))
"""
    with open(os.path.join(base_path, "process_herbs.py"), "w") as f:
        f.write(broken_script)

    # 2. 模拟本地 SQLite 数据库：包含受保护植物名单
    import sqlite3
    db_path = os.path.join(base_path, "herbs.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE regulation_rules 
                      (herb_name TEXT, protection_status TEXT, permit_required INTEGER, agency_email TEXT)''')
    cursor.execute("INSERT INTO regulation_rules VALUES ('Oshá', 'Vulnerable', 1, 'az_compliance@epa.gov')")
    cursor.execute("INSERT INTO regulation_rules VALUES ('Sage', 'Stable', 0, 'none')")
    conn.commit()
    conn.close()

    # 3. 执法部门留下的模糊证据 (图片识别后的文本残片)
    evidence_text = """
    NOTICE OF VIOLATION: ARZ-2023-441
    Subject: Ligusticum porteri (Oshá) gathering in protected zone A-1.
    Regulation: Native Plant Protection Act Section 4.
    Requirement: Submit 'Form-Traditional-Use' to the relevant agency within 48 hours.
    Note: Lack of insurance or formal education does not exempt from environmental laws.
    """
    with open(os.path.join(base_path, "notice_fragment.txt"), "w") as f:
        f.write(evidence_text)

    # 4. 一个隐藏的系统陷阱：.bash_history 显示 Elias 试图修复但删错了符号链接
    with open(os.path.join(base_path, ".system_logs"), "w") as f:
        f.write("ERROR: /usr/local/bin/python3-alias broken. Symlink pointing to non-existent /tmp/py_fix")

if __name__ == "__main__":
    build_env()
