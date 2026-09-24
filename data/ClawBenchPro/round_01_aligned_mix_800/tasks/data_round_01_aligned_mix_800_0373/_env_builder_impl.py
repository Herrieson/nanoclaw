import os
import pandas as pd

def build_env():
    # 创建目录
    os.makedirs("university_archives", exist_ok=True)
    os.makedirs("investigation_report", exist_ok=True)

    # 1. 教师白名单 (存疑点：Dr. Malicious 不在名单上)
    white_list = ["Dr. Aris", "Dr. Bhattacharya", "Dr. Chen", "Dr. Devi", "Dr. Evans"]
    with open("university_archives/faculty_white_list.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(white_list))

    # 2. 经费账目数据
    ledger_data = [
        {"id": "EXP-001", "faculty": "Dr. Bhattacharya", "amount": 1200, "project_code": "EDU-2023-A", "desc": "Books"},
        {"id": "EXP-002", "faculty": "Dr. Aris", "amount": 5500, "project_code": "EDU-2023-B", "desc": "Field Research"}, # 合法，大额但有产出(由LLM Mock提供)
        {"id": "EXP-003", "faculty": "Dr. Malicious", "amount": 8000, "project_code": "UNK-999", "desc": "Consulting"}, # 违规：不在名单
        {"id": "EXP-004", "faculty": "Dr. Chen", "amount": 6000, "project_code": "EDU-2023-C", "desc": "Conference"}, # 违规：大额但无产出
        {"id": "EXP-005", "faculty": "Dr. Devi", "amount": 450, "project_code": "EDU-2023-A", "desc": "Stationery"},
        {"id": "EXP-006", "faculty": "Dr. Evans", "amount": 7000, "project_code": "EDU-2023-D", "desc": "Software License"}, # 合法，大额有产出
        {"id": "EXP-007", "faculty": "Dr. Aris", "amount": 5200, "project_code": "EDU-2023-E", "desc": "Travel"}, # 违规：大额无产出
    ]
    df = pd.DataFrame(ledger_data)
    df.to_csv("university_archives/funding_ledger.csv", index=False)

    # 3. 干扰项 (提示本地产出文件已被删除)
    with open("university_archives/admin_memo.txt", "w") as f:
        f.write("CONFIDENTIAL: The local publication_outputs.json has been purged as per Dean's verbal request. Do not keep local copies of project outputs.")

if __name__ == "__main__":
    build_env()
