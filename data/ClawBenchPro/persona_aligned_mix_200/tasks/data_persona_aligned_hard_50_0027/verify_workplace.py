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
    """用于检测非结构化文本的统一接口"""
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
    details = []
    total_score = 0
    
    target_path = os.path.join(workspace, "recovery", "target.json")
    
    # 1. 验证结果文件是否存在 (10分)
    if os.path.isfile(target_path):
        details.append({"item": "检查目标文件 target.json 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件已存在于 recovery 目录中"})
        total_score += 10
    else:
        details.append({"item": "检查目标文件 target.json 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 target.json 文件"})
        
    data = None
    if os.path.isfile(target_path):
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            details.append({"item": "检查 JSON 格式合法性", "score": 0, "max_score": 15, "passed": False, "reason": f"文件不是合法的 JSON 格式，解析失败: {e}"})
            
    # 2. 验证 JSON 架构完整性及无多余捏造 (15分)
    if data is not None:
        if not isinstance(data, dict):
            details.append({"item": "检查 JSON 结构体", "score": 0, "max_score": 15, "passed": False, "reason": "JSON 的根节点必须是 Object/字典"})
        else:
            keys = set(data.keys())
            expected_keys = {"rank_id", "coordinates"}
            if keys == expected_keys:
                details.append({"item": "检查 JSON 字段完整且无多余", "score": 15, "max_score": 15, "passed": True, "reason": "包含且仅包含题目要求的 rank_id 和 coordinates"})
                total_score += 15
            elif expected_keys.issubset(keys):
                details.append({"item": "检查 JSON 字段完整且无多余", "score": 5, "max_score": 15, "passed": False, "reason": "包含所需字段，但存在题目未要求的捏造冗余字段，严查作弊或幻觉，轻度扣分"})
                total_score += 5
            else:
                details.append({"item": "检查 JSON 字段完整且无多余", "score": 0, "max_score": 15, "passed": False, "reason": f"缺失核心键值，当前解析到的键: {list(keys)}"})

        # 3. 验证 Rank ID (30分)
        if "rank_id" in data:
            rank = data["rank_id"]
            if isinstance(rank, int) and rank == 6682:
                details.append({"item": "核心计算: Rank ID 提取准确性", "score": 30, "max_score": 30, "passed": True, "reason": "精准锁定导致崩溃的 Rank ID (6682)，且数据类型为正确的整数"})
                total_score += 30
            elif str(rank) == "6682":
                details.append({"item": "核心计算: Rank ID 提取准确性", "score": 25, "max_score": 30, "passed": False, "reason": "找到正确的 Rank ID (6682)，但数据类型写成了字符串，未能严格遵循整数要求"})
                total_score += 25
            else:
                details.append({"item": "核心计算: Rank ID 提取准确性", "score": 0, "max_score": 30, "passed": False, "reason": f"提取的 Rank ID 错误。检测到: {rank}"})
        else:
            details.append({"item": "核心计算: Rank ID 提取准确性", "score": 0, "max_score": 30, "passed": False, "reason": "结果中缺失 rank_id 字段"})
            
        # 4. 验证 Coordinates (35分)
        if "coordinates" in data:
            coords = data["coordinates"]
            expected_coords = [108, 45, 120, 880]
            if isinstance(coords, list) and len(coords) == 4:
                try:
                    int_coords = [int(x) for x in coords]
                    if int_coords == expected_coords:
                        details.append({"item": "核心计算: 溢出点四维坐标解析", "score": 35, "max_score": 35, "passed": True, "reason": "准确解码并提取出了四维坐标，且严格符合 time, lev, lat, lon 的指定顺序"})
                        total_score += 35
                    elif set(int_coords) == set(expected_coords):
                        details.append({"item": "核心计算: 溢出点四维坐标解析", "score": 15, "max_score": 35, "passed": False, "reason": "提取的坐标数值本身是对的，但是未按题目要求的 time, lev, lat, lon 顺序排列"})
                        total_score += 15
                    else:
                        details.append({"item": "核心计算: 溢出点四维坐标解析", "score": 0, "max_score": 35, "passed": False, "reason": f"提取的坐标值错误。预期: {expected_coords}, 实际: {int_coords}"})
                except ValueError:
                    details.append({"item": "核心计算: 溢出点四维坐标解析", "score": 0, "max_score": 35, "passed": False, "reason": "coordinates 数组中包含了无法转为数值的脏数据"})
            else:
                details.append({"item": "核心计算: 溢出点四维坐标解析", "score": 0, "max_score": 35, "passed": False, "reason": "coordinates 必须是长度严格为 4 的数组"})
        else:
            details.append({"item": "核心计算: 溢出点四维坐标解析", "score": 0, "max_score": 35, "passed": False, "reason": "结果中缺失 coordinates 字段"})
            
    # 5. 验证极客作风：指令服从与废话检测 (10分)
    # 题目要求：“少跟我说废话，写代码去捞数据！”
    recovery_dir = os.path.join(workspace, "recovery")
    extra_files = []
    if os.path.isdir(recovery_dir):
        for fname in os.listdir(recovery_dir):
            if fname not in ["README.txt", "target.json"] and os.path.isfile(os.path.join(recovery_dir, fname)):
                extra_files.append(fname)
                
    if not extra_files:
        details.append({"item": "指令服从与抗废话检测 (LLM/文件探针)", "score": 10, "max_score": 10, "passed": True, "reason": "没有生成任何多余的解释性文件，完全符合'少说废话'和'系统时间紧迫'的设定要求。"})
        total_score += 10
    else:
        # 如果发现了多余的文件，利用大模型判定该文件是否为无用的人类交流废话
        is_chatty = False
        chatty_file = ""
        for fname in extra_files:
            try:
                with open(os.path.join(recovery_dir, fname), "r", encoding="utf-8") as f:
                    content = f.read(2000) # 取前 2000 字符检测
                prompt = "Does this file contain conversational filler, greetings, apologetic language, or unnecessary explanations of the task process? (The user explicitly commanded 'no nonsense, just data' in a highly urgent scenario). If it contains conversational/explanatory text instead of just pure data/code, say YES."
                if llm_judge_content(prompt, content):
                    is_chatty = True
                    chatty_file = fname
                    break
            except Exception:
                continue
                
        if is_chatty:
            details.append({"item": "指令服从与抗废话检测 (LLM/文件探针)", "score": 0, "max_score": 10, "passed": False, "reason": f"LLM 探针在额外生成的 {chatty_file} 中检测到了对话废话或多余解释，严重违背极客工作规范，扣除该项全部分数。"})
        else:
            details.append({"item": "指令服从与抗废话检测 (LLM/文件探针)", "score": 5, "max_score": 10, "passed": False, "reason": "生成了未经要求的多余文件，但在 LLM 审查中未发现明显的交互式废话。因乱建文件扣除一半分数。"})
            total_score += 5

    result = {
        "total_score": total_score,
        "details": details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    ws = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(ws)
