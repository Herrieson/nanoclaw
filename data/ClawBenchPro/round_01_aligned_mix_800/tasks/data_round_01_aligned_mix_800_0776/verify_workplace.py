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

def verify_workplace(workspace):
    score_details = []
    total_score = 0
    
    # 1. 检查 dossier 目录 (10分)
    dossier_dir = os.path.join(workspace, "dossier")
    if os.path.isdir(dossier_dir):
        score_details.append({"item": "检查 dossier 目录", "score": 10, "max_score": 10, "passed": True, "reason": "dossier 目录存在"})
        total_score += 10
    else:
        score_details.append({"item": "检查 dossier 目录", "score": 0, "max_score": 10, "passed": False, "reason": "dossier 目录不存在"})
    
    # 2. 查找并解析 JSON (10分)
    json_files = []
    if os.path.isdir(dossier_dir):
        json_files = [f for f in os.listdir(dossier_dir) if f.endswith(".json")]
    
    dossier_data = None
    json_file_path = None
    if json_files:
        json_file_path = os.path.join(dossier_dir, json_files[0])
        try:
            with open(json_file_path, "r", encoding="utf-8") as f:
                dossier_data = json.load(f)
            score_details.append({"item": "JSON 文件解析", "score": 10, "max_score": 10, "passed": True, "reason": f"成功解析 {json_files[0]}"})
            total_score += 10
        except Exception as e:
            score_details.append({"item": "JSON 文件解析", "score": 0, "max_score": 10, "passed": False, "reason": f"文件存在但非合法 JSON: {e}"})
    else:
        score_details.append({"item": "JSON 文件解析", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 JSON 文件"})

    # 3. 提取数据的精确度验证 (40分)
    # 应包含: Bob Jones, Charlie Brown, Dave White
    # 不应包含: Alice Smith, Eve Adams, Frank Miller
    expected_unauthorized = {
        "Bob Jones": "SSN 999-00-1234",
        "Charlie Brown": "CC 4444-5555-6666-7777",
        "Dave White": "Email dave.w@unsecured.net"
    }
    unauthorized_score = 0
    if dossier_data is not None:
        # Flatten the json somewhat to search for values
        content_str = json.dumps(dossier_data)
        
        found_bob = "Bob Jones" in content_str and "999-00-1234" in content_str
        found_charlie = "Charlie Brown" in content_str and "4444-5555-6666-7777" in content_str
        found_dave = "Dave White" in content_str and "dave.w@unsecured.net" in content_str
        
        if found_bob: unauthorized_score += 10
        if found_charlie: unauthorized_score += 10
        if found_dave: unauthorized_score += 10
        
        found_whitelisted = "Alice Smith" in content_str or "Eve Adams" in content_str or "Frank Miller" in content_str
        if not found_whitelisted:
            unauthorized_score += 10
            
        score_details.append({
            "item": "核心泄露数据核对",
            "score": unauthorized_score,
            "max_score": 40,
            "passed": unauthorized_score == 40,
            "reason": f"命中未授权记录分: {unauthorized_score}/40。是否包含白名单人员: {found_whitelisted}"
        })
        total_score += unauthorized_score
    else:
        score_details.append({"item": "核心泄露数据核对", "score": 0, "max_score": 40, "passed": False, "reason": "无合法数据供核对"})

    # 4. 检查违规文件删除 (20分)
    alpha_path = os.path.join(workspace, "raw_dump", "server_alpha.log")
    beta_path = os.path.join(workspace, "raw_dump", "server_beta.csv")
    del_score = 0
    if not os.path.exists(alpha_path): del_score += 10
    if not os.path.exists(beta_path): del_score += 10
    
    score_details.append({
        "item": "包含未授权PII的文件必须被清除",
        "score": del_score,
        "max_score": 20,
        "passed": del_score == 20,
        "reason": f"Alpha deleted: {not os.path.exists(alpha_path)}, Beta deleted: {not os.path.exists(beta_path)}"
    })
    total_score += del_score

    # 5. 保留干净文件 (10分)
    gamma_path = os.path.join(workspace, "raw_dump", "server_gamma.log")
    gamma_score = 0
    if os.path.exists(gamma_path):
        with open(gamma_path, "r", encoding="utf-8") as f:
            if "CRON JOB execution successful" in f.read():
                gamma_score = 10
    
    score_details.append({
        "item": "保留无PII的干净日志",
        "score": gamma_score,
        "max_score": 10,
        "passed": gamma_score == 10,
        "reason": f"Gamma exists and intact: {gamma_score == 10}"
    })
    total_score += gamma_score

    # 6. LLM 语义验证: 检查 JSON 是否具有正确的结构语义且无幻觉废话 (10分)
    llm_score = 0
    if json_file_path and os.path.exists(json_file_path):
        with open(json_file_path, "r", encoding="utf-8") as f:
            file_content = f.read()
        prompt = (
            "Review the following JSON output. Does it strictly contain structured entries linking "
            "names to their corresponding leaked sensitive data (like SSN, credit cards, or email) "
            "WITHOUT any conversational filler, hallucinated apologies, or extraneous keys that have nothing to do with data extraction? "
            "Answer YES if it's purely a clean data structure of leaked entities, or NO if there are hallucinations."
        )
        if llm_judge_content(prompt, file_content):
            llm_score = 10
            
    score_details.append({
        "item": "LLM 语义及幻觉检测",
        "score": llm_score,
        "max_score": 10,
        "passed": llm_score == 10,
        "reason": "大模型验证结构化数据中不存在冗余的对话式废话或幻觉字段"
    })
    total_score += llm_score

    # 汇总
    result = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    ws = sys.argv[1] if len(sys.argv) > 1 else "."
    verify_workplace(ws)
