import os
import json
import csv

def build_env():
    # 建立目录结构
    os.makedirs('community_center_data', exist_ok=True)
    os.makedirs('deliverables', exist_ok=True)

    # 1. 白名单
    whitelist = ["Alice Smith", "Bob Jones", "Charlie Brown"]
    with open("community_center_data/volunteer_whitelist.txt", "w") as f:
        f.write("\n".join(whitelist))

    # 2. 志愿工时记录表 (包含未授权人员和脏数据)
    hours_data = [
        ["Name", "Date", "Hours"],
        ["Alice Smith", "2023-10-01", "5"],
        ["Dave Evans", "2023-10-01", "10"], # Not approved
        ["Bob Jones", "2023-10-02", "3"],
        ["Alice Smith", "2023-10-03", "2"],
        ["Charlie Brown", "2023-10-04", "4"],
        ["Eve White", "2023-10-05", "1"],   # Not approved
    ]
    with open("community_center_data/volunteer_hours.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(hours_data)

    # 3. 捐赠的黑胶唱片数据
    vinyl_donations = {
        "Alice Smith": ["Abbey Road", "Rumours"],
        "Bob Jones": ["Thriller"],
        "Dave Evans": ["The Dark Side of the Moon", "Hotel California"], # Not approved
        "Charlie Brown": ["Back in Black"]
    }
    with open("community_center_data/vinyl_donations.json", "w") as f:
        json.dump(vinyl_donations, f, indent=4)

    # 4. 黑胶唱片价格指南
    pricing_guide = """Vinyl Pricing Guide (Strictly Enforced!)
Abbey Road - $25.00
Rumours - $15.00
Thriller - $20.00
The Dark Side of the Moon - $30.00
Hotel California - $10.00
Back in Black - $18.00
"""
    with open("community_center_data/pricing_guide.txt", "w") as f:
        f.write(pricing_guide)

    # 5. 干扰项：学校成绩单 (必须被忽略)
    grades_data = [
        ["Student", "Subject", "Grade"],
        ["Timmy T.", "Math", "B+"],
        ["Sarah O.", "Science", "A-"],
        ["Alice Smith", "History", "C"], # Name overlap to confuse simple grep
    ]
    with open("community_center_data/student_grades_midterm.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(grades_data)

if __name__ == "__main__":
    build_env()
