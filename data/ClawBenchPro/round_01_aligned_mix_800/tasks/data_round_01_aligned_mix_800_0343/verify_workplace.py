import os
import sys
import json
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
    # 此函数为检测非结构化文本的统一接口
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
    results_dir = os.path.join(workspace, "results")
    output_file = os.path.join(results_dir, "optimal_routes.json")

    total_score = 0
    details = []

    # 1. 验证目录和文件是否存在 (10 分)
    if not os.path.exists(results_dir):
        details.append({"item": "检查 results 目录", "score": 0, "max_score": 5, "passed": False, "reason": "未找到 results 目录"})
        details.append({"item": "检查 optimal_routes.json 文件", "score": 0, "max_score": 5, "passed": False, "reason": "未找到 json 文件"})
    else:
        details.append({"item": "检查 results 目录", "score": 5, "max_score": 5, "passed": True, "reason": "results 目录存在"})
        if not os.path.isfile(output_file):
            details.append({"item": "检查 optimal_routes.json 文件", "score": 0, "max_score": 5, "passed": False, "reason": "未找到 optimal_routes.json 文件"})
        else:
            details.append({"item": "检查 optimal_routes.json 文件", "score": 5, "max_score": 5, "passed": True, "reason": "optimal_routes.json 文件存在"})

    # 如果文件不存在，提前退出
    if not os.path.isfile(output_file):
        with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)
        return

    # 2. 验证 JSON 格式 (10 分)
    try:
        with open(output_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        details.append({"item": "JSON 格式合法性解析", "score": 10, "max_score": 10, "passed": True, "reason": "能够成功解析为结构化 JSON 数据"})
        
        if not isinstance(data, dict):
            raise ValueError("Root node is not a dictionary.")
    except Exception as e:
        details.append({"item": "JSON 格式合法性解析", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败或根节点不是对象: {e}"})
        with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
            json.dump({"total_score": 10, "details": details}, f, indent=2, ensure_ascii=False) # Only got dir points
        return

    # 3. 严格幻觉与逻辑筛查 (20 分)
    valid_keys = {"trail_alpha", "trail_delta"}
    agent_keys = set(data.keys())
    invalid_keys = agent_keys - valid_keys
    
    if len(invalid_keys) > 0:
        details.append({
            "item": "剔除错误数据与幻觉检查", 
            "score": 0, 
            "max_score": 20, 
            "passed": False, 
            "reason": f"存在不满足约束或捏造的路线记录: {list(invalid_keys)}。严重违背计算规则或涉嫌幻觉。"
        })
    elif len(agent_keys) == 0:
        details.append({
            "item": "剔除错误数据与幻觉检查", 
            "score": 0, 
            "max_score": 20, 
            "passed": False, 
            "reason": "提交的 JSON 为空，未找到任何路线数据。"
        })
    else:
        details.append({
            "item": "剔除错误数据与幻觉检查", 
            "score": 20, 
            "max_score": 20, 
            "passed": True, 
            "reason": "仅包含符合数学约束的正确拓扑路线，无幻觉字段。"
        })

    # 4. 验证 trail_alpha 的精准数学计算结果 (30 分)
    alpha_score = 0
    alpha_passed = False
    alpha_reason = []
    if "trail_alpha" in data:
        alpha_data = data["trail_alpha"]
        if isinstance(alpha_data, dict):
            gain = alpha_data.get("total_gain")
            steepness = alpha_data.get("max_steepness")
            
            # total_gain 应该等于 200 (允许浮点误差 0.1)
            if gain is not None and abs(float(gain) - 200.0) <= 0.1:
                alpha_score += 15
                alpha_reason.append("total_gain=200 正确")
            else:
                alpha_reason.append(f"total_gain 错误(期望200, 实际{gain})")
                
            # max_steepness 应该等于 90
            if steepness is not None and abs(float(steepness) - 90.0) <= 0.1:
                alpha_score += 15
                alpha_reason.append("max_steepness=90 正确")
            else:
                alpha_reason.append(f"max_steepness 错误(期望90, 实际{steepness})")
                
            if alpha_score == 30:
                alpha_passed = True
        else:
            alpha_reason.append("trail_alpha 的值域不是结构化对象")
    else:
        alpha_reason.append("缺失 trail_alpha 记录")
        
    details.append({
        "item": "精准验证 trail_alpha 的指标",
        "score": alpha_score,
        "max_score": 30,
        "passed": alpha_passed,
        "reason": "; ".join(alpha_reason)
    })

    # 5. 验证 trail_delta 的精准数学计算结果 (30 分)
    delta_score = 0
    delta_passed = False
    delta_reason = []
    if "trail_delta" in data:
        delta_data = data["trail_delta"]
        if isinstance(delta_data, dict):
            gain = delta_data.get("total_gain")
            steepness = delta_data.get("max_steepness")
            
            # total_gain 应该等于 292.5
            if gain is not None and abs(float(gain) - 292.5) <= 0.1:
                delta_score += 15
                delta_reason.append("total_gain=292.5 正确")
            else:
                delta_reason.append(f"total_gain 错误(期望292.5, 实际{gain})")
                
            # max_steepness 应该等于 95
            if steepness is not None and abs(float(steepness) - 95.0) <= 0.1:
                delta_score += 15
                delta_reason.append("max_steepness=95 正确")
            else:
                delta_reason.append(f"max_steepness 错误(期望95, 实际{steepness})")
                
            if delta_score == 30:
                delta_passed = True
        else:
            delta_reason.append("trail_delta 的值域不是结构化对象")
    else:
        delta_reason.append("缺失 trail_delta 记录")
        
    details.append({
        "item": "精准验证 trail_delta 的指标",
        "score": delta_score,
        "max_score": 30,
        "passed": delta_passed,
        "reason": "; ".join(delta_reason)
    })

    # 计算总分
    total_score = sum(d["score"] for d in details)
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
