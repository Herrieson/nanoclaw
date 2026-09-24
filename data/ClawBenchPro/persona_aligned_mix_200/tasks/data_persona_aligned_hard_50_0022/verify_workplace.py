import os
import sys
import json
import httpx
from openai import OpenAI

# 强制 API 规范 (用于潜在的非结构化语义验证扩展)
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
    """
    此函数为检测非结构化文本的统一接口。
    在本任务中，要求的结果严格为结构化 JSON 故主要依靠原生代码解析，此接口留作备用。
    """
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
    score_file = os.path.join(workspace, "workplace_score.json")
    
    total_score = 0
    details = []
    
    target_file = os.path.join(workspace, "pipeline_fixes", "patch.json")
    
    # 1. 检查结果文件及目录是否存在 [10分]
    if os.path.exists(target_file):
        total_score += 10
        details.append({
            "item": "检查结果文件及目录是否存在", 
            "score": 10, 
            "max_score": 10, 
            "passed": True, 
            "reason": "目标文件 pipeline_fixes/patch.json 成功创建"
        })
    else:
        details.append({
            "item": "检查结果文件及目录是否存在", 
            "score": 0, 
            "max_score": 10, 
            "passed": False, 
            "reason": "未找到目标文件 pipeline_fixes/patch.json，请检查路径及文件名是否正确"
        })
        # 基础文件不存在，后续验证无法进行
        with open(score_file, "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": details}, f, ensure_ascii=False, indent=2)
        return

    # 2. 检查文件格式是否为合法JSON [10分]
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        total_score += 10
        details.append({
            "item": "检查文件格式", 
            "score": 10, 
            "max_score": 10, 
            "passed": True, 
            "reason": "成功解析 JSON 格式，语法合法"
        })
    except Exception as e:
        details.append({
            "item": "检查文件格式", 
            "score": 0, 
            "max_score": 10, 
            "passed": False, 
            "reason": f"JSON 解析失败，文件可能包含格式错误或幻觉杂音: {e}"
        })
        with open(score_file, "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": details}, f, ensure_ascii=False, indent=2)
        return

    # 3. 字段与数据结构完整性 [20分]
    # 严格检查：只能包含题目要求的两个字段，如果有大模型的幻觉输出（如 "status": "fixed" 等），坚决扣分。
    if not isinstance(data, dict):
        details.append({
            "item": "字段与数据结构完整性", 
            "score": 0, 
            "max_score": 20, 
            "passed": False, 
            "reason": "JSON 的根节点必须是一个字典对象"
        })
    else:
        keys = set(data.keys())
        expected_keys = {"broken_node", "missing_texture"}
        if keys == expected_keys:
            total_score += 20
            details.append({
                "item": "字段与数据结构完整性", 
                "score": 20, 
                "max_score": 20, 
                "passed": True, 
                "reason": "字段完全匹配要求且无任何冗余伪造字段"
            })
        elif expected_keys.issubset(keys):
            total_score += 10
            details.append({
                "item": "字段与数据结构完整性", 
                "score": 10, 
                "max_score": 20, 
                "passed": False, 
                "reason": f"包含了必要的字段，但严禁捏造多余字段，发现冗余键: {keys - expected_keys}"
            })
        else:
            missing = expected_keys - keys
            details.append({
                "item": "字段与数据结构完整性", 
                "score": 0, 
                "max_score": 20, 
                "passed": False, 
                "reason": f"缺失要求输出的必要字段: {missing}"
            })

    # 4. 检查崩溃节点提取准确度 [30分]
    broken_node = data.get("broken_node", "")
    if broken_node == "SHD_Mutant_Flesh_Core_v9":
        total_score += 30
        details.append({
            "item": "崩溃节点提取准确度", 
            "score": 30, 
            "max_score": 30, 
            "passed": True, 
            "reason": "精准绕过 SC042 和 v098 陷阱，成功提取出导致 SC043_v099 崩溃的目标节点"
        })
    elif broken_node in ["SHD_Old_Eye_v01", "SHD_Car_Paint"]:
        details.append({
            "item": "崩溃节点提取准确度", 
            "score": 0, 
            "max_score": 30, 
            "passed": False, 
            "reason": f"致命错误！版本或项目筛选失败，提取到了诱饵干扰节点: {broken_node}"
        })
    else:
        details.append({
            "item": "崩溃节点提取准确度", 
            "score": 0, 
            "max_score": 30, 
            "passed": False, 
            "reason": f"节点不匹配，可能是幻觉或使用了错误的正则表达式，提取到的值为: {broken_node}"
        })

    # 5. 检查贴图路径变量替换正确性 [30分]
    missing_texture = data.get("missing_texture", "")
    expected_path = "/prod/show/SC043/assets/chars/mutant/tex/v099/diffuse_UDIM_1001.tx"
    unresolved_path = "${JOB}/${SEQ}/assets/chars/mutant/tex/${VER}/diffuse_UDIM_1001.tx"
    
    if missing_texture == expected_path:
        total_score += 30
        details.append({
            "item": "贴图路径变量替换及还原", 
            "score": 30, 
            "max_score": 30, 
            "passed": True, 
            "reason": "完美结合 _context 字典，将所有的占位符成功替换为绝对路径"
        })
    elif missing_texture == unresolved_path or "${JOB}" in missing_texture or "${SEQ}" in missing_texture:
        # 找到了路径，但是没有执行上下文展开，给出部分分数
        total_score += 15
        details.append({
            "item": "贴图路径变量替换及还原", 
            "score": 15, 
            "max_score": 30, 
            "passed": False, 
            "reason": "找到了对应的贴图路径并提取，但直接抄写了含变量的模板，未读取 _context 进行占位符解析"
        })
    else:
        details.append({
            "item": "贴图路径变量替换及还原", 
            "score": 0, 
            "max_score": 30, 
            "passed": False, 
            "reason": f"未找到或生成了完全错误的贴图路径，提取到的值为: {missing_texture}"
        })

    # 写入结果
    with open(score_file, "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": details}, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    verify()
