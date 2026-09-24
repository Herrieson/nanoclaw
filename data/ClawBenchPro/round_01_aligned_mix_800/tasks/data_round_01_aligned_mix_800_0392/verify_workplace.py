import os
import sys
import json
import httpx
from openai import OpenAI

# 基础环境配置
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

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ready_for_mix_path = os.path.join(workspace, "ready_for_mix")
    scores = []
    
    # 1. 目录与基础文件存在性 (10分)
    exists = os.path.exists(ready_for_mix_path) and os.path.isdir(ready_for_mix_path)
    scores.append({"item": "目录 ready_for_mix 存在", "score": 10 if exists else 0, "max_score": 10, "passed": exists, "reason": ""})

    # 2. 关键音频文件筛选准确性 (30分)
    # 应包含: Vocals_Echo_Final.wav, Drums_Echo_Raw.wav, Bass_Neon_Main.wav, Synth_Neon_Arp.wav
    # 应剔除: Midnight (Cancelled), Lost (Scrapped), Silence (0 duration)
    expected_files = ["Vocals_Echo_Final.wav", "Drums_Echo_Raw.wav", "Bass_Neon_Main.wav", "Synth_Neon_Arp.wav"]
    forbidden_files = ["Guitar_Midnight_Test.wav", "Piano_Lost_Buzz.wav", "Silence_Gap.wav"]
    
    if exists:
        found_files = os.listdir(ready_for_mix_path)
        correct_count = sum(1 for f in expected_files if f in found_files)
        penalty_count = sum(1 for f in forbidden_files if f in found_files)
        
        passed_files = correct_count == 4 and penalty_count == 0
        file_score = max(0, (correct_count * 7.5) - (penalty_count * 10))
        scores.append({
            "item": "音频文件筛选准确性 (需排除无效/取消音轨)",
            "score": file_score,
            "max_score": 30,
            "passed": passed_files,
            "reason": f"找到了 {correct_count}/4 个正确文件，包含了 {penalty_count} 个错误文件"
        })
    else:
        scores.append({"item": "音频文件筛选准确性", "score": 0, "max_score": 30, "passed": False, "reason": "目录不存在"})

    # 3. JSON 格式与 Schema 符合性 (30分)
    # 根据 Knowledge Base 标准: "session_total_duration" (float) 和 "approved_assets" (list)
    json_path = None
    if exists:
        for f in os.listdir(ready_for_mix_path):
            if f.endswith(".json"):
                json_path = os.path.join(ready_for_mix_path, f)
                break
    
    if json_path:
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            # 检查键名 (来源于 Knowledge Base 搜索结果)
            has_duration_key = "session_total_duration" in data
            has_assets_key = "approved_assets" in data
            
            # 检查数值准确性 (来源于 Cost Calculator: 4.75 + 6.0 = 10.75)
            duration_val = data.get("session_total_duration", 0)
            is_duration_correct = abs(float(duration_val) - 10.75) < 0.01
            
            # 综合评分
            schema_score = 0
            if has_duration_key: schema_score += 10
            if has_assets_key: schema_score += 10
            if is_duration_correct: schema_score += 10
            
            scores.append({
                "item": "JSON 格式、Schema 键名及计费时长准确性",
                "score": schema_score,
                "max_score": 30,
                "passed": schema_score == 30,
                "reason": f"键名正确性: {has_duration_key}/{has_assets_key}, 时长: {duration_val} (期望 10.75)"
            })
        except Exception as e:
            scores.append({"item": "JSON 格式", "score": 0, "max_score": 30, "passed": False, "reason": f"JSON 解析失败: {e}"})
    else:
        scores.append({"item": "JSON 格式", "score": 0, "max_score": 30, "passed": False, "reason": "未找到 JSON 结果文件"})

    # 4. 语义验证：是否有对录音棚经理的汇总说明 (30分)
    # 这里通常检查是否存在一个 README 或 Summary 文件，并用 LLM 检查语气和内容完整性
    summary_content = ""
    summary_file_found = False
    for root, dirs, files in os.walk(workspace):
        for f in files:
            if "summary" in f.lower() or "readme" in f.lower() or f.endswith(".txt"):
                if f != "requirements.txt":
                    with open(os.path.join(root, f), 'r') as sf:
                        summary_content = sf.read()
                        summary_file_found = True
                        break
    
    if summary_file_found:
        prompt = "Does this summary mention that the sessions for 'Midnight' and 'Lost' were excluded and provide a professional tone for the label?"
        is_professional = llm_judge_content(prompt, summary_content)
        scores.append({
            "item": "总结文档语义检查 (专业度与内容完整性)",
            "score": 30 if is_professional else 10,
            "max_score": 30,
            "passed": is_professional,
            "reason": "LLM 判定总结内容是否包含必要排除说明并语气专业"
        })
    else:
        scores.append({"item": "总结文档", "score": 0, "max_score": 30, "passed": False, "reason": "未找到总结说明文件"})

    # 计算总分
    total_score = sum(s["score"] for s in scores)
    result = {
        "total_score": int(total_score),
        "details": scores
    }
    
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
