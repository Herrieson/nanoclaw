import os
import sys
import json
import math
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

def verify(workspace):
    score_details = []
    total_score = 0
    target_file = os.path.join(workspace, "output", "critical_state.json")

    # 1. 检查文件是否存在 (20分)
    if not os.path.exists(target_file):
        score_details.append({
            "item": "检查结果文件是否存在",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"未找到文件 {target_file}"
        })
        write_score(0, score_details, workspace)
        return
    else:
        score_details.append({
            "item": "检查结果文件是否存在",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "文件 output/critical_state.json 存在"
        })
        total_score += 20

    # 2. 检查 JSON 格式合法性 (15分)
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        score_details.append({
            "item": "检查 JSON 解析",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": "文件为合法 JSON"
        })
        total_score += 15
    except Exception as e:
        score_details.append({
            "item": "检查 JSON 解析",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"解析 JSON 失败: {e}"
        })
        write_score(total_score, score_details, workspace)
        return

    # 3. 检查 JSON 键名准确性与无幻觉字段 (15分)
    expected_keys = {"latest_quaternion", "max_temperature"}
    actual_keys = set(data.keys())
    if actual_keys == expected_keys:
        score_details.append({
            "item": "检查 JSON 字段严格匹配",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": "字段名称完全匹配，无多余捏造字段"
        })
        total_score += 15
    else:
        missing = expected_keys - actual_keys
        extra = actual_keys - expected_keys
        reason_parts = []
        if missing: reason_parts.append(f"缺失: {missing}")
        if extra: reason_parts.append(f"多余: {extra}")
        score_details.append({
            "item": "检查 JSON 字段严格匹配",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": "字段不完全匹配。 " + " | ".join(reason_parts)
        })

    # 4. 检查 max_temperature 计算结果 (25分)
    temp = data.get("max_temperature", None)
    if temp is not None:
        try:
            temp_val = float(temp)
            # 正确值为 94.75。容忍度很低
            if math.isclose(temp_val, 94.75, abs_tol=0.01):
                score_details.append({
                    "item": "验证最大异常温度峰值",
                    "score": 25,
                    "max_score": 25,
                    "passed": True,
                    "reason": "最高异常温度峰值精确等于 94.75"
                })
                total_score += 25
            else:
                score_details.append({
                    "item": "验证最大异常温度峰值",
                    "score": 0,
                    "max_score": 25,
                    "passed": False,
                    "reason": f"温度值错误，期望 94.75，实际为 {temp_val}"
                })
        except ValueError:
            score_details.append({
                "item": "验证最大异常温度峰值",
                "score": 0,
                "max_score": 25,
                "passed": False,
                "reason": "max_temperature 并非有效数值类型"
            })
    else:
        score_details.append({
            "item": "验证最大异常温度峰值",
            "score": 0,
            "max_score": 25,
            "passed": False,
            "reason": "未找到 max_temperature 字段"
        })

    # 5. 检查 latest_quaternion 提取与计算结果 (25分)
    quat = data.get("latest_quaternion", None)
    if quat is not None:
        if isinstance(quat, list) and len(quat) == 4:
            expected_quat = [0.4999, 0.5001, -0.4999, -0.5001]
            try:
                match_all = True
                for val, exp in zip(quat, expected_quat):
                    if not math.isclose(float(val), exp, abs_tol=0.0002):
                        match_all = False
                        break
                if match_all:
                    score_details.append({
                        "item": "验证最新星象仪四元数",
                        "score": 25,
                        "max_score": 25,
                        "passed": True,
                        "reason": f"成功提取有效时间最新的一帧四元数并保留正确小数位"
                    })
                    total_score += 25
                else:
                    score_details.append({
                        "item": "验证最新星象仪四元数",
                        "score": 0,
                        "max_score": 25,
                        "passed": False,
                        "reason": f"四元数值不匹配，可能找错了时间帧、提取到了被破坏的帧头数据或解析小/大端序出错。实际值：{quat}"
                    })
            except ValueError:
                score_details.append({
                    "item": "验证最新星象仪四元数",
                    "score": 0,
                    "max_score": 25,
                    "passed": False,
                    "reason": "数组内含有非数值数据"
                })
        else:
            score_details.append({
                "item": "验证最新星象仪四元数",
                "score": 0,
                "max_score": 25,
                "passed": False,
                "reason": "latest_quaternion 格式错误，必须为包含4个数值的数组"
            })
    else:
        score_details.append({
            "item": "验证最新星象仪四元数",
            "score": 0,
            "max_score": 25,
            "passed": False,
            "reason": "未找到 latest_quaternion 字段"
        })

    write_score(total_score, score_details, workspace)

def write_score(total_score, details, workspace):
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    work_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(work_dir)
