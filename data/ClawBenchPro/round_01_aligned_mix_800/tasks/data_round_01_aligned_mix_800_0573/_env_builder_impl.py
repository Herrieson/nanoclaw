import os
import json
import random
import string
import pandas as pd
import numpy as np

def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def clean_amount_sim(amt_str):
    # Just for internal generation verification
    s = str(amt_str).replace("$", "").replace("USD", "").replace(",", "").strip()
    try:
        return float(s)
    except:
        return 0.0

def build_env():
    random.seed(1649)
    np.random.seed(1649)

    os.makedirs("archives/personnel", exist_ok=True)
    os.makedirs("archives/publications", exist_ok=True)
    os.makedirs("archives/finance/ledgers", exist_ok=True)
    os.makedirs("investigation_report", exist_ok=True)

    # 1. 构建人员档案碎片
    names = [f"Dr. {generate_random_string(5)}" for _ in range(300)]
    white_list_names = set()
    
    depts = ["Cross-Cultural Education", "Computer Science", "Physics", "History", "Biology"]
    statuses = ["active", "retired", "suspended", "on_leave"]
    
    for i, name in enumerate(names):
        dept = random.choice(depts)
        status = random.choice(statuses)
        # 强制制造一些合法的白名单人员
        if i < 40:
            dept = "Cross-Cultural Education"
            status = "active"
        
        if dept == "Cross-Cultural Education" and status == "active":
            white_list_names.add(name)
            
        personnel_data = {
            "id": f"EMP-{1000+i}",
            "name": name,
            "department": dept,
            "status": status,
            "join_year": random.randint(1990, 2022)
        }
        
        # 散落分布在多个子目录
        sub_dir = f"archives/personnel/batch_{i % 15}"
        os.makedirs(sub_dir, exist_ok=True)
        with open(os.path.join(sub_dir, f"profile_{1000+i}.json"), "w") as f:
            json.dump(personnel_data, f)

    # 2. 构建产出档案碎片
    valid_projects = set()
    all_projects = [f"PRJ-{generate_random_string(6)}" for _ in range(500)]
    
    for i, prj in enumerate(all_projects):
        review_stat = random.choice(["approved", "pending", "rejected"])
        pub_state = random.choice(["published", "draft", "in_review"])
        
        # 强制制造一些有效的产出
        if i < 150:
            review_stat = "approved"
            pub_state = "published"
            
        if review_stat == "approved" and pub_state == "published":
            valid_projects.add(prj)
            
        pub_data = {
            "project_code": prj,
            "title": f"Study on {generate_random_string(10)}",
            "review_status": review_stat,
            "publication_state": pub_state,
            "year": random.randint(2015, 2023)
        }
        
        sub_dir = f"archives/publications/year_{pub_data['year']}/q_{random.randint(1,4)}"
        os.makedirs(sub_dir, exist_ok=True)
        with open(os.path.join(sub_dir, f"pub_{prj}.json"), "w") as f:
            json.dump(pub_data, f)

    # 3. 构建经费账单 (带有大量噪音和诱饵)
    total_txns = 1200
    all_txns = []
    
    for i in range(total_txns):
        txn_id = f"TXN-{10000+i}"
        faculty = random.choice(names)
        base_amount = round(random.uniform(100, 15000), 2)
        prj = random.choice(all_projects)
        
        # 混淆金额格式
        fmt_choice = random.choice([0, 1, 2, 3])
        if fmt_choice == 0:
            amt_str = f"${base_amount:,.2f}"
        elif fmt_choice == 1:
            amt_str = f" {base_amount} USD "
        elif fmt_choice == 2:
            amt_str = f"{base_amount}"
        else:
            amt_str = f"$ {base_amount:,.2f} USD"
            
        all_txns.append({
            "txn_id": txn_id,
            "faculty_name": faculty,
            "amount": amt_str,
            "project_ref": prj,
            "description": f"Exp {generate_random_string(4)}"
        })

    # 将数据分散到不同的 CSV 中，有些是 certified，有些是 draft
    df_txns = pd.DataFrame(all_txns)
    chunk_size = max(1, len(df_txns) // 30)
    chunks = [df_txns.iloc[start:start + chunk_size] for start in range(0, len(df_txns), chunk_size)]
    
    for idx, chunk in enumerate(chunks):
        # 20% 是废弃草稿，不应被读取
        if idx >= 30:
            break
        if random.random() < 0.2:
            file_name = f"ledger_part_{idx}_draft.csv"
        else:
            file_name = f"ledger_part_{idx}_certified.csv"
            
        sub_dir = f"archives/finance/ledgers/folder_{idx % 5}"
        os.makedirs(sub_dir, exist_ok=True)
        chunk.to_csv(os.path.join(sub_dir, file_name), index=False)

    # 生成一个完全无关的垃圾文件，测试抗干扰
    with open("archives/finance/ledgers/DO_NOT_READ_THIS.txt", "w") as f:
        f.write("This is some random garbage notes that might break the parser if read as CSV.")

if __name__ == "__main__":
    build_env()
