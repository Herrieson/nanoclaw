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

def verify(workspace):
    score = 0
    details = []
    
    target_path = os.path.join(workspace, "fix_list", "target.json")
    
    # 1. 结构验证：检查结果文件是否存在 (20分)
    if os.path.exists(target_path):
        score += 20
        details.append({"item": "检查目标结果文件是否存在", "score": 20, "max_score": 20, "passed": True, "reason": "文件 fix_list/target.json 存在"})
    else:
        details.append({"item": "检查目标结果文件是否存在", "score": 0, "max_score": 20, "passed": False, "reason": "文件 fix_list/target.json 不存在"})
        return dump_result(score, details)

    # 2. 结构验证：JSON 格式及 Schema 验证 (20分)
    try:
        with open(target_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        if "culprit_asset" in data:
            # 防止 Agent 幻觉捏造冗余的说明性字段
            if len(data.keys()) > 3:
                score += 10
                details.append({"item": "JSON格式与Schema合法性", "score": 10, "max_score": 20, "passed": False, "reason": "文件是合法的JSON且包含 culprit_asset，但检测到Agent捏造了冗余和无关的键值对"})
            else:
                score += 20
                details.append({"item": "JSON格式与Schema合法性", "score": 20, "max_score": 20, "passed": True, "reason": "JSON格式合法，成功且精准提取 culprit_asset 键"})
            
            culprit_asset = str(data["culprit_asset"]).strip()
        else:
            details.append({"item": "JSON格式与Schema合法性", "score": 0, "max_score": 20, "passed": False, "reason": "JSON中未找到强制要求的 culprit_asset 键"})
            return dump_result(score, details)
    except Exception as e:
        details.append({"item": "JSON格式与Schema合法性", "score": 0, "max_score": 20, "passed": False, "reason": f"无法解析为合法的JSON文件: {e}"})
        return dump_result(score, details)
        
    # 3. 陷阱检测：剔除诱饵数据 (20分)
    decoy_asset = "assets/models/environment/super_mountain_background_static.mesh"
    if culprit_asset == decoy_asset:
        details.append({"item": "剔除诱饵与错误数据", "score": 0, "max_score": 20, "passed": False, "reason": "严重扣分项：检测到输出结果为静态山体网格(超高顶点数诱饵)，Agent未结合死锁帧条件，直接全图搜索了最大Vtx"})
    elif culprit_asset == "":
        details.append({"item": "剔除诱饵与错误数据", "score": 0, "max_score": 20, "passed": False, "reason": "提取的罪魁祸首资产路径为空字符串"})
    else:
        score += 20
        details.append({"item": "剔除诱饵与错误数据", "score": 20, "max_score": 20, "passed": True, "reason": "未踩中诱饵实体陷阱，成功绕开全局最大值的逻辑干扰"})
        
    # 4. 精准比对：关键解算结果匹配 (40分)
    correct_asset = "assets/models/cinematics/boss_titan_shatter_piece_HD_LOD0.mesh"
    if culprit_asset == correct_asset:
        score += 40
        details.append({"item": "关键解算结果精准匹配", "score": 40, "max_score": 40, "passed": True, "reason": "完美匹配！精准锁定了在异常帧死锁状态下，同时满足 AWAKE 状态且参与解算中 Vtx 最高实体的 AssetPath"})
    else:
        details.append({"item": "关键解算结果精准匹配", "score": 0, "max_score": 40, "passed": False, "reason": f"结果验证失败，解析出的错误目标是: {culprit_asset}"})
        
    return dump_result(score, details)

def dump_result(score, details):
    res = {"total_score": score, "details": details}
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(res, f, indent=4, ensure_ascii=False)
    return res

if __name__ == "__main__":
    workspace_path = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace_path)
