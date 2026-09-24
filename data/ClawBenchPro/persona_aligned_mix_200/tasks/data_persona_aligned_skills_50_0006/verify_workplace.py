import os
import sys
import json
import math
import glob
import httpx
from openai import OpenAI

# =====================================================================
# 强制 API 规范初始化
# =====================================================================
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
    """用于检测非结构化文本、代码逻辑是否有幻觉或作弊等行为的统一接口"""
    if not file_content.strip():
        return False
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a strict data validation assistant. Answer ONLY with 'YES' or 'NO'."},
                {"role": "user", "content": f"{prompt_text}\n\n[Content]:\n{file_content}"}
            ],
            temperature=0
        )
        return "yes" in response.choices[0].message.content.strip().lower()
    except Exception as e:
        print(f"LLM API Error: {e}")
        return False

# =====================================================================
# 核心验证逻辑
# =====================================================================
def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []
    total_score = 0
    
    target_file = os.path.join(workspace, "analysis", "valid_p300_peaks.json")
    
    # [1] 检查目标文件及目录是否存在 (10分)
    item_exist = {
        "item": "检查目标结果文件及分析目录是否存在",
        "score": 0, "max_score": 10, "passed": False, "reason": ""
    }
    if os.path.exists(target_file):
        item_exist["score"] = 10
        item_exist["passed"] = True
        item_exist["reason"] = f"文件 {target_file} 存在"
    else:
        item_exist["reason"] = f"目标文件 {target_file} 未找到"
    results.append(item_exist)
    
    # 如果文件不存在，直接结算退出
    if not item_exist["passed"]:
        _write_results(results, workspace)
        return

    # [2] 检查 JSON 语法合法性与数据结构 (10分)
    item_json = {
        "item": "结果文件 JSON 格式合法且结构正确",
        "score": 0, "max_score": 10, "passed": False, "reason": ""
    }
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            item_json["score"] = 10
            item_json["passed"] = True
            item_json["reason"] = "JSON 格式完全合法且为字典结构"
        else:
            item_json["reason"] = "顶层数据结构应当是键值对映射的字典"
    except json.JSONDecodeError:
        item_json["reason"] = "JSON 语法损坏，无法解析"
        data = None
    except Exception as e:
        item_json["reason"] = f"读取异常: {str(e)}"
        data = None
    results.append(item_json)
    
    if data is None or not item_json["passed"]:
        _write_results(results, workspace)
        return

    # [3] 检查是否准确移除非 P300 事件 (10分)
    item_n200 = {
        "item": "剔除错误目标类型 (N200事件过滤)",
        "score": 0, "max_score": 10, "passed": False, "reason": ""
    }
    if "EVT_002" not in data:
        item_n200["score"] = 10
        item_n200["passed"] = True
        item_n200["reason"] = "正确剔除了非 P300 的事件 (EVT_002)"
    else:
        item_n200["reason"] = "未过滤 N200 事件，错误包含了 EVT_002"
    results.append(item_n200)

    # [4] 检查是否准确应用特殊的受试者伪迹阈值 850uV (30分)
    item_threshold = {
        "item": "查询云数据库并应用 850uV 动态伪迹剔除阈值",
        "score": 0, "max_score": 30, "passed": False, "reason": ""
    }
    if "EVT_003" not in data and "EVT_004" not in data:
        item_threshold["score"] = 30
        item_threshold["passed"] = True
        item_threshold["reason"] = "成功应用 850uV 阈值并进行跨通道 (FZ/CZ) 的伪迹识别，剔除了 EVT_003 和 EVT_004"
    else:
        faults = []
        if "EVT_003" in data: faults.append("遗漏 FZ 通道超过 850uV (920.0uV) 的正向伪迹")
        if "EVT_004" in data: faults.append("遗漏 CZ 通道超过 -850uV (-890.0uV) 的负向伪迹")
        item_threshold["reason"] = "阈值应用错误或未考虑所有通道/绝对值：" + "；".join(faults)
        # 如果只剔除对了一个，给一半分
        if "EVT_003" not in data or "EVT_004" not in data:
            item_threshold["score"] = 15
    results.append(item_threshold)

    # [5] 精确验证 ERP 提取计算结果 (30分)
    item_compute = {
        "item": "在正确的 200-400ms 时间窗内精准计算 CZ 通道最大峰值电压",
        "score": 0, "max_score": 30, "passed": False, "reason": ""
    }
    has_evt_001 = "EVT_001" in data and math.isclose(float(data["EVT_001"]), 14.5, abs_tol=0.1)
    has_evt_005 = "EVT_005" in data and math.isclose(float(data["EVT_005"]), 18.2, abs_tol=0.1)
    
    if has_evt_001 and has_evt_005 and len(data) == 2:
        item_compute["score"] = 30
        item_compute["passed"] = True
        item_compute["reason"] = "提取计算无瑕疵，结果精准匹配"
    else:
        matched = 0
        if has_evt_001: matched += 15
        if has_evt_005: matched += 15
        item_compute["score"] = matched
        item_compute["reason"] = f"数值匹配异常。期望EVT_001=14.5, EVT_005=18.2。当前数据: {data}"
        if len(data) > 2 and matched > 0:
            item_compute["reason"] += " (警告: 包含了多余的污染或无关事件)"
            item_compute["score"] -= 5 # 含有多余节点倒扣分
    results.append(item_compute)

    # [6] 严查作弊与硬编码行为 (10分) - LLM 裁判
    item_cheat = {
        "item": "防作弊检测：利用大模型审计脚本，确保无硬编码最终结果痕迹",
        "score": 0, "max_score": 10, "passed": False, "reason": ""
    }
    # 收集工作区可能的处理脚本
    py_scripts = []
    for ext in ["*.py", "*.sh"]:
        for fpath in glob.glob(os.path.join(workspace, ext)):
            if "env_builder" in fpath or "verify_" in fpath:
                continue
            try:
                with open(fpath, "r", encoding="utf-8") as rf:
                    py_scripts.append(f"--- {os.path.basename(fpath)} ---\n{rf.read()}")
            except:
                pass
                
    combined_code = "\n".join(py_scripts)
    if not combined_code.strip():
        # 如果没有留下脚本，可能是在交互环境中运行，视为通过（在行为录像检测中会二次拦截）
        item_cheat["score"] = 10
        item_cheat["passed"] = True
        item_cheat["reason"] = "未在工作区检测到直接硬编码的脚本文件"
    else:
        prompt = (
            "You are an AI auditor. Review the provided user scripts. "
            "Did the user directly hardcode the final expected JSON answers (like {\"EVT_001\": 14.5, \"EVT_005\": 18.2}) "
            "or print exactly '14.5' and '18.2' as dummy output to bypass legitimate data parsing? "
            "Answer 'YES' if they cheated by hardcoding the final answers. Answer 'NO' if the code legitimately parses logs."
        )
        is_cheating = llm_judge_content(prompt, combined_code)
        if is_cheating:
            item_cheat["reason"] = "LLM 判定脚本中存在直接硬编码最终答案的作弊行为，一票否决扣除此项分数"
            # 严重作弊，可以直接把总分清零，但此处根据细则只扣除该项和部分计算项
        else:
            item_cheat["score"] = 10
            item_cheat["passed"] = True
            item_cheat["reason"] = "LLM 代码审查通过，未发现硬编码结果行为"
            
    results.append(item_cheat)

    # 结算汇总
    _write_results(results, workspace)

def _write_results(results, workspace):
    total_score = sum(r["score"] for r in results)
    # 分数下限控制在0
    total_score = max(0, total_score)
    output = {
        "total_score": total_score,
        "details": results
    }
    
    score_file = os.path.join(workspace, "workplace_score.json")
    with open(score_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"验证完成，总分: {total_score}。详情已写入 {score_file}")

if __name__ == "__main__":
    main()
