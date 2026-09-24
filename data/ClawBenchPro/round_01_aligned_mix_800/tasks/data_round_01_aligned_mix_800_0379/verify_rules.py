import os
import json

def verify():
    results = {
        "output_file_exists": False,
        "json_format_valid": False,
        "correct_unauthorized_detected": False,
        "math_accurate": False
    }
    
    output_path = "deliverables/official_service_summary.json"
    if os.path.exists(output_path):
        results["output_file_exists"] = True
        try:
            with open(output_path, "r") as f:
                data = json.load(f)
            results["json_format_valid"] = True
            
            # 预期合法人员工时：V-101: 210, V-102: 180, V-105: 150 (跳过坏数据)
            # 预期非法人员：X-999, X-888
            
            # 检查非法人员检测 (模糊匹配，只要JSON里提到了这两个ID或对应数量)
            content_str = json.dumps(data)
            if "X-999" in content_str and "X-888" in content_str:
                results["correct_unauthorized_detected"] = True
            
            # 检查关键数值计算
            if "210" in content_str and "180" in content_str and "150" in content_str:
                results["math_accurate"] = True
                
        except:
            pass

    with open("state.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
