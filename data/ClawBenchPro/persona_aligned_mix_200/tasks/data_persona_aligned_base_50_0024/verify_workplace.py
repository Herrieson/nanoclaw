import os
import sys
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 初始化客户端，必须关闭 SSL 验证
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    # 此函数为检测非结构化文本的统一接口
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a strict data validation assistant. Answer ONLY with 'YES' or 'NO'."},
                {"role": "user", "content": f"{prompt_text}\n\n[File Content]:\n{file_content}"}
            ],
            temperature=0
        )
        return "yes" in response.choices[0].message.content.strip().lower()
    except Exception as e:
        print(f"LLM API Error: {e}")
        return False

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    score_details = []
    total_score = 0
    
    target_file = os.path.join(workspace, "hotfix", "version_pin.json")
    
    # Check 1: File Existence (10 points)
    file_exists = os.path.exists(target_file)
    if file_exists:
        score_details.append({"item": "检查热更配置文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件 hotfix/version_pin.json 存在"})
        total_score += 10
    else:
        score_details.append({"item": "检查热更配置文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件 hotfix/version_pin.json 缺失"})
        
    data = None
    if file_exists:
        # Check 2: JSON format (10 points)
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            score_details.append({"item": "检查文件是否为合法 JSON", "score": 10, "max_score": 10, "passed": True, "reason": "成功解析 JSON 格式"})
            total_score += 10
        except Exception as e:
            score_details.append({"item": "检查文件是否为合法 JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {e}"})
            
    if data and isinstance(data, dict):
        # Check 3: Required Fields Presence (10 points)
        required_fields = {"conflict_pkg", "bad_version", "system_version"}
        actual_fields = set(data.keys())
        missing = required_fields - actual_fields
        extra = actual_fields - required_fields
        
        if not missing:
            score_details.append({"item": "检查是否包含全部必填字段", "score": 10, "max_score": 10, "passed": True, "reason": "需要的三个核心字段全部存在"})
            total_score += 10
        else:
            score_details.append({"item": "检查是否包含全部必填字段", "score": 0, "max_score": 10, "passed": False, "reason": f"缺失必要字段: {missing}"})
            
        # Check 4: No Extra Fields (10 points)
        if not extra:
            score_details.append({"item": "检查是否捏造多余字段防幻觉", "score": 10, "max_score": 10, "passed": True, "reason": "未发现多余字段，输出符合最简结构要求"})
            total_score += 10
        else:
            score_details.append({"item": "检查是否捏造多余字段防幻觉", "score": 0, "max_score": 10, "passed": False, "reason": f"包含不被允许的额外字段: {extra}"})
            
        # Check 5: conflict_pkg accuracy (20 points)
        conflict_pkg = data.get("conflict_pkg", "")
        if isinstance(conflict_pkg, str) and (conflict_pkg.strip() == "boost-python-deps" or conflict_pkg.strip() == "boost_python_deps"):
            score_details.append({"item": "准确提取导致崩溃的冲突包名", "score": 20, "max_score": 20, "passed": True, "reason": f"正确识别引发崩溃的 Python 依赖库: {conflict_pkg}"})
            total_score += 20
        else:
            score_details.append({"item": "准确提取导致崩溃的冲突包名", "score": 0, "max_score": 20, "passed": False, "reason": f"识别的冲突包错误或类型异常: {conflict_pkg}"})
            
        # Check 6: bad_version accuracy (20 points)
        bad_version = data.get("bad_version", "")
        if isinstance(bad_version, str) and bad_version.strip() == "1.81.0":
            score_details.append({"item": "精确提取错误注入的库高版本号", "score": 20, "max_score": 20, "passed": True, "reason": "完美匹配错误的高版本 1.81.0"})
            total_score += 20
        else:
            score_details.append({"item": "精确提取错误注入的库高版本号", "score": 0, "max_score": 20, "passed": False, "reason": f"版本号抽取错误: {bad_version}"})
            
        # Check 7: system_version accuracy (20 points)
        system_version = data.get("system_version", "")
        if isinstance(system_version, str) and system_version.strip() == "1.74.0":
            score_details.append({"item": "精确探测系统底层所需底座版本号", "score": 20, "max_score": 20, "passed": True, "reason": "成功反查到系统真实预期的 C++ 底座版本 1.74.0"})
            total_score += 20
        else:
            score_details.append({"item": "精确探测系统底层所需底座版本号", "score": 0, "max_score": 20, "passed": False, "reason": f"提取系统底座版本号错误: {system_version}"})
    else:
        # Fallback for failing condition 3-7 when dict parsing fails
        score_details.append({"item": "检查是否包含全部必填字段", "score": 0, "max_score": 10, "passed": False, "reason": "非有效 JSON 字典"})
        score_details.append({"item": "检查是否捏造多余字段防幻觉", "score": 0, "max_score": 10, "passed": False, "reason": "非有效 JSON 字典"})
        score_details.append({"item": "准确提取导致崩溃的冲突包名", "score": 0, "max_score": 20, "passed": False, "reason": "无法读取字段"})
        score_details.append({"item": "精确提取错误注入的库高版本号", "score": 0, "max_score": 20, "passed": False, "reason": "无法读取字段"})
        score_details.append({"item": "精确探测系统底层所需底座版本号", "score": 0, "max_score": 20, "passed": False, "reason": "无法读取字段"})
        
    result = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
