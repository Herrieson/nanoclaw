import os
import json
import re

def verify():
    base_dir = "."
    drafts_dir = os.path.join(base_dir, "drafts")
    
    state = {
        "drafts_folder_exists": False,
        "expected_files_exist": False,
        "unexpected_files_exist": False,
        "premiums_correct": {}
    }
    
    # 根据 2023-10 和 Adventure Package 筛选出来的预期目标
    # 以及按照 1.05 比例计算的新保费
    expected_premiums = {
        "Alice": 1260.0,
        "Carol": 945.0,
        "Eve": 1155.0,
        "Grace": 1365.0,
        "Ivan": 892.5
    }
    
    if os.path.exists(drafts_dir) and os.path.isdir(drafts_dir):
        state["drafts_folder_exists"] = True
        files = os.listdir(drafts_dir)
        
        expected_filenames = [f"email_{name}.txt" for name in expected_premiums.keys()]
        
        # 检查是否有多余的错误邮件文件
        state["unexpected_files_exist"] = any(f.endswith('.txt') and f not in expected_filenames for f in files)
        # 检查是否所有的预期邮件文件都存在
        state["expected_files_exist"] = all(f in files for f in expected_filenames)
        
        for name, expected_amount in expected_premiums.items():
            file_path = os.path.join(drafts_dir, f"email_{name}.txt")
            state["premiums_correct"][name] = False
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                # 寻找内容中所有的数字（包含浮点数）来匹配是否包含正确的金额
                numbers = re.findall(r"\d+\.?\d*", content)
                for num_str in numbers:
                    try:
                        num = float(num_str)
                        if abs(num - expected_amount) < 0.01:
                            state["premiums_correct"][name] = True
                            break
                    except ValueError:
                        pass
    
    with open("verify_result.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
