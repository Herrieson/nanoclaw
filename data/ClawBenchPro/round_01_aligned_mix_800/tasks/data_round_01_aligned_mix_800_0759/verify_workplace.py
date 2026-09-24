import os
import sys
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 初始化客户端，强制关闭 SSL 验证
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

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    deliverables_dir = os.path.join(workspace, "deliverables")
    
    # 1. 检查 deliverables 目录
    if os.path.isdir(deliverables_dir):
        details.append({"item": "检查 deliverables 目录是否存在", "score": 5, "max_score": 5, "passed": True, "reason": "目录 deliverables 存在"})
        score += 5
    else:
        details.append({"item": "检查 deliverables 目录是否存在", "score": 0, "max_score": 5, "passed": False, "reason": "目录 deliverables 不存在"})
    
    # 2. 检查 ready_for_crm.json 文件及其内容
    crm_file = os.path.join(deliverables_dir, "ready_for_crm.json")
    if os.path.isfile(crm_file):
        details.append({"item": "检查 ready_for_crm.json 文件是否存在", "score": 5, "max_score": 5, "passed": True, "reason": "文件 ready_for_crm.json 存在"})
        score += 5
        
        try:
            with open(crm_file, "r", encoding="utf-8") as f:
                crm_data = json.load(f)
            
            details.append({"item": "ready_for_crm.json 格式合法性", "score": 5, "max_score": 5, "passed": True, "reason": "成功解析为原生 JSON 格式"})
            score += 5
            
            # 兼容处理：支持 [{}] 或 {"leads": [{}]} 形式
            records = []
            if isinstance(crm_data, list):
                records = crm_data
            elif isinstance(crm_data, dict) and len(crm_data) == 1:
                key = list(crm_data.keys())[0]
                if isinstance(crm_data[key], list):
                    records = crm_data[key]
            
            if not records:
                details.append({"item": "CRM 根结构需为包含字典的 JSON 列表", "score": 0, "max_score": 55, "passed": False, "reason": "根结构或主要键值不是列表，无法提取确定的数据"})
            else:
                names = [str(r.get("Company_Name", "")).strip() for r in records if isinstance(r, dict)]
                
                # TechNova Solutions 判断 (附带信息完整性校验)
                technova_valid = False
                for r in records:
                    if r.get("Company_Name") == "TechNova Solutions" and str(r.get("Phone")) == "5551234567" and r.get("District") == "East":
                        technova_valid = True
                        break
                
                if technova_valid:
                    details.append({"item": "CRM 包含 TechNova Solutions 且数据不被篡改", "score": 15, "max_score": 15, "passed": True, "reason": "完全正确的 TechNova 商业线索"})
                    score += 15
                else:
                    details.append({"item": "CRM 包含 TechNova Solutions 且数据不被篡改", "score": 0, "max_score": 15, "passed": False, "reason": "遗漏 TechNova 线索或其字段值（地区/电话）被破坏"})

                # Eastern Telecom Partners 判断
                eastern_valid = False
                for r in records:
                    if r.get("Company_Name") == "Eastern Telecom Partners" and str(r.get("Phone")) == "1234567890":
                        eastern_valid = True
                        break
                
                if eastern_valid:
                    details.append({"item": "CRM 包含 Eastern Telecom Partners 且数据未被篡改", "score": 15, "max_score": 15, "passed": True, "reason": "完全正确的 Eastern Telecom 商业线索"})
                    score += 15
                else:
                    details.append({"item": "CRM 包含 Eastern Telecom Partners 且数据未被篡改", "score": 0, "max_score": 15, "passed": False, "reason": "遗漏 Eastern Telecom 线索或电话被破坏"})

                # 排除错误数据严酷测试 (不能包含其他非10位纯数字、非对应地区、非对应类型的数据)
                bad_names = {
                    "Downtown Soup Kitchen", "Westside Plumbers", "South District Retail", 
                    "Alpha Logistics", "Crescent Community Center", "Northside Cafe", "Global Imports"
                }
                found_bad = set(names).intersection(bad_names)
                if not found_bad and len(names) == 2:
                    details.append({"item": "CRM 严格排除了所有的不合格线索，且未捏造假数据", "score": 25, "max_score": 25, "passed": True, "reason": "极度干净的数据管道，没有混入不合法记录"})
                    score += 25
                else:
                    details.append({"item": "CRM 严格排除了所有的不合格线索，且未捏造假数据", "score": 0, "max_score": 25, "passed": False, "reason": f"拦截失败，发现错误记录或捏造了多余的结构: {found_bad if found_bad else '条目总数不符'}"})

        except Exception as e:
            details.append({"item": "ready_for_crm.json 解析", "score": 0, "max_score": 60, "passed": False, "reason": f"文件不合法或报错: {e}"})
    else:
        details.append({"item": "检查 ready_for_crm.json 文件是否存在", "score": 0, "max_score": 65, "passed": False, "reason": "文件 ready_for_crm.json 不存在"})
    
    # 3. 检查 volunteer_contacts.txt 文件及其内容
    volunteer_file = os.path.join(deliverables_dir, "volunteer_contacts.txt")
    if os.path.isfile(volunteer_file):
        details.append({"item": "检查 volunteer_contacts.txt 文件是否存在", "score": 5, "max_score": 5, "passed": True, "reason": "文件 volunteer_contacts.txt 存在"})
        score += 5
        
        try:
            with open(volunteer_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
            
            prompt1 = "Does this text contain BOTH the names and the emails of 'Downtown Soup Kitchen' (help@downtownsoup.org) AND 'Crescent Community Center' (director@crescentcc.org) clearly? Answer YES or NO."
            if llm_judge_content(prompt1, content):
                details.append({"item": "LLM验证志愿者文件是否正确包含两家机构及其邮箱", "score": 15, "max_score": 15, "passed": True, "reason": "准确抓取并导出了对应非营利机构的信息"})
                score += 15
            else:
                details.append({"item": "LLM验证志愿者文件是否正确包含两家机构及其邮箱", "score": 0, "max_score": 15, "passed": False, "reason": "内容有缺失或邮箱未能精准匹配"})
            
            prompt2 = "Does this text strictly EXCLUDE other unrelated corporate or business leads like 'TechNova', 'Westside Plumbers', 'Alpha Logistics', 'Eastern Telecom' etc.? In other words, is it ONLY about the soup kitchen and the community center? Answer YES or NO."
            if llm_judge_content(prompt2, content):
                details.append({"item": "LLM验证志愿者文件是否排除了商业销售线索", "score": 10, "max_score": 10, "passed": True, "reason": "文本极其纯净，没有混入无关线索"})
                score += 10
            else:
                details.append({"item": "LLM验证志愿者文件是否排除了商业销售线索", "score": 0, "max_score": 10, "passed": False, "reason": "未能遵守职责分离原则，混入了推销线索数据"})

        except Exception as e:
            details.append({"item": "读取 volunteer_contacts.txt 失败", "score": 0, "max_score": 25, "passed": False, "reason": f"文件读取报错: {e}"})
    else:
        details.append({"item": "检查 volunteer_contacts.txt 文件是否存在", "score": 0, "max_score": 30, "passed": False, "reason": "文件 volunteer_contacts.txt 不存在"})
    
    # 写入得分报告
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": score, "details": details}, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
