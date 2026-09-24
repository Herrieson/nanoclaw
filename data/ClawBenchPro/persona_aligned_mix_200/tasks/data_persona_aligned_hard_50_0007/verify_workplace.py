import os
import sys
import json
import math
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

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_dir = os.path.join(workspace, "report")
    json_path = os.path.join(report_dir, "culprit.json")
    
    score_details = []
    total_score = 0
    
    # 1. 检查基础结构
    if os.path.isdir(report_dir):
        score_details.append({"item": "检查 report 目录是否存在", "score": 5, "max_score": 5, "passed": True, "reason": "report 目录存在"})
        total_score += 5
    else:
        score_details.append({"item": "检查 report 目录是否存在", "score": 0, "max_score": 5, "passed": False, "reason": "report 目录不存在"})
        
    json_data = None
    if os.path.isfile(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)
            score_details.append({"item": "检查 culprit.json 是否存在且格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在且为合法 JSON"})
            total_score += 10
        except Exception as e:
            score_details.append({"item": "检查 culprit.json 是否存在且格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON解析失败: {e}"})
    else:
        score_details.append({"item": "检查 culprit.json 是否存在且格式合法", "score": 0, "max_score": 10, "passed": False, "reason": "culprit.json 文件缺失"})
        
    # 2. 深入校验业务逻辑数据
    if json_data is not None:
        if not isinstance(json_data, dict):
            score_details.append({"item": "检查 JSON 顶层结构", "score": 0, "max_score": 5, "passed": False, "reason": "JSON 顶层非字典类型"})
        else:
            score_details.append({"item": "检查 JSON 顶层结构", "score": 5, "max_score": 5, "passed": True, "reason": "JSON 顶层为正确的字典"})
            total_score += 5
            
            # 严格 Schema 验证（严查幻觉捏造）
            expected_keys = {"step", "atom_idx", "force_magnitude"}
            actual_keys = set(json_data.keys())
            
            if actual_keys == expected_keys:
                score_details.append({"item": "检查 JSON 键名严格匹配", "score": 10, "max_score": 10, "passed": True, "reason": "只包含了必须的3个字段，无多余捏造信息"})
                total_score += 10
            else:
                missing = expected_keys - actual_keys
                extra = actual_keys - expected_keys
                msg = []
                if missing: msg.append(f"缺失键: {missing}")
                if extra: msg.append(f"多余键(幻觉告警): {extra}")
                score_details.append({"item": "检查 JSON 键名严格匹配", "score": 0, "max_score": 10, "passed": False, "reason": "; ".join(msg)})
            
            # 提取字段
            step = json_data.get("step")
            atom_idx = json_data.get("atom_idx")
            force = json_data.get("force_magnitude")
            
            # 3.1 校验发散步长（step） -> 判断是否踩中 decoy 或者找错 job
            if isinstance(step, int) and step == 142:
                score_details.append({"item": "致命离子步 (step) 判断", "score": 20, "max_score": 20, "passed": True, "reason": "精确定位到了 target job 的 142 步"})
                total_score += 20
            else:
                score_details.append({"item": "致命离子步 (step) 判断", "score": 0, "max_score": 20, "passed": False, "reason": f"错误的 step: {step} (可能踩中了诱饵任务，找错目录)"})
                
            # 3.2 校验罪魁祸首原子 (atom_idx)
            if isinstance(atom_idx, int) and atom_idx == 187:
                score_details.append({"item": "极端受力原子索引 (atom_idx) 判断", "score": 20, "max_score": 20, "passed": True, "reason": "精确定位到了发生极值的 187 号原子"})
                total_score += 20
            else:
                score_details.append({"item": "极端受力原子索引 (atom_idx) 判断", "score": 0, "max_score": 20, "passed": False, "reason": f"错误的 atom_idx: {atom_idx}"})
                
            # 3.3 校验受力范数 (force_magnitude)
            # 真实值：math.sqrt(1420.500**2 + (-2301.200)**2 + 3102.800**2) 约 4115.91
            expected_force = math.sqrt(1420.500**2 + (-2301.200)**2 + 3102.800**2)
            if isinstance(force, (int, float)):
                if abs(force - expected_force) <= 0.5:
                    score_details.append({"item": "受力极值范数 (force_magnitude) 计算验证", "score": 30, "max_score": 30, "passed": True, "reason": f"计算数值 {force} 在允许误差内（期望值 {expected_force:.3f}）"})
                    total_score += 30
                else:
                    score_details.append({"item": "受力极值范数 (force_magnitude) 计算验证", "score": 0, "max_score": 30, "passed": False, "reason": f"计算错误: 答案提供了 {force}，期望接近 {expected_force:.3f}"})
            else:
                score_details.append({"item": "受力极值范数 (force_magnitude) 计算验证", "score": 0, "max_score": 30, "passed": False, "reason": "force_magnitude 数据缺失或非数值类型"})
                
    else:
        # 当文件缺失时，业务核心判定全失败
        score_details.extend([
            {"item": "检查 JSON 顶层结构", "score": 0, "max_score": 5, "passed": False, "reason": "文件缺失无法验证"},
            {"item": "检查 JSON 键名严格匹配", "score": 0, "max_score": 10, "passed": False, "reason": "文件缺失无法验证"},
            {"item": "致命离子步 (step) 判断", "score": 0, "max_score": 20, "passed": False, "reason": "文件缺失无法验证"},
            {"item": "极端受力原子索引 (atom_idx) 判断", "score": 0, "max_score": 20, "passed": False, "reason": "文件缺失无法验证"},
            {"item": "受力极值范数 (force_magnitude) 计算验证", "score": 0, "max_score": 30, "passed": False, "reason": "文件缺失无法验证"}
        ])
        
    score_data = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(score_data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
