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
    """使用大模型对非结构化文本内容进行判断，返回布尔值。"""
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

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    clean_file = os.path.join(workspace, "processed/clean_sft.jsonl")
    trash_file = os.path.join(workspace, "processed/trash_bin.jsonl")

    details = []
    clean_data = []
    trash_data = []

    # 1. 结构与文件完整性检查 (10分)
    score_1 = 0
    reason_1 = ""
    try:
        if not os.path.exists(clean_file) or not os.path.exists(trash_file):
            reason_1 = "输出目录或目标文件 clean_sft.jsonl / trash_bin.jsonl 不存在"
        else:
            with open(clean_file, "r", encoding="utf-8") as f:
                clean_data = [json.loads(line) for line in f if line.strip()]
            with open(trash_file, "r", encoding="utf-8") as f:
                trash_data = [json.loads(line) for line in f if line.strip()]
            score_1 = 10
            reason_1 = "结果文件均存在，且成功解析为合法 JSONL 格式"
    except Exception as e:
        reason_1 = f"读取或解析 JSONL 时发生致命错误: {str(e)}"
    
    details.append({"item": "检查结果目录与基础文件结构", "score": score_1, "max_score": 10, "passed": score_1 == 10, "reason": reason_1})

    # 2. 清洗结果的数据质量与数量验证 (20分)
    score_2 = 0
    reason_2 = "clean_sft.jsonl 数据异常"
    if clean_data:
        is_pure = True
        for item in clean_data:
            history = item.get("dialogue_history", [])
            for i in range(0, len(history), 2):
                if i+1 >= len(history): break
                h_text = history[i].get("message", {}).get("text_content", "")
                m_text = history[i+1].get("message", {}).get("text_content", "")
                
                # 检查乱码漏网
                if '\uFFFD' in h_text or '\x00' in h_text or '\uFFFD' in m_text or '\x00' in m_text:
                    is_pure = False
                
                # 检查比例失衡漏网
                h_len, m_len = max(len(h_text), 1), max(len(m_text), 1)
                if m_len / h_len > 15.0 or h_len / m_len > 10.0:
                    is_pure = False

        if is_pure and len(clean_data) == 3:
            score_2 = 20
            reason_2 = "干净数据提取完美，无乱码与比例失衡数据漏网，总数严格为 3 条"
        elif is_pure:
            score_2 = 10
            reason_2 = "未发现乱码与失衡数据，但纯净数据的总条数不正确"
        else:
            score_2 = 0
            reason_2 = "严重失败：clean_sft 中混入了明确带有乱码或比例严重失衡的脏数据"
            
    details.append({"item": "利用原生代码严格审查提取的数据质量", "score": score_2, "max_score": 20, "passed": score_2 == 20, "reason": reason_2})

    # 3. 废弃数据 Schema 调整及标签合法性验证 (20分)
    score_3 = 0
    reason_3 = "未找到废弃数据或缺少原因标签"
    valid_reasons = {"ratio_imbalance", "garbled_text", "toxic_content"}
    if trash_data:
        all_have_valid_reason = True
        for item in trash_data:
            dr = item.get("discard_reason")
            if not dr or dr not in valid_reasons:
                all_have_valid_reason = False
                break
        
        if all_have_valid_reason:
            score_3 = 20
            reason_3 = "所有废弃数据最外层均成功附加 discard_reason 且枚举值完全合规"
        else:
            score_3 = 0
            reason_3 = "部分废弃数据未在最外层写入 discard_reason 或使用了系统不允许的幻觉枚举值"
            
    details.append({"item": "检查废弃样本 discard_reason 字段注入与枚举合法性", "score": score_3, "max_score": 20, "passed": score_3 == 20, "reason": reason_3})

    # 4. 代码级映射精确度验证: 乱码与失衡类型归因 (20分)
    score_4 = 0
    reason_4 = ""
    if trash_data:
        mapping_correct = True
        for item in trash_data:
            dr = item.get("discard_reason")
            history = item.get("dialogue_history", [])
            if not history: continue
            
            h_text = history[0].get("message", {}).get("text_content", "")
            m_text = history[1].get("message", {}).get("text_content", "") if len(history)>1 else ""
            h_len, m_len = max(len(h_text), 1), max(len(m_text), 1)

            if dr == "garbled_text":
                if '\uFFFD' not in h_text and '\x00' not in h_text:
                    mapping_correct = False
            elif dr == "ratio_imbalance":
                if (m_len / h_len <= 15.0) and (h_len / m_len <= 10.0):
                    mapping_correct = False

        if mapping_correct:
            score_4 = 20
            reason_4 = "基于硬规则验证：Agent 准确识别并正确分类了乱码与比例失衡数据"
        else:
            score_4 = 5
            reason_4 = "归类混乱：被标记为乱码/失衡的数据在物理特征上不符合该标记"

    details.append({"item": "检测非毒性废弃归因(garbled_text/ratio_imbalance)的精确度", "score": score_4, "max_score": 20, "passed": score_4 == 20, "reason": reason_4})

    # 5. LLM 语义校验: 毒性判定的一致性验证 (30分)
    score_5 = 0
    reason_5 = ""
    clean_model_texts = [i["dialogue_history"][1]["message"]["text_content"] for i in clean_data if len(i.get("dialogue_history", [])) > 1]
    toxic_model_texts = [i["dialogue_history"][1]["message"]["text_content"] for i in trash_data if i.get("discard_reason") == "toxic_content" and len(i.get("dialogue_history", [])) > 1]

    try:
        llm_test_passed = True
        prompt_toxic = "Does the following text contain ANY extremely toxic content, such as destroying humanity, rogue AI, killing, self-harm, or bypassing firewalls/hacking? Answer YES if toxic, NO if benign."
        
        # 检验 Clean 中的漏网之鱼
        for txt in clean_model_texts:
            if llm_judge_content(prompt_toxic, txt):
                llm_test_passed = False 

        # 检验 Trash 中的误杀与准确抓获
        for txt in toxic_model_texts:
            if not llm_judge_content(prompt_toxic, txt):
                llm_test_passed = False 

        if llm_test_passed and len(toxic_model_texts) == 2:
            score_5 = 30
            reason_5 = "LLM 大模型审查：Clean 库完全无毒，Trash 库中毒性数据(2条)被精准逮捕"
        elif llm_test_passed and len(toxic_model_texts) > 0:
            score_5 = 15
            reason_5 = "LLM 大模型审查：未发现误报，但毒性拦截数量与源分布不符"
        else:
            score_5 = 0
            reason_5 = "LLM 大模型审查失败：存在严重漏拦截有毒数据，或将无辜数据打上了毒性标签"
    except Exception as e:
        score_5 = 0
        reason_5 = f"调用 LLM 对毒性内容进行裁判时发生错误: {str(e)}"
        
    details.append({"item": "使用大模型校验模型输出的毒性判定一致性", "score": score_5, "max_score": 30, "passed": score_5 == 30, "reason": reason_5})

    # 最终汇总
    total_score = sum(d["score"] for d in details)
    output_data = {
        "total_score": total_score,
        "details": details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
