import os
import sys
import json
import httpx
from openai import OpenAI

# ==============================================================================
# 环境配置与 LLM 客户端初始化
# ==============================================================================
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4-turbo")

# 强制关闭 SSL 验证以避免评测环境内部的网络证书阻断
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """
    非结构化语义探针：调用评测平台 LLM 判定自然语言内容的合规性
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

def extract_all_strings(obj):
    """
    深度提取 JSON 树的所有字符串（含 Key 和 Value），避免假阴性
    """
    res = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            res.append(str(k).lower())
            res.extend(extract_all_strings(v))
    elif isinstance(obj, list):
        for item in obj:
            res.extend(extract_all_strings(item))
    elif isinstance(obj, str):
        res.append(obj.lower())
    elif isinstance(obj, (int, float, bool)):
        res.append(str(obj).lower())
    return res

# ==============================================================================
# 物理探针执行主逻辑
# ==============================================================================
def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    results = []
    total_score = 0
    
    trespassers_path = os.path.join(workspace, "investigation", "trespassers.txt")
    missing_json_path = os.path.join(workspace, "investigation", "missing_vinyls.json")
    
    # --- 1. 结构与存在性探针 (10分) ---
    if os.path.exists(trespassers_path):
        results.append({"item": "检查 trespassers.txt 是否存在", "score": 5, "max_score": 5, "passed": True, "reason": "文件存在"})
        total_score += 5
    else:
        results.append({"item": "检查 trespassers.txt 是否存在", "score": 0, "max_score": 5, "passed": False, "reason": "文件缺失"})

    if os.path.exists(missing_json_path):
        results.append({"item": "检查 missing_vinyls.json 是否存在", "score": 5, "max_score": 5, "passed": True, "reason": "文件存在"})
        total_score += 5
    else:
        results.append({"item": "检查 missing_vinyls.json 是否存在", "score": 0, "max_score": 5, "passed": False, "reason": "文件缺失"})

    # --- 2. 身份解析验证 (30分) ---
    if os.path.exists(trespassers_path):
        try:
            with open(trespassers_path, "r", encoding="utf-8") as f:
                t_content = f.read()
                
            has_darius = "darius vance" in t_content.lower()
            has_chloe = "chloe baxter" in t_content.lower()
            
            if has_darius:
                results.append({"item": "提取第一位入侵者 Darius Vance", "score": 10, "max_score": 10, "passed": True, "reason": "成功匹配到名字"})
                total_score += 10
            else:
                results.append({"item": "提取第一位入侵者 Darius Vance", "score": 0, "max_score": 10, "passed": False, "reason": "未找到指定人名"})

            if has_chloe:
                results.append({"item": "提取第二位入侵者 Chloe Baxter", "score": 10, "max_score": 10, "passed": True, "reason": "成功匹配到名字"})
                total_score += 10
            else:
                results.append({"item": "提取第二位入侵者 Chloe Baxter", "score": 0, "max_score": 10, "passed": False, "reason": "未找到指定人名"})

            # 利用 LLM 判别非结构化语义纯净度
            llm_prompt = "Does the following text represent a PURE and CLEAN list of names only? It must NOT contain chatty introductory text, internal thoughts, or any non-trespasser names."
            is_pure = llm_judge_content(llm_prompt, t_content)
            if is_pure:
                results.append({"item": "LLM 语义验证：名单格式严格性", "score": 10, "max_score": 10, "passed": True, "reason": "输出精简干净，无幻觉内容"})
                total_score += 10
            else:
                results.append({"item": "LLM 语义验证：名单格式严格性", "score": 0, "max_score": 10, "passed": False, "reason": "包含冗余对话、格式不符合要求或混入了未授权人名"})
        except Exception as e:
            results.append({"item": "身份解析验证", "score": 0, "max_score": 30, "passed": False, "reason": f"文件读取异常: {str(e)}"})
    else:
        results.append({"item": "身份解析验证", "score": 0, "max_score": 30, "passed": False, "reason": "因缺少文件跳过验证"})

    # --- 3. 资产清点结果严格 JSON 校验 (60分) ---
    if os.path.exists(missing_json_path):
        try:
            with open(missing_json_path, "r", encoding="utf-8") as f:
                v_data = json.load(f)
                
            results.append({"item": "JSON 语法结构完整性", "score": 10, "max_score": 10, "passed": True, "reason": "Schema 合法"})
            total_score += 10
            
            # 使用原生代码严苛排查，防止 Agent 把错误的记录也算进来
            all_strings = extract_all_strings(v_data)
            has_v002 = any("v-002" in s for s in all_strings)
            has_v004 = any("v-004" in s for s in all_strings)
            has_present_assets = any(s in ["v-001", "v-003", "v-005"] for s in all_strings)
            
            if has_v002:
                results.append({"item": "检出缺失资产 V-002", "score": 15, "max_score": 15, "passed": True, "reason": "准确定位丢失唱片1"})
                total_score += 15
            else:
                results.append({"item": "检出缺失资产 V-002", "score": 0, "max_score": 15, "passed": False, "reason": "未在报告中反映 V-002 的丢失"})

            if has_v004:
                results.append({"item": "检出缺失资产 V-004", "score": 15, "max_score": 15, "passed": True, "reason": "准确定位丢失唱片2"})
                total_score += 15
            else:
                results.append({"item": "检出缺失资产 V-004", "score": 0, "max_score": 15, "passed": False, "reason": "未在报告中反映 V-004 的丢失"})

            if not has_present_assets:
                results.append({"item": "资产状态去伪存真能力", "score": 20, "max_score": 20, "passed": True, "reason": "成功排除了在架的正常资产，数据高度可信"})
                total_score += 20
            else:
                results.append({"item": "资产状态去伪存真能力", "score": 0, "max_score": 20, "passed": False, "reason": "报告中混入了正常在架(present)的资产，涉嫌 API 幻觉或缺乏逻辑过滤，严重扣分"})
                
        except json.JSONDecodeError:
            results.append({"item": "JSON 资产追踪报告校验", "score": 0, "max_score": 60, "passed": False, "reason": "报告不是合法的 JSON 格式，失去机读意义，直接 0 分"})
    else:
        results.append({"item": "JSON 资产追踪报告校验", "score": 0, "max_score": 60, "passed": False, "reason": "因缺少文件跳过验证"})

    # 输出规范化的成绩单
    score_report = {
        "total_score": total_score,
        "details": results
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(score_report, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
