import os
import json

def verify():
    base_dir = "."
    script_path = os.path.join(base_dir, "distributor.py")
    results = {
        "api_key_updated": False,
        "syntax_error_fixed": False,
        "http_method_corrected": False,
        "auth_header_added": False,
        "job_triggered": False
    }

    if not os.path.exists(script_path):
        return results

    with open(script_path, "r") as f:
        content = f.read()
        
        # 检查 API Key
        if "PRINT_VIBES_2024_X" in content:
            results["api_key_updated"] = True
        
        # 检查除零错误是否移除
        if "10 / 0" not in content:
            results["syntax_error_fixed"] = True
            
        # 检查是否使用了 POST
        if "requests.post" in content:
            results["http_method_corrected"] = True
            
        # 检查是否添加了 Authorization header (简单匹配)
        if "headers" in content and "Authorization" in content:
            results["auth_header_added"] = True

    # 这种任务通常会检查 agent 是否执行了脚本并产生了预期的输出
    # 我们可以通过分析 agent 的 trace 来判定，或者检查它是否尝试访问了 localhost:5000
    # 在本沙盒环境中，我们通过静态分析和最后的操作记录来给分
    
    with open("verify_result.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
