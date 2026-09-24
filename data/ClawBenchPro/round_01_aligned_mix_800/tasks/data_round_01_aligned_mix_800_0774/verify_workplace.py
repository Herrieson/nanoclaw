import os
import sys
import json
import httpx
from openai import OpenAI

# =====================================================================
# 强制的 API 规范初始化
# =====================================================================
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
    统一接口：利用大模型做不可精确结构化的语义探针。
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

# =====================================================================
# 原生代码精准匹配探针，杜绝简单正则造成的结构化数据假阳性
# =====================================================================
def check_violators_anywhere(data):
    """
    递归遍历整个 JSON 数据结构（字典键值或列表），
    寻找是否精确识别出了违规者（John Doe, Jane Smith），且绝不包含被授权员工。
    """
    if isinstance(data, dict):
        # 如果是字典，递归检查所有的键和值，防止Agent将人名设为key
        items = list(data.keys()) + list(data.values())
        for item in items:
            if check_violators_anywhere(item):
                return True
    elif isinstance(data, list):
        strs = [str(s).lower().strip() for s in data if isinstance(s, str)]
        # 必须把两个违规者找全
        if any("john doe" in s for s in strs) and any("jane smith" in s for s in strs):
            # 且坚决不能误伤授权员工
            if not any("siobhan" in s or "liam" in s or "aisling" in s for s in strs):
                return True
        for item in data:
            if check_violators_anywhere(item):
                return True
    elif isinstance(data, str):
        s = data.lower()
        if "john doe" in s and "jane smith" in s:
            if not any("siobhan" in s or "liam" in s or "aisling" in s for s in s):
                return True
    return False

def check_hours_strict(data):
    """
    递归遍历整个 JSON 数据结构，寻找正确的工时计算结果数值（455 分钟）。
    允许转换为了 7.5833 (7.58 / 7.5) 小时的情况。
    """
    if isinstance(data, dict):
        for v in data.values():
            if check_hours_strict(v):
                return True
    elif isinstance(data, list):
        for v in data:
            if check_hours_strict(v):
                return True
    elif isinstance(data, (int, float)):
        # 容忍少量精度误差
        if abs(data - 455) < 0.1 or abs(data - 7.58) < 0.1 or abs(data - 7.5) < 0.1:
            return True
    elif isinstance(data, str):
        s = data.lower().strip()
        if "455" in s or "7.58" in s or "7.5 " in s:
            return True
    return False

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    total_score = 0
    details = []
    
    # 1. 检测目录存在性 (10分)
    audit_dir = os.path.join(workspace, "audit_reports")
    if os.path.isdir(audit_dir):
        total_score += 10
        details.append({"item": "检查结果目录 audit_reports 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录 audit_reports 存在"})
    else:
        details.append({"item": "检查结果目录 audit_reports 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 audit_reports 目录"})
        with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": details}, f, ensure_ascii=False, indent=2)
        return
    
    # 2. 检测 JSON 文件是否生成并合法 (15分)
    json_files = [f for f in os.listdir(audit_dir) if f.endswith(".json")]
    json_data = None
    json_content_str = ""
    if json_files:
        json_path = os.path.join(audit_dir, json_files[0])
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                json_content_str = f.read()
                json_data = json.loads(json_content_str)
            total_score += 15
            details.append({"item": "生成文件格式要求", "score": 15, "max_score": 15, "passed": True, "reason": f"成功读取并解析 {json_files[0]} 为规范 JSON"})
        except Exception as e:
            details.append({"item": "生成文件格式要求", "score": 0, "max_score": 15, "passed": False, "reason": f"文件解析失败或不是干净的 JSON: {e}"})
    else:
        details.append({"item": "生成文件格式要求", "score": 0, "max_score": 15, "passed": False, "reason": "在目录中未找到以 .json 结尾的文件"})

    # 如果没有合法的 JSON 对象，后续的数据提取项全按失败处理
    # 3. 数据精确提取探针：违规者判定 (30分)
    if json_data is not None:
        if check_violators_anywhere(json_data):
            total_score += 30
            details.append({"item": "精准提取违规人员名单", "score": 30, "max_score": 30, "passed": True, "reason": "在结果中完美找齐未授权人且没有误伤授权者"})
        else:
            details.append({"item": "精准提取违规人员名单", "score": 0, "max_score": 30, "passed": False, "reason": "未能精准提取出 John Doe 与 Jane Smith，或者掺杂了授权员工"})
    else:
        details.append({"item": "精准提取违规人员名单", "score": 0, "max_score": 30, "passed": False, "reason": "无法执行数据提取(JSON缺失)"})
        
    # 4. 数据精确提取探针：工时总和判定 (25分)
    if json_data is not None:
        if check_hours_strict(json_data):
            total_score += 25
            details.append({"item": "精准计算计费总工时", "score": 25, "max_score": 25, "passed": True, "reason": "成功统计并提取数值 455(分钟) 或等效小时数"})
        else:
            details.append({"item": "精准计算计费总工时", "score": 0, "max_score": 25, "passed": False, "reason": "未能提取到正确的总工时数值，说明过滤脏数据或聚合计算失败"})
    else:
        details.append({"item": "精准计算计费总工时", "score": 0, "max_score": 25, "passed": False, "reason": "无法执行数据提取(JSON缺失)"})

    # 5. LLM语义探针：报告纯净度与无幻觉检测 (20分)
    if json_content_str:
        prompt_text = (
            "You are a strict legal data validation assistant. Evaluate the provided JSON document. "
            "It should act as an audit report containing ONLY unauthorized access persons and total billable hours. "
            "Does this JSON cleanly present the necessary data without inventing unnecessary narrative, "
            "conversational text, or hallucinatory fields (e.g. fabricated timestamps, unrelated activities, or apology letters)? "
            "Note: The structural keys can vary, but the content MUST strictly be business data only."
        )
        if llm_judge_content(prompt_text, json_content_str):
            total_score += 20
            details.append({"item": "LLM语义检验：内容纯净度", "score": 20, "max_score": 20, "passed": True, "reason": "大模型判定 JSON 结构纯净，无过度闲聊或捏造的额外字段"})
        else:
            details.append({"item": "LLM语义检验：内容纯净度", "score": 0, "max_score": 20, "passed": False, "reason": "大模型检测出报告中包含了冗余非结构化文本、邮件格式或捏造的伪造字段信息"})
    else:
        details.append({"item": "LLM语义检验：内容纯净度", "score": 0, "max_score": 20, "passed": False, "reason": "没有内容可供检验"})

    # 输出最终评分结果文件
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": details}, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
