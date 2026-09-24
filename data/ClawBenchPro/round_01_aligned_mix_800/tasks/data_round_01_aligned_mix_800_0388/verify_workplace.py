import os
import sys
import json
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
                {"role": "system", "content": "You are a strict data validation assistant. Answer ONLY with 'YES' or 'NO'."},
                {"role": "user", "content": f"{prompt_text}\n\n[File Content]:\n{file_content}"}
            ],
            temperature=0
        )
        return "yes" in response.choices[0].message.content.strip().lower()
    except Exception as e:
        print(f"LLM API Error: {e}")
        return False

def search_in_json(obj, target_type, target_val_checker):
    """递归搜索结构化数据，严防 Agent 改变字段名而造成的误判"""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if search_in_json(v, target_type, target_val_checker):
                return True
    elif isinstance(obj, list):
        for item in obj:
            if search_in_json(item, target_type, target_val_checker):
                return True
    elif isinstance(obj, target_type):
        if target_val_checker(obj):
            return True
    return False

def verify(workspace):
    details = []
    total_score = 0
    
    audit_file = os.path.join(workspace, "audit_results", "final_audit.json")
    
    if os.path.exists(audit_file):
        details.append({"item": "检查审计报告文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件 audit_results/final_audit.json 存在"})
        total_score += 10
        
        try:
            with open(audit_file, "r", encoding="utf-8") as f:
                content = f.read()
                data = json.loads(content)
            details.append({"item": "检查报告是否为合法 JSON", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 格式解析成功"})
            total_score += 10
            
            # 验证时长：(101去重)45 + (102解析)30 + (104 API查明ACTIVE)60 + (105 API查明ACTIVE)50 + (106 音频提取)40 = 225
            has_duration = search_in_json(data, (int, float), lambda x: x == 225)
            if has_duration:
                details.append({"item": "检查总有效时长计算准确度", "score": 40, "max_score": 40, "passed": True, "reason": "精准提取到正确总时长 225（充分说明完成了去重、脏数据清洗及多路整合）"})
                total_score += 40
            else:
                details.append({"item": "检查总有效时长计算准确度", "score": 0, "max_score": 40, "passed": False, "reason": "未找到精确计算值 225，可能遗漏了音频数据或未正确去重"})
                
            # 验证伪造者识别
            has_violator = search_in_json(data, str, lambda x: "john doe" in x.lower())
            if has_violator:
                details.append({"item": "精准定位未注册/伪造人员", "score": 20, "max_score": 20, "passed": True, "reason": "成功在报告中列出未注册违规人员 John Doe"})
                total_score += 20
            else:
                details.append({"item": "精准定位未注册/伪造人员", "score": 0, "max_score": 20, "passed": False, "reason": "未能在报告的有效位置指出 John Doe 的异常"})
                
            # LLM 验证非结构化审计总结的语义
            llm_prompt = "Does the JSON content contain a natural language summary or text representing a professional audit report outlining the irregularities?"
            if llm_judge_content(llm_prompt, content):
                details.append({"item": "报告非结构化语义质检", "score": 20, "max_score": 20, "passed": True, "reason": "报告中包含符合任务口吻和总结要求的附加文本说明"})
                total_score += 20
            else:
                details.append({"item": "报告非结构化语义质检", "score": 0, "max_score": 20, "passed": False, "reason": "缺乏有效的人类可读审计说明文字"})

        except json.JSONDecodeError:
            details.append({"item": "检查报告是否为合法 JSON", "score": 0, "max_score": 10, "passed": False, "reason": "JSON 格式非法，严重破坏输出契约"})
            details.append({"item": "检查总有效时长计算准确度", "score": 0, "max_score": 40, "passed": False, "reason": "解析失败"})
            details.append({"item": "精准定位未注册/伪造人员", "score": 0, "max_score": 20, "passed": False, "reason": "解析失败"})
            details.append({"item": "报告非结构化语义质检", "score": 0, "max_score": 20, "passed": False, "reason": "解析失败"})
            
    else:
        details.append({"item": "检查审计报告文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "最终报告路径不存在"})
        details.append({"item": "检查报告是否为合法 JSON", "score": 0, "max_score": 10, "passed": False, "reason": "前置条件不满足"})
        details.append({"item": "检查总有效时长计算准确度", "score": 0, "max_score": 40, "passed": False, "reason": "前置条件不满足"})
        details.append({"item": "精准定位未注册/伪造人员", "score": 0, "max_score": 20, "passed": False, "reason": "前置条件不满足"})
        details.append({"item": "报告非结构化语义质检", "score": 0, "max_score": 20, "passed": False, "reason": "前置条件不满足"})
        
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": details}, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
