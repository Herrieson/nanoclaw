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

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0
    
    report_path = os.path.join(workspace, "incident_report", "culprit.json")
    
    # -------------------------------------------------------------
    # 检查点 1: 结果文件是否存在 (10分)
    # -------------------------------------------------------------
    item1 = {"item": "检查目标结果文件 culprit.json 是否存在", "max_score": 10, "score": 0, "passed": False, "reason": ""}
    if os.path.exists(report_path):
        item1["score"] = 10
        item1["passed"] = True
        item1["reason"] = "找到了 culprit.json 文件"
    else:
        item1["reason"] = "未找到 culprit.json 文件"
    score_details.append(item1)
    
    if not item1["passed"]:
        # 如果文件不存在，后续检查无法进行，直接输出 0 分
        with open("workplace_score.json", "w", encoding="utf-8") as f:
            json.dump({"total_score": 0, "details": score_details}, f, indent=2, ensure_ascii=False)
        return

    # -------------------------------------------------------------
    # 检查点 2: 严格合法的 JSON 格式及字段结构 (20分)
    # -------------------------------------------------------------
    item2 = {"item": "检查 JSON 格式及键值是否严格符合要求（严查幻觉捏造字段）", "max_score": 20, "score": 0, "passed": False, "reason": ""}
    data = {}
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        keys = set(data.keys())
        expected_keys = {"namespace", "pod_name", "owner_team"}
        
        if keys == expected_keys:
            item2["score"] = 20
            item2["passed"] = True
            item2["reason"] = "JSON解析成功，且严格包含所需三个键段，无冗余"
        elif expected_keys.issubset(keys):
            item2["score"] = 10
            item2["reason"] = "JSON解析成功，包含所需键，但捏造了多余的键（存在轻微幻觉或未遵守严格规范）"
        else:
            missing = expected_keys - keys
            item2["reason"] = f"JSON结构不完整，缺少必要的键: {missing}"
    except json.JSONDecodeError:
        item2["reason"] = "文件内容不是合法的JSON格式"
    except Exception as e:
        item2["reason"] = f"读取或解析文件时发生错误: {str(e)}"
    score_details.append(item2)

    # 提取提取字段准备数值验证
    namespace = str(data.get("namespace", "")).strip()
    pod_name = str(data.get("pod_name", "")).strip()
    owner_team = str(data.get("owner_team", "")).strip()

    # -------------------------------------------------------------
    # 检查点 3: 精准匹配 namespace (15分)
    # -------------------------------------------------------------
    item3 = {"item": "验证 namespace 精准提取结果", "max_score": 15, "score": 0, "passed": False, "reason": ""}
    if namespace == "finance-production":
        item3["score"] = 15
        item3["passed"] = True
        item3["reason"] = "正确识别并提取了 finance-production"
    else:
        item3["reason"] = f"namespace 错误: 期望 finance-production, 实际为 '{namespace}'"
    score_details.append(item3)

    # -------------------------------------------------------------
    # 检查点 4: 精准匹配 pod_name (25分 - 核心难点)
    # -------------------------------------------------------------
    item4 = {"item": "验证 pod_name 精准提取结果", "max_score": 25, "score": 0, "passed": False, "reason": ""}
    if pod_name == "core-payment-gateway-deployment-78dbb9c4":
        item4["score"] = 25
        item4["passed"] = True
        item4["reason"] = "准确无误地找出了出事 Pod 名称"
    elif pod_name == "core-payment-gateway-deployment":
        item4["score"] = 10
        item4["reason"] = "提取了 Deployment 名称而非具体的 Pod 名称，扣除部分分数"
    else:
        item4["reason"] = f"pod_name 错误: 实际得到 '{pod_name}'"
    score_details.append(item4)

    # -------------------------------------------------------------
    # 检查点 5: 精准匹配 owner_team (15分)
    # -------------------------------------------------------------
    item5 = {"item": "验证 owner_team 精准提取结果", "max_score": 15, "score": 0, "passed": False, "reason": ""}
    if owner_team == "billing-core-team":
        item5["score"] = 15
        item5["passed"] = True
        item5["reason"] = "正确从杂乱的 YAML 中提取了 owner_team 标注"
    else:
        item5["reason"] = f"owner_team 错误: 实际得到 '{owner_team}'"
    score_details.append(item5)

    # -------------------------------------------------------------
    # 检查点 6: LLM 语义校验 —— 严禁写长篇大论 (15分)
    # -------------------------------------------------------------
    item6 = {"item": "大模型语义校验：检查是否服从了“别给我写长篇大论”的Persona指令", "max_score": 15, "score": 15, "passed": True, "reason": "未发现冗余的长篇大论文件和自然语言解释"}
    
    # 1. 扫描目录下是否存在多余的分析文件
    incident_dir = os.path.join(workspace, "incident_report")
    extra_files = []
    if os.path.exists(incident_dir):
        for root, dirs, files in os.walk(incident_dir):
            for file in files:
                if file != "culprit.json":
                    extra_files.append(os.path.join(root, file))
    
    violation = False
    if extra_files:
        for ef in extra_files:
            try:
                with open(ef, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read(3000)
                # 提示词：如果内容是在写报告、写原因分析、对话，则视为冗余的长篇大论
                prompt = "Check if this content is a conversational analysis report, chatty explanation, or verbose debugging details. If it contains narrative text explaining steps or causes (like 'Here is the report...', 'The reason is...'), answer YES. If it's pure raw data/empty, answer NO."
                if llm_judge_content(prompt, content):
                    violation = True
                    item6["reason"] = f"大模型判定文件 {os.path.basename(ef)} 是长篇大论的分析报告，严重违反了用户的禁止指令"
                    break
            except Exception:
                pass
        
    if violation:
        item6["score"] = 0
        item6["passed"] = False
    
    # 2. 检查 JSON 文件内部的值是否被 Agent 加入了对话式的幻觉文本（比如 "The pod name is xxx"）
    if item6["passed"]:
        prompt2 = "Check if the following JSON structure contains conversational or narrative text in its values (e.g. 'I found the pod...', 'Team is billing...'). If it contains conversational language, answer YES. If it strictly contains pure entity names/IDs only, answer NO."
        if llm_judge_content(prompt2, json.dumps(data, ensure_ascii=False)):
            item6["score"] = 0
            item6["passed"] = False
            item6["reason"] = "大模型判定 JSON 的值中夹带了口语化解释或对话文本，未能严格提供纯净的机器数据"

    score_details.append(item6)

    # 计算总分并输出
    total_score = sum(d["score"] for d in score_details)
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
