#!/usr/bin/env python3
import os
import sys
import json
import httpx
from openai import OpenAI

# 强制按照规范读取环境变量与初始化客户端，并关闭 SSL 验证
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
    """大模型语义检测接口，统一应对非结构化或多变格式的语义判断"""
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

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    deliverables_dir = os.path.join(workspace, "deliverables")
    sitrep_file = os.path.join(deliverables_dir, "sitrep.json")
    
    score = 0
    details = []

    # 1. 检查 deliverables 目录 (10分)
    if os.path.isdir(deliverables_dir):
        score += 10
        details.append({"item": "检查目标目录 deliverables 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录存在"})
    else:
        details.append({"item": "检查目标目录 deliverables 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "目录不存在"})

    # 2. 检查 sitrep.json 文件存在及基础结构 (10分)
    is_valid_json = False
    json_data = None
    if os.path.isfile(sitrep_file):
        try:
            with open(sitrep_file, "r", encoding="utf-8") as f:
                json_data = json.load(f)
            is_valid_json = True
            score += 10
            details.append({"item": "检查 sitrep.json 是否存在且为合法 JSON", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在且解析成功"})
        except Exception as e:
            details.append({"item": "检查 sitrep.json 是否存在且为合法 JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"文件解析失败: {e}"})
    else:
        details.append({"item": "检查 sitrep.json 是否存在且为合法 JSON", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})

    # 3. 严格数据名单过滤检查 (20分) - 严查是否发生幻觉或混入错误数据
    if is_valid_json and isinstance(json_data, list):
        expected_names = {"Timmy Smith", "Sarah Connor", "Chris Evans", "Emma Stone"}
        actual_names = {str(item.get("Name", "")).strip() for item in json_data if isinstance(item, dict) and "Name" in item}
        if len(json_data) == 4 and actual_names == expected_names:
            score += 20
            details.append({"item": "检查人员过滤 (严格提取4名符合条件的 Dependents)", "score": 20, "max_score": 20, "passed": True, "reason": "精准提取了4人且没有多余、遗漏或作弊数据"})
        else:
            details.append({"item": "检查人员过滤 (严格提取4名符合条件的 Dependents)", "score": 0, "max_score": 20, "passed": False, "reason": f"提取的人员名单不精确。期望: {expected_names}, 实际: {actual_names}, 总记录数: {len(json_data)}"})
    else:
        details.append({"item": "检查人员过滤 (严格提取4名符合条件的 Dependents)", "score": 0, "max_score": 20, "passed": False, "reason": "JSON非列表格式，无法执行条目检查"})

    # 4. 代码级精细验证：Age 与 Assigned_Exhibit 映射 (30分)
    if is_valid_json and isinstance(json_data, list):
        mapping_expectations = {
            "Timmy Smith": {"Age": 8, "Exhibit": "Potawatomi_Crafts"},
            "Emma Stone": {"Age": 10, "Exhibit": "Potawatomi_Crafts"},
            "Sarah Connor": {"Age": 14, "Exhibit": "Navajo_Code_Talkers"},
            "Chris Evans": {"Age": 17, "Exhibit": "Navajo_Code_Talkers"}
        }
        correct_count = 0
        for item in json_data:
            if not isinstance(item, dict): continue
            name = str(item.get("Name", "")).strip()
            if name in mapping_expectations:
                exp = mapping_expectations[name]
                age = item.get("Age")
                exhibit = str(item.get("Assigned_Exhibit", "")).strip()
                try:
                    if int(age) == exp["Age"] and exhibit == exp["Exhibit"]:
                        correct_count += 1
                except:
                    pass
        
        mapping_score = int(30 * (correct_count / 4))
        score += mapping_score
        details.append({"item": "检查年龄与展区的计算映射精确性", "score": mapping_score, "max_score": 30, "passed": mapping_score == 30, "reason": f"4人中有 {correct_count} 人匹配精确的年龄及展区业务规则"})
    else:
        details.append({"item": "检查年龄与展区的计算映射精确性", "score": 0, "max_score": 30, "passed": False, "reason": "数据异常，无法检查业务映射"})

    # 5. LLM语义检查：Chow_Type 处理 (30分) - 处理非结构化口语化文字匹配
    if is_valid_json and isinstance(json_data, list) and len(json_data) > 0:
        chow_data = []
        for item in json_data:
            if isinstance(item, dict) and "Name" in item and "Chow_Type" in item:
                chow_data.append({"Name": item["Name"], "Chow_Type": item["Chow_Type"]})
        
        if chow_data:
            prompt_text = (
                "You are evaluating the 'Chow_Type' field assigned to specific personnel in a JSON log. "
                "The business rules state:\n"
                "- Timmy Smith -> Must receive 'standard MREs' or simply 'MREs'.\n"
                "- Emma Stone -> Must receive 'standard MREs' or simply 'MREs'.\n"
                "- Sarah Connor -> Must receive 'Special Chow'.\n"
                "- Chris Evans -> Must receive 'Special Chow'.\n\n"
                "Review the JSON provided below. It may contain varied casing (e.g., 'Standard MREs', 'special chow'). "
                "If the semantics for ALL of these specific named individuals perfectly align with the rules above, reply 'YES'. "
                "If any name is missing, has an incorrect meal type, or is completely unrelated to the dietary rule, reply 'NO'."
            )
            is_chow_correct = llm_judge_content(prompt_text, json.dumps(chow_data, ensure_ascii=False))
            if is_chow_correct:
                score += 30
                details.append({"item": "大模型检查 Chow_Type 语义合理性", "score": 30, "max_score": 30, "passed": True, "reason": "大模型判定饮食分类分配全对"})
            else:
                details.append({"item": "大模型检查 Chow_Type 语义合理性", "score": 0, "max_score": 30, "passed": False, "reason": "大模型判定饮食分类存在错误、无效或者幻觉"})
        else:
            details.append({"item": "大模型检查 Chow_Type 语义合理性", "score": 0, "max_score": 30, "passed": False, "reason": "未能提取到有效的 Name 或 Chow_Type 字段供语义分析"})
    else:
        details.append({"item": "大模型检查 Chow_Type 语义合理性", "score": 0, "max_score": 30, "passed": False, "reason": "数据结构异常无法检查"})

    # 统一落盘输出
    result = {
        "total_score": score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
