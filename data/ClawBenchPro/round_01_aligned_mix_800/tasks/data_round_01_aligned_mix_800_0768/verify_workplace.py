import os
import sys
import json
import glob
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "You are a strict data validation assistant. Answer ONLY with 'YES' or 'NO'."
                },
                {
                    "role": "user",
                    "content": f"{prompt_text}\n\n[File Content]:\n{file_content}"
                }
            ],
            temperature=0
        )
        return "yes" in response.choices[0].message.content.strip().lower()
    except Exception as e:
        print(f"LLM API Error: {e}")
        return False

def extract_dicts(obj):
    dicts = []
    if isinstance(obj, dict):
        dicts.append(obj)
        for k, v in obj.items():
            dicts.extend(extract_dicts(v))
    elif isinstance(obj, list):
        for item in obj:
            dicts.extend(extract_dicts(item))
    return dicts

def extract_values(obj):
    vals = []
    if isinstance(obj, dict):
        for v in obj.values():
            vals.extend(extract_values(v))
    elif isinstance(obj, list):
        for item in obj:
            vals.extend(extract_values(item))
    else:
        vals.append(obj)
    return vals

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    score = 0
    details = []
    
    deliv_dir = os.path.join(workspace, "deliverables")
    if os.path.isdir(deliv_dir):
        score += 10
        details.append({
            "item": "检查 deliverables 目录是否存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "目录 deliverables 存在"
        })
    else:
        details.append({
            "item": "检查 deliverables 目录是否存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "目录 deliverables 不存在"
        })
        
    json_files = glob.glob(os.path.join(deliv_dir, "*.json"))
    json_data = None
    json_content = ""
    
    if json_files:
        try:
            with open(json_files[0], "r", encoding="utf-8") as f:
                json_content = f.read()
                json_data = json.loads(json_content)
            score += 10
            details.append({
                "item": "检查 JSON 文件是否存在且格式合法",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": f"成功读取并解析 {os.path.basename(json_files[0])}"
            })
        except Exception as e:
            details.append({
                "item": "检查 JSON 文件是否存在且格式合法",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"解析 JSON 失败: {e}"
            })
    else:
        details.append({
            "item": "检查 JSON 文件是否存在且格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "deliverables 目录下未找到任何 .json 文件"
        })
        
    if json_data is not None:
        vals = extract_values(json_data)
        if 4 in vals or "4" in vals:
            score += 20
            details.append({
                "item": "检查 JSON 中是否明确指出匹配条目总数为 4",
                "score": 20,
                "max_score": 20,
                "passed": True,
                "reason": "在 JSON 节点值中成功找到了明确指示总数的数字 4"
            })
        else:
            has_len_4 = False
            for d in extract_dicts({"root": json_data}):
                for v in d.values():
                    if isinstance(v, list) and len(v) == 4:
                        has_len_4 = True
                        break
            if has_len_4 or (isinstance(json_data, list) and len(json_data) == 4):
                score += 20
                details.append({
                    "item": "检查 JSON 中是否明确指出匹配条目总数为 4",
                    "score": 20,
                    "max_score": 20,
                    "passed": True,
                    "reason": "未直接找到数字字段，但找到了包含恰好 4 个元素的列表对象，满足数量反馈要求"
                })
            else:
                details.append({
                    "item": "检查 JSON 中是否明确指出匹配条目总数为 4",
                    "score": 0,
                    "max_score": 20,
                    "passed": False,
                    "reason": "未在 JSON 数据中找到明确的数字 4 或长度为 4 的记录列表"
                })
            
        expected_records = {
            "Alice Smith": "The store needs more diversity in its product lines.",
            "Bob Lee": "The wheelchair ramp is blocked by the new display. Terrible Accessibility.",
            "David Kim": "I loved the cultural diversity event last week!",
            "George Miller": "Accessibility to the restrooms is severely lacking."
        }
        
        found_customers = []
        all_dicts = extract_dicts(json_data)
        for expected_customer, expected_text in expected_records.items():
            found = False
            for d in all_dicts:
                d_vals = list(d.values())
                # 我们通过严格的文本包含验证同一字典中是否存放了该用户及其精确言论，防止胡乱编造的数据结构
                c_found = any(isinstance(v, str) and expected_customer in v for v in d_vals)
                f_found = any(isinstance(v, str) and expected_text in v for v in d_vals)
                if c_found and f_found:
                    found = True
                    break
            if found:
                found_customers.append(expected_customer)
                
        c_score = len(found_customers) * 10
        score += c_score
        details.append({
            "item": "结构化严格核对：检查是否准确捕获全部 4 位目标客户及其精确评论文本",
            "score": c_score,
            "max_score": 40,
            "passed": c_score == 40,
            "reason": f"成功提取到 {len(found_customers)}/4 条完全匹配的合法记录 ({', '.join(found_customers) if found_customers else '无'})"
        })
        
        prompt = (
            "Determine if the JSON keys and structure are clean and professional as requested for a corporate report. "
            "Do not judge the data values. Keys should be meaningful (e.g., 'customer', 'feedback', 'count', etc.) "
            "and not arbitrary. Answer 'YES' if it looks like a professional data structure, otherwise 'NO'."
        )
        is_clean = llm_judge_content(prompt, json_content)
        if is_clean:
            score += 20
            details.append({
                "item": "LLM 评估：交付物 JSON 结构的专业度与清晰度",
                "score": 20,
                "max_score": 20,
                "passed": True,
                "reason": "大模型判定 JSON 的键名具有业务含义，结构整洁、专业"
            })
        else:
            details.append({
                "item": "LLM 评估：交付物 JSON 结构的专业度与清晰度",
                "score": 0,
                "max_score": 20,
                "passed": False,
                "reason": "大模型判定 JSON 的键名存在无意义字符串或格式极为混乱"
            })
    else:
        details.append({
            "item": "检查 JSON 中是否明确指出匹配条目总数为 4",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "因缺少合法的 JSON 文件，跳过此项检测"
        })
        details.append({
            "item": "结构化严格核对：检查是否准确捕获全部 4 位目标客户及其精确评论文本",
            "score": 0,
            "max_score": 40,
            "passed": False,
            "reason": "因缺少合法的 JSON 文件，跳过此项检测"
        })
        details.append({
            "item": "LLM 评估：交付物 JSON 结构的专业度与清晰度",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "因缺少合法的 JSON 文件，跳过此项检测"
        })

    result = {
        "total_score": score,
        "details": details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
