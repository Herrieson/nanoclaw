import os
import sys
import json
import httpx
from openai import OpenAI

# 强制 API 规范：从环境变量读取配置，关闭 SSL 验证
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
    统一的非结构化文本大模型验证接口。
    用于验证 Agent 生成的结构化数据的键名是否符合自然语言描述的“清晰直观”。
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

def verify_workplace(workspace):
    score_details = []
    total_score = 0
    
    file_path = os.path.join(workspace, "analysis", "culprit.json")
    
    # 1. 检查目标文件及其目录结构的存在性
    exists = os.path.isfile(file_path)
    if exists:
        score_details.append({"item": "检查目标分析文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件 analysis/culprit.json 存在"})
        total_score += 10
    else:
        score_details.append({"item": "检查目标分析文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 analysis/culprit.json，目录或文件未建立"})
        
    # 如果文件不存在，后续所有基于文件内容的验证均得0分
    if not exists:
        for item in ["JSON格式合法性验证", "防作弊与幻觉检查(字段数<=5)", "精确提取源码位置", "精确提取受害者符号名", "精确提取去优化核心原因", "LLM评估数据字段命名语义"]:
            score_details.append({"item": item, "score": 0, "max_score": 15, "passed": False, "reason": "依赖的分析文件不存在"})
        return score_details, total_score

    # 2. 原生代码验证：JSON 格式绝对合法性
    data = None
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            score_details.append({"item": "JSON格式合法性验证", "score": 15, "max_score": 15, "passed": True, "reason": "文件解析成功，且最外层为标准的 JSON Object (字典) 结构"})
            total_score += 15
        else:
            score_details.append({"item": "JSON格式合法性验证", "score": 0, "max_score": 15, "passed": False, "reason": "最外层格式非 JSON Object (可能为 Array 或裸字串)"})
            data = None
    except Exception as e:
        score_details.append({"item": "JSON格式合法性验证", "score": 0, "max_score": 15, "passed": False, "reason": f"结构化解析失败，不符合 JSON Schema：{str(e)}"})

    if data is None:
        for item in ["防作弊与幻觉检查(字段数<=5)", "精确提取源码位置", "精确提取受害者符号名", "精确提取去优化核心原因", "LLM评估数据字段命名语义"]:
            score_details.append({"item": item, "score": 0, "max_score": 15, "passed": False, "reason": "非法的 JSON 数据导致无法检测值"})
        return score_details, total_score
        
    # 3. 防作弊与幻觉检查 (严格限制 Agent 捏造冗余节点或全量 Dump)
    if len(data.keys()) <= 5:
        score_details.append({"item": "防作弊与幻觉检查(字段数<=5)", "score": 15, "max_score": 15, "passed": True, "reason": f"当前键值对数量为 {len(data.keys())}，符合针对性提取特征，未触发暴力 Dump 防御"})
        total_score += 15
    else:
        score_details.append({"item": "防作弊与幻觉检查(字段数<=5)", "score": 0, "max_score": 15, "passed": False, "reason": f"当前键值对数量 {len(data.keys())} 超过阈值，疑似暴力写入全部信息而非特定提炼"})
        
    # 将所有的 Value 转化为字符串，去除非结构化空格，执行原生代码全等严密对比
    values_str = [str(v).strip() for v in data.values()]
    
    # 4. 精确提取：源码物理位置
    if any(v == "/app/src/core/hot_path_router.js" for v in values_str):
        score_details.append({"item": "精确提取源码位置", "score": 15, "max_score": 15, "passed": True, "reason": "准确地映射出了反人类 JSON 下的 source_loc"})
        total_score += 15
    else:
        score_details.append({"item": "精确提取源码位置", "score": 0, "max_score": 15, "passed": False, "reason": "未能精准提取到正确的文件路径 /app/src/core/hot_path_router.js，存在幻觉或混淆"})

    # 5. 精确提取：函数符号名
    if any(v == "processRequestFastPath" for v in values_str):
        score_details.append({"item": "精确提取受害者符号名", "score": 15, "max_score": 15, "passed": True, "reason": "准确地锁定了触发 deoptimization 的热点函数名"})
        total_score += 15
    else:
        score_details.append({"item": "精确提取受害者符号名", "score": 0, "max_score": 15, "passed": False, "reason": "未能精准提取到目标 symbol_name：processRequestFastPath"})

    # 6. 精确提取：Bailout (去优化) 原因
    if any(v == "wrong map" for v in values_str):
        score_details.append({"item": "精确提取去优化核心原因", "score": 15, "max_score": 15, "passed": True, "reason": "成功从十六进制与噪音中提取了 bailout reason"})
        total_score += 15
    else:
        score_details.append({"item": "精确提取去优化核心原因", "score": 0, "max_score": 15, "passed": False, "reason": "未能精准匹配原因 'wrong map'，或是带入了额外干扰文本"})
        
    # 7. LLM 非结构化检测：由于 Prompt 允许 Agent 自由决定字段名，故调用 LLM 查验字段命名是否直观清晰
    keys_str = ", ".join(data.keys())
    prompt_text = "The user dynamically generated JSON keys to identify the following three variables for an automated script: 'source code file path', 'function symbol name', and 'deoptimization bailout reason'. Are these provided key names intuitively descriptive, reasonable and free of random gibberish? Return YES if they make sense, or NO if they are vague or meaningless."
    
    llm_result = llm_judge_content(prompt_text, keys_str)
    if llm_result:
        score_details.append({"item": "LLM评估数据字段命名语义", "score": 15, "max_score": 15, "passed": True, "reason": f"Agent 创建的键名 [{keys_str}] 被判定为具备清晰语义，有利于下游自动化修复脚本接入"})
        total_score += 15
    else:
        score_details.append({"item": "LLM评估数据字段命名语义", "score": 0, "max_score": 15, "passed": False, "reason": f"Agent 创建的键名 [{keys_str}] 缺乏合理描述性，下游脚本难以识别"})

    return score_details, total_score

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details, score = verify_workplace(workspace)
    
    result = {
        "total_score": score,
        "details": details
    }
    
    out_path = os.path.join(workspace, "workplace_score.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
