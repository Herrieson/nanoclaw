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

def verify_workplace():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ready_dir = os.path.join(workspace, "ready_for_mix")
    
    score_details = []
    total_score = 0
    
    # 1. 检查目录结构 (10分)
    if os.path.isdir(ready_dir):
        score_details.append({"item": "检查目标目录 ready_for_mix 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "成功找到 ready_for_mix 目录。"})
        total_score += 10
    else:
        score_details.append({"item": "检查目标目录 ready_for_mix 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 ready_for_mix 目录。"})
        # 无法继续
        with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # 2. 检查有效音频文件的复制 (30分)
    # 根据 log，只有 Echo 和 Neon 是成功会话。
    expected_stems = {"Vocals_Echo.wav", "Drums_Echo.wav", "Bass_Neon.wav", "Synth_Neon.wav"}
    invalid_stems = {"Guitar_Midnight.wav", "Piano_Lost.wav", "Random_Noise_Test.wav"}
    
    files_in_ready = set(os.listdir(ready_dir))
    wav_files_in_ready = {f for f in files_in_ready if f.endswith(".wav")}
    
    missing_stems = expected_stems - wav_files_in_ready
    extra_stems = wav_files_in_ready.intersection(invalid_stems)
    
    if not missing_stems and not extra_stems:
        score_details.append({"item": "检查是否只拷贝了有效的Stems", "score": 30, "max_score": 30, "passed": True, "reason": "精确拷贝了所有有效stems且没有无效文件。"})
        total_score += 30
    else:
        penalty = 0
        reason_parts = []
        if missing_stems:
            penalty += len(missing_stems) * 10
            reason_parts.append(f"遗漏了文件: {missing_stems}")
        if extra_stems:
            penalty += len(extra_stems) * 10
            reason_parts.append(f"错误包含了无效文件: {extra_stems}")
            
        awarded = max(0, 30 - penalty)
        score_details.append({"item": "检查是否只拷贝了有效的Stems", "score": awarded, "max_score": 30, "passed": awarded > 0, "reason": "; ".join(reason_parts)})
        total_score += awarded

    # 3. 检查 JSON 文件存在及合法性 (10分)
    json_files = [f for f in files_in_ready if f.endswith(".json")]
    json_data = None
    if json_files:
        json_file_path = os.path.join(ready_dir, json_files[0])
        try:
            with open(json_file_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)
            score_details.append({"item": "检查 JSON 文件是否存在且可解析", "score": 10, "max_score": 10, "passed": True, "reason": f"成功解析 {json_files[0]}。"})
            total_score += 10
        except Exception as e:
            score_details.append({"item": "检查 JSON 文件是否存在且可解析", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON解析失败: {e}"})
    else:
        score_details.append({"item": "检查 JSON 文件是否存在且可解析", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 JSON 文件。"})

    # 4 & 5 需要基于 JSON 解析结果
    if json_data and isinstance(json_data, dict):
        # 提取所有值寻找时长 10.5
        found_hours = False
        for k, v in json_data.items():
            if isinstance(v, (int, float)) and v == 10.5:
                found_hours = True
            if isinstance(v, str) and "10.5" in v:
                found_hours = True
                
        if found_hours:
            score_details.append({"item": "检查 JSON 中是否包含正确计算的总录音室时长 (10.5小时)", "score": 20, "max_score": 20, "passed": True, "reason": "成功在 JSON 中匹配到计算正确的总时长 10.5。"})
            total_score += 20
        else:
            score_details.append({"item": "检查 JSON 中是否包含正确计算的总录音室时长 (10.5小时)", "score": 0, "max_score": 20, "passed": False, "reason": "JSON 中未找到正确的总录音室时长(10.5)。"})

        # 提取所有列表以寻找有效的 stems 文件名
        found_files = False
        for k, v in json_data.items():
            if isinstance(v, list):
                # 检查此列表中是否完整包含 expected_stems
                # 使用 set 判断以忽略顺序
                list_str = [str(x) for x in v]
                if expected_stems.issubset(set(list_str)):
                    found_files = True
                    # 检查是否掺杂了多余的文件名
                    if len(set(list_str).intersection(invalid_stems)) > 0:
                        found_files = False # 但包含了无效文件，不予给分
                        
        if found_files:
            score_details.append({"item": "检查 JSON 中是否包含纯净的有效文件列表", "score": 30, "max_score": 30, "passed": True, "reason": "成功找到完整的有效文件列表，且未包含无效数据。"})
            total_score += 30
        else:
            score_details.append({"item": "检查 JSON 中是否包含纯净的有效文件列表", "score": 0, "max_score": 30, "passed": False, "reason": "未在 JSON 数组中找到完整且纯净的有效文件名列表。"})
    else:
        score_details.append({"item": "检查 JSON 中是否包含正确计算的总录音室时长", "score": 0, "max_score": 20, "passed": False, "reason": "JSON不存在或并非字典格式，无法检查。"})
        score_details.append({"item": "检查 JSON 中是否包含纯净的有效文件列表", "score": 0, "max_score": 30, "passed": False, "reason": "JSON不存在或并非字典格式，无法检查。"})

    # 输出结果
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({
            "total_score": total_score,
            "details": score_details
        }, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify_workplace()
