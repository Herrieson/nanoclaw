import os
import sys
import json
import httpx
from openai import OpenAI

# 强制约定的环境变量
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
    """LLM 语义验证探针"""
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
    deliverables_dir = os.path.join(workspace, "deliverables")
    vip_alerts_path = os.path.join(deliverables_dir, "vip_alerts.json")
    junk_count_path = os.path.join(deliverables_dir, "junk_count.txt")

    total_score = 0
    details = []

    # 1. 验证输出目录 (10分)
    if os.path.isdir(deliverables_dir):
        total_score += 10
        details.append({"item": "检查 deliverables 目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录存在"})
    else:
        details.append({"item": "检查 deliverables 目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "目录不存在"})

    # 2. 验证废品统计结果 (30分)
    if os.path.exists(junk_count_path):
        try:
            with open(junk_count_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
            
            # 精确匹配数值 4
            if content == "4":
                total_score += 30
                details.append({"item": "检查 junk_count.txt 废品数量", "score": 30, "max_score": 30, "passed": True, "reason": "成功提取所有无主物品并正确统计为4"})
            elif "4" in content:
                total_score += 15
                details.append({"item": "检查 junk_count.txt 废品数量", "score": 15, "max_score": 30, "passed": False, "reason": "包含正确数字，但含有冗余字符"})
            else:
                details.append({"item": "检查 junk_count.txt 废品数量", "score": 0, "max_score": 30, "passed": False, "reason": f"统计错误，发现内容为: {content}"})
        except Exception as e:
            details.append({"item": "检查 junk_count.txt 废品数量", "score": 0, "max_score": 30, "passed": False, "reason": f"读取失败: {e}"})
    else:
        details.append({"item": "检查 junk_count.txt 废品数量", "score": 0, "max_score": 30, "passed": False, "reason": "文件不存在"})

    # 3. 验证 VIP 告警数据结构与确定性内容 (40分)
    if os.path.exists(vip_alerts_path):
        try:
            with open(vip_alerts_path, "r", encoding="utf-8") as f:
                vip_data = json.load(f)
            
            dumped_str = json.dumps(vip_data).lower()
            
            score_vip = 0
            reason_vip = []
            
            # 检查关键人物与物品
            if "marcus johnson" in dumped_str and "jacket" in dumped_str:
                score_vip += 10
                reason_vip.append("包含 Marcus")
            if "sarah connor" in dumped_str and "watch" in dumped_str:
                score_vip += 10
                reason_vip.append("包含 Sarah")
            if "chloe bennett" in dumped_str and ("vr" in dumped_str or "headset" in dumped_str):
                score_vip += 10
                reason_vip.append("包含 Chloe")
                
            # 反向检查幻觉与非VIP人员 (极其重要)
            if "david smith" not in dumped_str:
                score_vip += 10
                reason_vip.append("已排除非VIP David")
            else:
                reason_vip.append("未排除非VIP David (扣10分)")
                
            total_score += score_vip
            details.append({"item": "检查 vip_alerts.json 数据解析与过滤", "score": score_vip, "max_score": 40, "passed": score_vip == 40, "reason": ", ".join(reason_vip)})
            
        except json.JSONDecodeError:
            details.append({"item": "检查 vip_alerts.json 数据解析与过滤", "score": 0, "max_score": 40, "passed": False, "reason": "JSON 解析失败，格式非法"})
        except Exception as e:
            details.append({"item": "检查 vip_alerts.json 数据解析与过滤", "score": 0, "max_score": 40, "passed": False, "reason": f"发生错误: {e}"})
    else:
         details.append({"item": "检查 vip_alerts.json 数据解析与过滤", "score": 0, "max_score": 40, "passed": False, "reason": "文件不存在"})

    # 4. LLM 语义检测：确保 JSON 无剧透或多余的幻觉字段 (20分)
    if os.path.exists(vip_alerts_path):
        try:
            with open(vip_alerts_path, "r", encoding="utf-8") as f:
                file_content = f.read()
            prompt = (
                "Review the following JSON content. "
                "Does it ONLY contain clean, structured data representing lost items and VIP members, "
                "WITHOUT any conversational filler, hallucinated internal system logs, or commentary from the janitor? "
                "It should look like a professional data extract."
            )
            is_clean = llm_judge_content(prompt, file_content)
            if is_clean:
                total_score += 20
                details.append({"item": "LLM验证 vip_alerts.json 数据纯净度", "score": 20, "max_score": 20, "passed": True, "reason": "数据结构纯净，无幻觉与冗余对话"})
            else:
                details.append({"item": "LLM验证 vip_alerts.json 数据纯净度", "score": 0, "max_score": 20, "passed": False, "reason": "包含大模型生成的冗余文本或幻觉字段"})
        except Exception as e:
            details.append({"item": "LLM验证 vip_alerts.json 数据纯净度", "score": 0, "max_score": 20, "passed": False, "reason": f"LLM 调用失败: {e}"})
    else:
        details.append({"item": "LLM验证 vip_alerts.json 数据纯净度", "score": 0, "max_score": 20, "passed": False, "reason": "文件不存在"})

    # 输出评分结果
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    verify()
