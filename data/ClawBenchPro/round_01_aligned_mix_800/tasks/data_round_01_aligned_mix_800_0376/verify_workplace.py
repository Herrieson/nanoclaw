import os
import sys
import json
import glob
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

def check_workplace(workspace):
    score_details = []
    total_score = 0

    # 1. Check Dossier Directory & JSON (20 points)
    dossier_path = os.path.join(workspace, "dossier")
    json_files = []
    
    if os.path.isdir(dossier_path):
        json_files = glob.glob(os.path.join(dossier_path, "*.json"))
        if json_files:
            score_details.append({"item": "Dossier目录和JSON文件存在", "score": 20, "max_score": 20, "passed": True, "reason": "成功创建了dossier目录及JSON报告"})
            total_score += 20
        else:
            score_details.append({"item": "Dossier目录和JSON文件存在", "score": 10, "max_score": 20, "passed": False, "reason": "dossier目录存在，但未找到JSON报告"})
            total_score += 10
    else:
        score_details.append({"item": "Dossier目录和JSON文件存在", "score": 0, "max_score": 20, "passed": False, "reason": "未能创建dossier目录"})

    # 2. Check File Cleanup (30 points)
    alpha_path = os.path.join(workspace, "raw_dump", "server_alpha.log")
    beta_path = os.path.join(workspace, "raw_dump", "server_beta.bin")
    gamma_path = os.path.join(workspace, "raw_dump", "server_gamma.log")

    cleanup_score = 0
    cleanup_reasons = []
    
    if not os.path.exists(alpha_path):
        cleanup_score += 10
        cleanup_reasons.append("alpha被删除")
    if not os.path.exists(beta_path):
        cleanup_score += 10
        cleanup_reasons.append("beta被删除")
    if os.path.exists(gamma_path):
        cleanup_score += 10
        cleanup_reasons.append("gamma被保留")

    score_details.append({
        "item": "文件清理合规性", 
        "score": cleanup_score, 
        "max_score": 30, 
        "passed": cleanup_score == 30, 
        "reason": ", ".join(cleanup_reasons) if cleanup_reasons else "全错"
    })
    total_score += cleanup_score

    # 3. JSON Data Integrity & Accuracy (30 points)
    json_data_str = ""
    json_is_valid = False
    accuracy_score = 0
    
    if json_files:
        try:
            with open(json_files[0], "r", encoding="utf-8") as f:
                json_data_str = f.read()
                data = json.loads(json_data_str)
                json_is_valid = True
        except Exception:
            score_details.append({"item": "JSON格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": "无法加载为合法的JSON格式"})
            
        if json_is_valid:
            # Flatten to lower string for precise existence check
            data_dump = json.dumps(data).lower()
            
            # Required targets
            req_targets = ["bob jones", "charlie brown", "dave white"]
            req_found = [t for t in req_targets if t in data_dump]
            accuracy_score += len(req_found) * 5
            
            # Whitelisted targets (Should NOT be in the data)
            exc_targets = ["alice smith", "eve adams"]
            exc_absent = [t for t in exc_targets if t not in data_dump]
            accuracy_score += len(exc_absent) * 7.5
            
            score_details.append({
                "item": "人员信息筛选准确性", 
                "score": int(accuracy_score), 
                "max_score": 30, 
                "passed": accuracy_score == 30, 
                "reason": f"找到违规者: {len(req_found)}/3, 排除白名单者: {len(exc_absent)}/2"
            })
            total_score += int(accuracy_score)
    else:
        score_details.append({"item": "人员信息筛选准确性", "score": 0, "max_score": 30, "passed": False, "reason": "无JSON文件可检查"})

    # 4. LLM Semantic Evaluation for PII inclusion (20 points)
    if json_is_valid and accuracy_score > 0:
        llm_prompt = (
            "Evaluate if the provided JSON correctly links the individuals (Bob Jones, Charlie Brown, Dave White) "
            "with their strictly relevant PII (e.g., SSN '999-00-1234', CC '4444-5555-6666-7777', Email 'dave.w@unsecured.net'). "
            "Does it structurally contain these PII details explicitly mapped to the respective names? Answer YES or NO."
        )
        has_pii = llm_judge_content(llm_prompt, json_data_str)
        if has_pii:
            score_details.append({"item": "PII数据关联准确性(LLM评估)", "score": 20, "max_score": 20, "passed": True, "reason": "JSON中正确且清晰地包含了详细的PII数据映射"})
            total_score += 20
        else:
            score_details.append({"item": "PII数据关联准确性(LLM评估)", "score": 0, "max_score": 20, "passed": False, "reason": "JSON未包含具体的PII数据，或者映射不清晰"})
    else:
        score_details.append({"item": "PII数据关联准确性(LLM评估)", "score": 0, "max_score": 20, "passed": False, "reason": "前置验证失败或缺失JSON"})

    # Write output
    output_data = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    ws = sys.argv[1] if len(sys.argv) > 1 else "."
    check_workplace(ws)
