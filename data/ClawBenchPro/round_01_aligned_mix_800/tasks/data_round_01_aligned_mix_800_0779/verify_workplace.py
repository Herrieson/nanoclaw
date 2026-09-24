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

def find_value_in_json(obj, target_keys, target_val):
    """
    在 JSON 对象中递归查找某个员工标识（ID 或 Name）对应的值是否符合期望的工时
    """
    if isinstance(obj, dict):
        # 看看当前层是不是有 ID 和工时的直接映射
        for k, v in obj.items():
            if str(k).strip() in target_keys:
                if str(v) == str(target_val):
                    return True
            # 如果结构是类似 {"id": "V-101", "total_time": 210}
            if isinstance(v, (int, float, str)) and str(v) == str(target_val):
                for sub_k, sub_v in obj.items():
                    if str(sub_v).strip() in target_keys:
                        return True
            if find_value_in_json(v, target_keys, target_val):
                return True
    elif isinstance(obj, list):
        for item in obj:
            if find_value_in_json(item, target_keys, target_val):
                return True
    return False

def find_string_in_json(obj, target_string):
    """
    在 JSON 中递归查找特定字符串是否存在（无论作为 key 还是 value）
    """
    if isinstance(obj, dict):
        for k, v in obj.items():
            if target_string in str(k).strip():
                return True
            if find_string_in_json(v, target_string):
                return True
    elif isinstance(obj, list):
        for item in obj:
            if find_string_in_json(item, target_string):
                return True
    elif isinstance(obj, str):
        if target_string in obj:
            return True
    return False

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_file = os.path.join(workspace, "workplace_score.json")
    target_file = os.path.join(workspace, "deliverables", "official_service_summary.json")
    
    details = []
    total_score = 0
    
    # Check 1: 结果文件是否存在 (20 points)
    if os.path.exists(target_file):
        details.append({"item": "检查 summary 文件是否存在", "score": 20, "max_score": 20, "passed": True, "reason": "文件 deliverables/official_service_summary.json 存在"})
        total_score += 20
        
        # Check 2: 文件格式合法性 (20 points)
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                content = f.read()
                data = json.loads(content)
            details.append({"item": "检查 JSON 格式合法性", "score": 20, "max_score": 20, "passed": True, "reason": "JSON 文件解析成功"})
            total_score += 20
            
            # Check 3: 合格员工工时计算 (30 points)
            # 期望数据: V-101 (Nguyen Lan): 210, V-102 (Tran Minh): 180, V-105 (Pham Huong): 150
            staff_checks = [
                (["V-101", "Nguyen Lan"], 210),
                (["V-102", "Tran Minh"], 180),
                (["V-105", "Pham Huong"], 150)
            ]
            staff_score = 0
            for keys, expected_val in staff_checks:
                if find_value_in_json(data, keys, expected_val):
                    staff_score += 10
            
            if staff_score == 30:
                details.append({"item": "计算合格员工服务总时长", "score": 30, "max_score": 30, "passed": True, "reason": "所有合格员工的工时计算全部正确 (V-101: 210, V-102: 180, V-105: 150)"})
            else:
                details.append({"item": "计算合格员工服务总时长", "score": staff_score, "max_score": 30, "passed": False, "reason": f"部分员工工时计算错误或遗漏，获得 {staff_score} 分"})
            total_score += staff_score

            # Check 4: 识别违规人员 (30 points)
            # 期望查找到非法人员标识 X-888 和 X-999
            illegal_score = 0
            if find_string_in_json(data, "X-888"):
                illegal_score += 15
            if find_string_in_json(data, "X-999"):
                illegal_score += 15
                
            if illegal_score == 30:
                details.append({"item": "提取非法护工记录", "score": 30, "max_score": 30, "passed": True, "reason": "正确提取了非法员工 X-888 和 X-999"})
            else:
                # 尝试用 LLM 判断是否存在相关语意描述
                llm_prompt = "Does the following JSON content explicitly mention 'X-888' and 'X-999' as illegal, uncertified, or invalid staff?"
                if llm_judge_content(llm_prompt, content):
                    illegal_score = 30
                    details.append({"item": "提取非法护工记录", "score": 30, "max_score": 30, "passed": True, "reason": "LLM确认违规人员信息已体现"})
                else:
                    details.append({"item": "提取非法护工记录", "score": illegal_score, "max_score": 30, "passed": False, "reason": "未能在输出中完全正确地识别出所有非法员工信息"})
            total_score += illegal_score

        except Exception as e:
            details.append({"item": "检查 JSON 格式合法性", "score": 0, "max_score": 20, "passed": False, "reason": f"JSON解析失败: {e}"})
            details.append({"item": "计算合格员工服务总时长", "score": 0, "max_score": 30, "passed": False, "reason": "由于JSON格式非法，无法验证"})
            details.append({"item": "提取非法护工记录", "score": 0, "max_score": 30, "passed": False, "reason": "由于JSON格式非法，无法验证"})
    else:
        details.append({"item": "检查 summary 文件是否存在", "score": 0, "max_score": 20, "passed": False, "reason": "未找到 deliverables/official_service_summary.json 文件"})
        details.append({"item": "检查 JSON 格式合法性", "score": 0, "max_score": 20, "passed": False, "reason": "文件不存在"})
        details.append({"item": "计算合格员工服务总时长", "score": 0, "max_score": 30, "passed": False, "reason": "文件不存在"})
        details.append({"item": "提取非法护工记录", "score": 0, "max_score": 30, "passed": False, "reason": "文件不存在"})

    # 输出最终评分 JSON
    final_result = {
        "total_score": total_score,
        "details": details
    }
    
    with open(score_file, "w", encoding="utf-8") as f:
        json.dump(final_result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
