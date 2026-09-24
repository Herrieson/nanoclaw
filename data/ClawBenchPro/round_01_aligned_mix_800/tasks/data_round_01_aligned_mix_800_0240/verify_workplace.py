import os
import sys
import json
import httpx
from openai import OpenAI

# 配置环境
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
    """统一的非结构化语义验证接口"""
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a strict data validation assistant. Answer ONLY with 'YES' or 'NO'."},
                {"role": "user", "content": f"{prompt_text}\n\n[File Content]:\n{file_content}"}
            ],
            temperature=0
        )
        result = response.choices[0].message.content.strip().lower()
        return "yes" in result
    except Exception as e:
        print(f"LLM API Error: {e}")
        return False

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    # 1. 垃圾文件清理检查 (20分)
    # 要求：lunch_orders.txt 和 trash_receipts.log 必须被彻底删除
    deleted_files = ["messy_desk/lunch_orders.txt", "messy_desk/trash_receipts.log"]
    deletion_success = True
    for f_path in deleted_files:
        full_path = os.path.join(workspace, f_path)
        if os.path.exists(full_path):
            deletion_success = False
            break
    
    score = 20 if deletion_success else 0
    score_details.append({
        "item": "清理垃圾文件",
        "score": score,
        "max_score": 20,
        "passed": deletion_success,
        "reason": "成功删除指定的垃圾文件" if deletion_success else "未删除或未完全删除垃圾文件"
    })
    total_score += score

    # 2. 目标文件存在性与格式检查 (10分)
    target_path = os.path.join(workspace, "clean_desk/Urgent_Repairs_Brief.md")
    exists = os.path.exists(target_path)
    score = 10 if exists else 0
    score_details.append({
        "item": "生成紧急简报文件",
        "score": score,
        "max_score": 10,
        "passed": exists,
        "reason": "文件 clean_desk/Urgent_Repairs_Brief.md 已生成" if exists else "未找到目标简报文件"
    })
    total_score += score

    # 3. 数据覆盖度与提取准确性 (40分) - 使用硬核解析
    # 预期紧急项目：12B(broken lock), Lobby(Leak), Note B(plumbing issue), Note C(small leak)
    # 预期非紧急：10A(lightbulb), Note A(kitchen)
    if exists:
        with open(target_path, "r", encoding="utf-8") as f:
            content = f.read().lower()
        
        # 关键词命中测试（模拟 OCR 与分类后的结果整合）
        expected_keywords = ["12b", "lobby", "note b", "note c", "leak", "broken"]
        found_keywords = [k for k in expected_keywords if k in content]
        
        # 梯度计分
        keyword_score = int((len(found_keywords) / len(expected_keywords)) * 40)
        
        # 排除项检查（如果误报了非紧急项，扣分）
        negative_keywords = ["lightbulb", "loved the kitchen"]
        penalty = 0
        for nk in negative_keywords:
            if nk in content:
                penalty += 10
        
        final_extraction_score = max(0, keyword_score - penalty)
        score_details.append({
            "item": "紧急事件提取覆盖度与准确性",
            "score": final_extraction_score,
            "max_score": 40,
            "passed": final_extraction_score > 25,
            "reason": f"匹配到关键词 {len(found_keywords)}/{len(expected_keywords)}, 扣除误报分 {penalty}"
        })
        total_score += final_extraction_score

        # 4. LLM 语义质量检查 (30分)
        # 检查是否以物业经理偏好的“简报”格式书写，且语气专业
        prompt = "Is this document a professional 'Morning Emergency Brief' that summarizes ONLY urgent property maintenance issues? It should look like a formal report and NOT include irrelevant junk like lunch orders."
        llm_passed = llm_judge_content(prompt, content)
        score = 30 if llm_passed else 0
        score_details.append({
            "item": "LLM 简报专业度与合规性评价",
            "score": score,
            "max_score": 30,
            "passed": llm_passed,
            "reason": "大模型判定简报格式与专业度合格" if llm_passed else "大模型判定内容不符合简报要求或包含无关信息"
        })
        total_score += score
    else:
        score_details.append({"item": "内容深度检测", "score": 0, "max_score": 70, "passed": False, "reason": "由于文件缺失，无法进行内容分析"})

    # 输出结果
    output = {
        "total_score": int(total_score),
        "details": score_details
    }
    
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
