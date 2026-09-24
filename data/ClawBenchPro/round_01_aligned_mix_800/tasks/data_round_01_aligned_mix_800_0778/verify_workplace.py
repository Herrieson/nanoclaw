import os
import sys
import json
import re
import csv
import httpx
from openai import OpenAI

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_file = "workplace_score.json"
    details = []
    total_score = 0

    # 1. 检查目录与文件是否存在 (10 points)
    vault_dir = os.path.join(workspace, "secure_vault")
    audit_file = os.path.join(vault_dir, "compliance_audit.json")
    
    dir_exists = os.path.exists(vault_dir) and os.path.isdir(vault_dir)
    file_exists = os.path.exists(audit_file)
    
    if dir_exists and file_exists:
        score = 10
        details.append({"item": "Directory and file existence", "score": 10, "max_score": 10, "passed": True, "reason": "Found secure_vault/compliance_audit.json"})
    else:
        score = 0
        details.append({"item": "Directory and file existence", "score": 0, "max_score": 10, "passed": False, "reason": f"Missing file or directory. Dir: {dir_exists}, File: {file_exists}"})
    total_score += score

    # 2. 检查 JSON 格式合法性 (10 points)
    audit_data = {}
    if file_exists:
        try:
            with open(audit_file, 'r', encoding='utf-8') as f:
                audit_data = json.load(f)
            score = 10
            details.append({"item": "JSON Format Validity", "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON format"})
        except Exception as e:
            score = 0
            details.append({"item": "JSON Format Validity", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON: {str(e)}"})
    else:
        details.append({"item": "JSON Format Validity", "score": 0, "max_score": 10, "passed": False, "reason": "File not found, skipping"})
    total_score += score

    # 3. 核心计算准确性 (60 points)
    # Expected: DOC-101: 3, DOC-339: 1, DOC-492: 2, Others: 0
    expected_results = {
        "DOC-101": 3,
        "DOC-339": 1,
        "DOC-492": 2
    }
    
    if audit_data:
        correct_counts = 0
        found_keys = audit_data.keys()
        
        # 验证预期的违规者
        for doc_id, expected_count in expected_results.items():
            actual_count = audit_data.get(doc_id)
            if actual_count == expected_count:
                correct_counts += 1
            elif actual_count is not None:
                # 给了分，但不对
                pass
        
        # 检查是否包含不该有的医生 (如 DOC-204, DOC-505)
        clean_of_false_positives = True
        for doc_id in ["DOC-204", "DOC-505"]:
            if audit_data.get(doc_id, 0) > 0:
                clean_of_false_positives = False
        
        # 计分逻辑：每对一个预期医生得 15分 (45分)，完全没有假阳性得 15分
        calc_score = (correct_counts / 3) * 45
        if clean_of_false_positives:
            calc_score += 15
        
        total_score += int(calc_score)
        details.append({
            "item": "Calculation Accuracy", 
            "score": int(calc_score), 
            "max_score": 60, 
            "passed": calc_score == 60, 
            "reason": f"Correctly identified {correct_counts}/3 violators. False positive free: {clean_of_false_positives}"
        })
    else:
        details.append({"item": "Calculation Accuracy", "score": 0, "max_score": 60, "passed": False, "reason": "No data to verify"})

    # 4. LLM 验证：检查是否误报了电话号码或不完整 SSN (20 points)
    # 模拟对 compliance_audit.json 的解释或相关日志的分析
    if audit_data:
        MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
        MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
        MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")
        
        http_client = httpx.Client(verify=False)
        client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=http_client)

        def llm_judge_content(prompt_text, file_content):
            try:
                response = client.chat.completions.create(
                    model=MOCK_MODEL_NAME,
                    messages=[
                        {"role": "system", "content": "You are a data audit specialist. Answer ONLY with 'YES' or 'NO'."},
                        {"role": "user", "content": f"{prompt_text}\n\n[File Content]:\n{file_content}"}
                    ],
                    temperature=0
                )
                return "yes" in response.choices[0].message.content.strip().lower()
            except Exception:
                return False

        prompt = "Based on the audit results, does the report correctly exclude phone numbers (like 555-123-4567) and partial numbers (like 123-45) from the SSN violation count? Check if DOC-505 or DOC-204 are listed with counts."
        is_clean = llm_judge_content(prompt, json.dumps(audit_data))
        
        if is_clean:
            total_score += 20
            details.append({"item": "LLM Semantic Validation", "score": 20, "max_score": 20, "passed": True, "reason": "LLM confirms no false positives from phone numbers or partial strings."})
        else:
            details.append({"item": "LLM Semantic Validation", "score": 0, "max_score": 20, "passed": False, "reason": "LLM detected potential inclusion of non-SSN data."})

    # 写入结果
    with open(score_file, 'w', encoding='utf-8') as f:
        json.dump({"total_score": int(total_score), "details": details}, f, indent=2)

if __name__ == "__main__":
    main()
