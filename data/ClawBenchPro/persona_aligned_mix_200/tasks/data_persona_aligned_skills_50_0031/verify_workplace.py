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
    """用于处理非结构化破坏情况的备用大模型兜底探针"""
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

def verify_workplace():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0
    
    blacklist_path = os.path.join(workspace, "config", "blacklist.json")
    
    # Target IPS derived from deterministic environment builder
    target_ips = {"120.44.55.66", "45.33.22.11", "10.0.5.200"}
    
    if os.path.exists(blacklist_path):
        score_details.append({"item": "检查目标文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件 config/blacklist.json 已生成"})
        total_score += 10
        
        try:
            with open(blacklist_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 严格代码解析结构化数据
            data = json.loads(content)
            score_details.append({"item": "检查文件是否符合标准 JSON Schema", "score": 10, "max_score": 10, "passed": True, "reason": "解析器成功加载 JSON"})
            total_score += 10
            
            if isinstance(data, list) and all(isinstance(x, str) for x in data):
                score_details.append({"item": "检查数据结构是否为纯粹的字符串数组", "score": 10, "max_score": 10, "passed": True, "reason": "文件顶层确认为包含字符串的 List，未夹带私货字段"})
                total_score += 10
                
                # 去重检查
                extracted_ips = set(data)
                if len(data) == len(extracted_ips) and len(data) > 0:
                    score_details.append({"item": "检查数据是否去重", "score": 10, "max_score": 10, "passed": True, "reason": "源 IP 无冗余和重复"})
                    total_score += 10
                else:
                    score_details.append({"item": "检查数据是否去重", "score": 0, "max_score": 10, "passed": False, "reason": "数组包含重复元素或为空"})
                
                # 严密准确度计算（满分 60分）
                correct_count = len(extracted_ips.intersection(target_ips))
                wrong_count = len(extracted_ips - target_ips)
                
                accuracy_score = correct_count * 20  # 找到一个给 20 分
                accuracy_score -= wrong_count * 15   # 抓错一个幻觉扣 15 分
                
                if extracted_ips == target_ips:
                    accuracy_score = 60
                else:
                    accuracy_score = max(0, min(accuracy_score, 59))
                
                if accuracy_score == 60:
                    score_details.append({"item": "源 IP 提取准确度评估", "score": 60, "max_score": 60, "passed": True, "reason": "极其精准！捕获了全部 3 个 MALFORMED 源 IP，且没有任何干扰项或幻觉"})
                elif accuracy_score > 0:
                    score_details.append({"item": "源 IP 提取准确度评估", "score": accuracy_score, "max_score": 60, "passed": False, "reason": f"提取了部分准确数据（{correct_count} 命中），但遗漏或掺杂了非攻击 IP 幻觉（{wrong_count} 错误）"})
                else:
                    score_details.append({"item": "源 IP 提取准确度评估", "score": 0, "max_score": 60, "passed": False, "reason": "未能提取有效恶意 IP，或幻觉伪造内容过多导致准确度清零"})
                
                total_score += accuracy_score

            else:
                score_details.append({"item": "检查数据结构是否为纯粹的字符串数组", "score": 0, "max_score": 10, "passed": False, "reason": "JSON 内部结构并非单纯的字符串数组"})
                
                # LLM 非结构化数据挽回机制
                prompt = "Does the following text contain ALL three of these specific IP addresses: '120.44.55.66', '45.33.22.11', '10.0.5.200'?"
                if llm_judge_content(prompt, content):
                    score_details.append({"item": "LLM 语义兜底提取 (容错机制)", "score": 30, "max_score": 70, "passed": False, "reason": "Agent 输出了非合规的 JSON 结构被代码解析器拦截，但 LLM 判定其内部包含了全部目标恶意 IP，发放部分容错辛苦分"})
                    total_score += 30
                else:
                    score_details.append({"item": "LLM 语义兜底提取 (容错机制)", "score": 0, "max_score": 70, "passed": False, "reason": "格式错误，且未能正确分析出全部的恶意源 IP"})

        except json.JSONDecodeError:
            score_details.append({"item": "检查文件是否符合标准 JSON Schema", "score": 0, "max_score": 10, "passed": False, "reason": "原生解析失败，文件可能包含解释性前缀、Markdown 块或其他非 JSON 格式废话"})
            score_details.append({"item": "检查数据结构是否为纯粹的字符串数组", "score": 0, "max_score": 10, "passed": False, "reason": "前置条件失败"})
            
            # LLM 非结构化数据挽回机制
            with open(blacklist_path, 'r', encoding='utf-8') as f:
                content = f.read()
            prompt = "Does the following text contain ALL three of these specific IP addresses: '120.44.55.66', '45.33.22.11', '10.0.5.200'?"
            if llm_judge_content(prompt, content):
                score_details.append({"item": "LLM 语义兜底提取 (容错机制)", "score": 30, "max_score": 70, "passed": False, "reason": "文件彻底损坏，但大模型判定其中散落了所有的目标源 IP，发放部分容错辛苦分"})
                total_score += 30
            else:
                score_details.append({"item": "LLM 语义兜底提取 (容错机制)", "score": 0, "max_score": 70, "passed": False, "reason": "文件彻底损坏，且错失了目标恶意源 IP"})

    else:
        score_details.append({"item": "检查目标文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": f"关键交付物 {blacklist_path} 缺失"})
        score_details.append({"item": "结构与精准度验证", "score": 0, "max_score": 90, "passed": False, "reason": "基础文件丢失，取消剩余考核链条"})

    # 结果强制写回
    result = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    verify_workplace()
