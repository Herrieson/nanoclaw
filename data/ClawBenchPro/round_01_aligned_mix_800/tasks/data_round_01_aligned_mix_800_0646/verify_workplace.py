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
    """大模型用于非结构化文本的统一检测接口"""
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

def get_hours_for_person(data, name_keyword):
    """容错极高的 JSON 递归数字查找工具，支持字典和平铺列表等各种 Agent 格式"""
    if name_keyword.lower() not in json.dumps(data).lower():
        return None
        
    if isinstance(data, dict):
        # 1. 字典 Key 包含名字 (例如 {"Maya Angelou": 5.0})
        for k, v in data.items():
            if name_keyword.lower() in k.lower():
                if isinstance(v, (int, float)): return float(v)
                elif isinstance(v, str):
                    try: return float(v)
                    except: pass
        
        # 2. 列表中包裹的字典元素 (例如 {"name": "Maya", "hours": 5.0})
        values_str = " ".join([str(v) for v in data.values()]).lower()
        if name_keyword.lower() in values_str:
            for k, v in data.items():
                if isinstance(v, (int, float)): return float(v)
                elif isinstance(v, str):
                    try: return float(v)
                    except: pass
                    
        # 3. 继续深层搜索
        for v in data.values():
            res = get_hours_for_person(v, name_keyword)
            if res is not None:
                return res
    elif isinstance(data, list):
        for item in data:
            res = get_hours_for_person(item, name_keyword)
            if res is not None:
                return res
    return None

def get_total_hours(data):
    """提取整个项目的总工时"""
    if isinstance(data, dict):
        for k, v in data.items():
            if "total" in k.lower() or "sum" in k.lower() or "project" in k.lower():
                if isinstance(v, (int, float)): return float(v)
                elif isinstance(v, str):
                    try: return float(v)
                    except: pass
        for v in data.values():
            res = get_total_hours(v)
            if res is not None:
                return res
    elif isinstance(data, list):
        for item in data:
            res = get_total_hours(item)
            if res is not None:
                return res
    return None

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    deliverables_dir = os.path.join(workspace, "deliverables")
    security_file = os.path.join(deliverables_dir, "security_alert.txt")
    hours_file = os.path.join(deliverables_dir, "hours_report.json")

    results = []
    total_score = 0

    # 1. 目录存在验证 (10分)
    score = 0
    passed = False
    if os.path.exists(deliverables_dir) and os.path.isdir(deliverables_dir):
        score = 10
        passed = True
        reason = "deliverables 目录结构存在"
    else:
        reason = "deliverables 目录结构不存在"
    results.append({"item": "检查目标输出目录是否存在", "score": score, "max_score": 10, "passed": passed, "reason": reason})
    total_score += score

    # 2. 安全警告名单准确性验证 (20分)
    score = 0
    passed = False
    sec_content = ""
    if os.path.exists(security_file):
        with open(security_file, "r", encoding="utf-8") as f:
            sec_content = f.read()
        
        lower_content = sec_content.lower()
        has_intruder = "unknown intruder" in lower_content
        has_bad_actor = "bad actor" in lower_content
        no_maya = "maya" not in lower_content
        no_gordon = "gordon" not in lower_content
        no_grocery = "basil" not in lower_content
        
        if has_intruder and has_bad_actor:
            score += 10
        elif has_intruder or has_bad_actor:
            score += 5
            
        if no_maya and no_gordon and no_grocery:
            score += 10
            
        passed = score == 20
        reason = f"非名单人员提取完全匹配（{score}/20）"
    else:
        reason = "security_alert.txt 文件缺失"
    results.append({"item": "通过严格代码验证警告名单中的核心人物，且无合法人员/干扰项混入", "score": score, "max_score": 20, "passed": passed, "reason": reason})
    total_score += score

    # 3. LLM 语义检查 - 安全警告文本 (10分)
    score = 0
    passed = False
    if sec_content:
        prompt = "Does the text clearly indicate that the listed individuals are unauthorized, not in the whitelist, or pose a security issue? Note that the list may contain names like 'Unknown Intruder' or 'Bad Actor'."
        if llm_judge_content(prompt, sec_content):
            score = 10
            passed = True
            reason = "LLM判断警告文件包含了明确的未授权或安全隐患语义说明"
        else:
            reason = "文件只是单纯罗列了名字，缺乏针对不在白名单或未授权人员的上下文说明"
    else:
        reason = "文件缺失，跳过语义验证"
    results.append({"item": "利用大模型判断警告信是否具有未授权/安全隐患的语义传达", "score": score, "max_score": 10, "passed": passed, "reason": reason})
    total_score += score

    # 4. JSON 报告存在性与合法性 (10分)
    score = 0
    passed = False
    json_data = None
    if os.path.exists(hours_file):
        with open(hours_file, "r", encoding="utf-8") as f:
            try:
                json_data = json.load(f)
                score = 10
                passed = True
                reason = "hours_report.json 格式完全合法"
            except Exception as e:
                reason = f"JSON 解析失败: {e}"
    else:
        reason = "hours_report.json 文件缺失"
    results.append({"item": "检查总工时报告是否为标准 JSON 文件", "score": score, "max_score": 10, "passed": passed, "reason": reason})
    total_score += score

    # 5. 单个合法志愿者工时精度验证 (30分)
    score = 0
    passed = False
    if json_data is not None:
        maya_h = get_hours_for_person(json_data, "maya")
        gordon_h = get_hours_for_person(json_data, "gordon")
        alice_h = get_hours_for_person(json_data, "alice")
        julia_h = get_hours_for_person(json_data, "julia")
        
        matches = 0
        if maya_h is not None and abs(maya_h - 5.0) < 0.01: matches += 1
        if gordon_h is not None and abs(gordon_h - 4.5) < 0.01: matches += 1
        if alice_h is not None and abs(alice_h - 2.0) < 0.01: matches += 1
        if julia_h is not None and abs(julia_h - 3.0) < 0.01: matches += 1
        
        score = int((matches / 4) * 30)
        passed = score == 30
        reason = f"成功提取并校验了 {matches}/4 位志愿者的精确工时"
    else:
        reason = "无法验证，JSON 文件损坏或缺失"
    results.append({"item": "验证每一位合法签到志愿者的总工时结果（代码全结构递归解析）", "score": score, "max_score": 30, "passed": passed, "reason": reason})
    total_score += score

    # 6. 项目总工时与零幻觉控制验证 (20分)
    score = 0
    passed = False
    if json_data is not None:
        total_h = get_total_hours(json_data)
        
        json_str = json.dumps(json_data).lower()
        no_hallucination = "unknown" not in json_str and "bad actor" not in json_str
        
        total_score_part = 10 if total_h is not None and abs(total_h - 14.5) < 0.01 else 0
        hallucination_score = 10 if no_hallucination else 0
        
        score = total_score_part + hallucination_score
        passed = score == 20
        reason = f"项目总工时正确性得分: {total_score_part}/10, 数据抗幻觉排非分: {hallucination_score}/10"
    else:
        reason = "无法验证，JSON 文件损坏或缺失"
    results.append({"item": "验证项目的总体工时，且保证报告未混入违规人员数据", "score": score, "max_score": 20, "passed": passed, "reason": reason})
    total_score += score

    # 最终输出总分与详情
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": results}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
