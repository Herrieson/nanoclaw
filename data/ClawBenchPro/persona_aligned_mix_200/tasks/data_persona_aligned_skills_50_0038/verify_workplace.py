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

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0
    
    report_path = os.path.join(workspace, "reports", "violation_root.json")
    
    # 1. 检查物理文件存在性 [10分]
    file_exists = os.path.exists(report_path)
    if file_exists:
        score_details.append({"item": "检查报告文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目标文件 reports/violation_root.json 成功创建。"})
        total_score += 10
    else:
        score_details.append({"item": "检查报告文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到报告文件 reports/violation_root.json。"})
        
    if not file_exists:
        # 短路后续验证
        score_details.extend([
            {"item": "利用大模型检查内容是否剔除废话", "score": 0, "max_score": 20, "passed": False, "reason": "文件不存在。"},
            {"item": "检查文件是否为原生严谨的 JSON 结构", "score": 0, "max_score": 15, "passed": False, "reason": "文件不存在。"},
            {"item": "检查 JSON 字段完整性与无幻觉多余节点", "score": 0, "max_score": 15, "passed": False, "reason": "文件不存在。"},
            {"item": "检查 timestamp_ps 的纯数字格式与数值精准性", "score": 0, "max_score": 20, "passed": False, "reason": "文件不存在。"},
            {"item": "检查 module_instance 的物理路径精准性", "score": 0, "max_score": 20, "passed": False, "reason": "文件不存在。"}
        ])
    else:
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 2. LLM 非结构化语义验证 (剔除解释性冗余) [20分]
        prompt = (
            "The user explicitly stated: 'Do not give me long-winded analysis, just the core data'. "
            "Examine the following file content. Does it successfully AVOID any conversational filler, "
            "explanations, markdown codeblock wraps outside the JSON, or verbose technical analysis? "
            "Answer YES if it is purely a clean data file structure without human-like chatter, NO if it violates this rule."
        )
        is_clean = llm_judge_content(prompt, content)
        if is_clean:
            score_details.append({"item": "利用大模型检查内容是否剔除废话", "score": 20, "max_score": 20, "passed": True, "reason": "大模型判定内容极致纯粹，无任何冗长分析或聊天废话。"})
            total_score += 20
        else:
            score_details.append({"item": "利用大模型检查内容是否剔除废话", "score": 0, "max_score": 20, "passed": False, "reason": "大模型判定内容包含了违反要求的格式外文本、长篇大论或解释性内容。"})
            
        # 3. 结构确定性验证: 原生 JSON 解析 [15分]
        try:
            data = json.loads(content)
            score_details.append({"item": "检查文件是否为原生严谨的 JSON 结构", "score": 15, "max_score": 15, "passed": True, "reason": "可原生 json.loads，无语法错误或非标准包裹。"})
            total_score += 15
            
            # 4. JSON Schema / 幻觉与捏造检查 [15分]
            if not isinstance(data, dict):
                score_details.append({"item": "检查 JSON 字段完整性与无幻觉多余节点", "score": 0, "max_score": 15, "passed": False, "reason": "JSON 的根节点必须是一个 Object 字典。"})
                data = {}
            else:
                expected_keys = {"module_instance", "timestamp_ps"}
                actual_keys = set(data.keys())
                
                if expected_keys.issubset(actual_keys) and actual_keys == expected_keys:
                    score_details.append({"item": "检查 JSON 字段完整性与无幻觉多余节点", "score": 15, "max_score": 15, "passed": True, "reason": "包含且仅包含指定的核心 key，没有捏造多余字段。"})
                    total_score += 15
                elif expected_keys.issubset(actual_keys):
                    score_details.append({"item": "检查 JSON 字段完整性与无幻觉多余节点", "score": 0, "max_score": 15, "passed": False, "reason": f"包含必需字段，但也捏造了多余的字段（幻觉行为）。提取的 keys: {list(actual_keys)}"})
                else:
                    score_details.append({"item": "检查 JSON 字段完整性与无幻觉多余节点", "score": 0, "max_score": 15, "passed": False, "reason": f"缺失必需的底层结构 key。当前 keys: {list(actual_keys)}"})
                    
            # 5. 精准数据提取: 时间点 [20分]
            ts = data.get("timestamp_ps", None)
            ts_correct = False
            if isinstance(ts, int) and ts == 478230:
                ts_correct = True
            elif isinstance(ts, str) and ts.strip() == "478230":
                ts_correct = True
                
            if ts_correct:
                score_details.append({"item": "检查 timestamp_ps 的纯数字格式与数值精准性", "score": 20, "max_score": 20, "passed": True, "reason": "X 态时间戳精准为 478230，且为纯数字表现形式。"})
                total_score += 20
            else:
                score_details.append({"item": "检查 timestamp_ps 的纯数字格式与数值精准性", "score": 0, "max_score": 20, "passed": False, "reason": f"数值计算错误、混入单位文本或格式非法。实际提取值: {ts}"})
                
            # 6. 精准数据提取: 实例路径 [20分]
            mi = data.get("module_instance", None)
            if isinstance(mi, str) and mi.strip() == "sys_top.bus_matrix.u_axi_interconnect_m0":
                score_details.append({"item": "检查 module_instance 的物理路径精准性", "score": 20, "max_score": 20, "passed": True, "reason": "受污染底层逻辑实例映射提取绝对正确。"})
                total_score += 20
            else:
                score_details.append({"item": "检查 module_instance 的物理路径精准性", "score": 0, "max_score": 20, "passed": False, "reason": f"路径未精准匹配。实际提取值: {mi}"})
                
        except json.JSONDecodeError:
            score_details.append({"item": "检查文件是否为原生严谨的 JSON 结构", "score": 0, "max_score": 15, "passed": False, "reason": "JSON 严格模式解析失败，涉嫌包裹非结构化文本。"})
            score_details.extend([
                {"item": "检查 JSON 字段完整性与无幻觉多余节点", "score": 0, "max_score": 15, "passed": False, "reason": "基础解析失败。"},
                {"item": "检查 timestamp_ps 的纯数字格式与数值精准性", "score": 0, "max_score": 20, "passed": False, "reason": "基础解析失败。"},
                {"item": "检查 module_instance 的物理路径精准性", "score": 0, "max_score": 20, "passed": False, "reason": "基础解析失败。"}
            ])

    # 导出不可篡改的最终计分卡
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({
            "total_score": total_score,
            "details": score_details
        }, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
